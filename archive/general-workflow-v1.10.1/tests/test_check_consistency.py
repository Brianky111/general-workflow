"""Exercise the consistency checker against copies of the workflow tree.

The checker is the only automatic gate on documentation edits, so a checker
that quietly stops checking makes every later change look reviewed. Each case
copies the real tree, changes exactly one thing, and asserts the error that
change is supposed to produce.

The last class works differently: it asserts the checker's own constants. Those
are a design decision stored as four numbers, and an edit to a number is the one
change no copied-tree case can see.
"""

from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_consistency.py"
# The cases below run the checker as a subprocess, the way CI and a human do.
# One case asserts on a pattern instead, where going through a document cannot
# distinguish the two behaviours; that case needs the module itself.
sys.path.insert(0, str(SCRIPT.parent))
import check_consistency  # noqa: E402
REFERENCES = sorted(path.name for path in (REPO / "references").glob("*.md"))
ARCHIVE = "archive/general-workflow-v0.12.0"
# The checker keys its budgets by bare filename and the copied-tree cases address
# files by path, so the router is spelled once and both forms derive from it.
ROUTER_NAME = "00-progress-router.md"
ROUTER = f"references/{ROUTER_NAME}"
RETRO = "references/11-retrospective-evolution.md"
LEAN = "references/00-lean-path.md"
SLICE = "references/07-vertical-slice.md"
CONSTRAINTS = "references/04-constraints-quality-risks.md"
STATE = "references/99-state-and-handoff.md"
# The leaf used by the reachability and budget cases: no policy anchor spells
# its filename, so cutting its inbound links leaves one error and not five.
LEAF = "11-retrospective-evolution.md"
POINTER = "复盘阶段文档"
LF = "\n"
CRLF = "\r\n"


class CheckConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="check-consistency-test-")
        self.addCleanup(self.temp.cleanup)
        # A space in the path catches a checker that pastes paths into strings.
        self.root = Path(self.temp.name) / "workflow copy"
        self.write("SKILL.md", (REPO / "SKILL.md").read_text(encoding="utf-8"))
        for name in REFERENCES:
            self.write(f"references/{name}",
                       (REPO / "references" / name).read_text(encoding="utf-8"))
        # The references name this script by path, so the copy carries the real
        # one; tests/ and archive/ are only checked for existence.
        self.write("scripts/workflow_status.py",
                   (REPO / "scripts" / "workflow_status.py").read_text(encoding="utf-8"))
        self.write("tests/test_workflow_status.py", "")
        self.write("archive/ARCHIVE-NOTE.md", "placeholder\n")
        for name in ("SKILL.md", "README.md", "references/.keep", "scripts/.keep"):
            self.write(f"{ARCHIVE}/{name}", "")

    def write(self, name, text, newline=LF):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        # newline="" writes the bytes as given, so a case can choose its own
        # line endings instead of inheriting the platform's.
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(text.replace(LF, newline))

    def read(self, name):
        return (self.root / name).read_text(encoding="utf-8")

    def replace(self, name, old, new):
        text = self.read(name)
        self.assertEqual(text.count(old), 1, f"{old!r} is not unique in {name}")
        self.write(name, text.replace(old, new))

    def set_section(self, name, heading, body):
        """Keep a heading and replace everything under it, up to the next peer."""

        lines = self.read(name).split(LF)
        start = lines.index(heading)
        depth = len(heading.split(" ")[0])
        end = next((i for i in range(start + 1, len(lines))
                    if re.match(rf"^#{{1,{depth}}}\s", lines[i])), len(lines))
        self.write(name, LF.join(lines[:start + 1] + ["", body, ""] + lines[end:]))

    def run_check(self, *args):
        run = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), *args],
            cwd=self.temp.name, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        self.assertIn(run.returncode, (0, 1), run.stdout + run.stderr)
        return run.returncode, run.stdout

    def errors(self):
        code, out = self.run_check("--root", str(self.root))
        prefix = "ERROR "
        found = [line[len(prefix):] for line in out.splitlines() if line.startswith(prefix)]
        self.assertEqual(code, 1, out)
        return found

    def assert_error(self, fragment):
        found = self.errors()
        self.assertTrue(any(fragment in error for error in found), found)
        return found

    def assert_only_error(self, fragment):
        found = self.assert_error(fragment)
        self.assertEqual(len(found), 1, found)
        return found[0]

    def test_a_clean_copy_passes(self):
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn(f"{len(REFERENCES)} active reference files, 0 error(s)", out)

    def test_the_default_root_is_still_the_shipped_tree(self):
        # The documented call has no arguments and does not depend on cwd; here
        # it runs from the temp directory and must still check the skill.
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn(f"{len(REFERENCES)} active reference files, 0 error(s)", out)

    def test_a_file_missing_from_the_reference_map_is_reported(self):
        kept = [line for line in self.read("SKILL.md").split(LF)
                if not line.startswith(f"- `{LEAF}`")]
        self.write("SKILL.md", LF.join(kept))
        self.assert_only_error(f"references/{LEAF} is not listed in the Reference Map")

    def test_the_reference_map_cannot_list_a_file_that_is_gone(self):
        row = f"- `{LEAF}`"
        self.replace("SKILL.md", row, "- `12-nonexistent-stage.md`：占位。\n" + row)
        found = self.assert_error("Reference Map lists missing file: 12-nonexistent-stage.md")
        self.assertTrue(
            any("mentions missing reference: 12-nonexistent-stage.md" in e for e in found),
            found)

    def test_a_reference_nothing_links_to_is_unreachable(self):
        # Reachability starts before the map, so the map row alone is not a
        # link; cut every real mention and only that file drops out.
        head, sep, tail = self.read("SKILL.md").partition("## Reference Map")
        self.write("SKILL.md", head.replace(LEAF, POINTER) + sep + tail)
        for name in REFERENCES:
            if name != LEAF:
                self.write(f"references/{name}",
                           self.read(f"references/{name}").replace(LEAF, POINTER))
        self.assert_only_error(f"references/{LEAF} is unreachable from active router/rules")

    def test_an_emptied_section_fails_even_though_the_heading_remains(self):
        # This is the edit the anchor check exists for: the LEAN exemption list
        # was replaced by a pointer here, and a plain substring check would
        # still pass on a heading with nothing under it.
        self.set_section(ROUTER, "## 路径深度与暂停", "")
        error = self.assert_only_error("section '路径深度与暂停' has 0 characters of body")
        self.assertIn("the heading is not the policy", error)

    def test_a_gate_section_needs_more_than_one_sentence(self):
        self.set_section(ROUTER, "## 全局门禁", "每个阶段都用同一组问题收口：目的、入口、产出、退出、游标，逐条回答。")
        error = self.assert_only_error("under the 60")
        # Long enough for an ordinary section, so it is the gate threshold that
        # rejected it, not the base one.
        self.assertGreaterEqual(int(re.search(r"has (\d+) characters", error)[1]), 30)

    def test_a_heading_inside_a_fence_is_not_a_section(self):
        self.replace(RETRO, "## 复盘门禁", "~~~markdown\n## 复盘门禁\n~~~")
        self.assert_only_error("missing policy anchor: ## 复盘门禁")

    def test_a_fenced_example_does_not_shadow_the_real_section(self):
        # A template block that shows a heading is documentation, not structure.
        # Read as structure, this trailing example would replace the gate's body
        # with the fence marker and the file would fail.
        self.write(RETRO, self.read(RETRO) + "\n~~~markdown\n## 复盘门禁\n~~~\n")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def pad_to(self, name, target):
        """Grow a file to just under `target` LF bytes, in many short lines.

        Short lines on purpose: the LF/CRLF gap is one byte per line, so the
        gap only moves a file across the budget if there are enough lines.
        """

        text = self.read(name)
        line = "对齐体积预算的填充行。" + LF
        while len(text.encode("utf-8")) + len(line.encode("utf-8")) <= target:
            text += line
        return text

    def test_a_crlf_checkout_of_the_whole_tree_passes(self):
        # git with core.autocrlf hands out exactly this tree, and this repo's
        # own working copy is already mixed. Everything the checker parses has
        # to survive it, not only the byte count: `startswith("---\n")` on the
        # frontmatter is the first thing that stops matching.
        for name in ["SKILL.md"] + [f"references/{ref}" for ref in REFERENCES]:
            self.write(name, self.read(name), newline=CRLF)
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_a_file_that_fits_as_lf_is_not_over_budget_as_crlf(self):
        # The one-directional failure, and the one that actually costs someone
        # an afternoon: the same document passes in a Linux checkout and is
        # rejected in a Windows one, for an edit nobody made. Remove the newline
        # normalization from read_text and this case turns red.
        self.write(RETRO, self.pad_to(RETRO, 12_950), newline=CRLF)
        on_disk = (self.root / RETRO).stat().st_size
        self.assertGreater(on_disk, 13_000, on_disk)
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_the_budget_counts_the_same_bytes_for_lf_and_crlf(self):
        # The printed number has to be the same for both checkouts, not merely
        # on the same side of the budget. That is what read_text's newline
        # normalization buys; delete it and the two counts diverge here.
        padded = self.read(RETRO) + LF + "撑破体积预算的填充行。\n" * 400
        measured = {}
        for newline in (LF, CRLF):
            with self.subTest(newline=repr(newline)):
                self.write(RETRO, padded, newline=newline)
                error = self.assert_only_error("over its 13000-byte budget")
                measured[newline] = (
                    (self.root / RETRO).stat().st_size,
                    int(re.search(r"is (\d+) bytes", error)[1]),
                )
        # The two files differ on disk by one byte per line; the budget must not,
        # or the same document passes on Linux and fails on a Windows checkout.
        self.assertNotEqual(measured[LF][0], measured[CRLF][0])
        self.assertEqual(measured[LF][1], measured[CRLF][1])

    def test_deleting_the_conditional_profile_load_is_caught(self):
        # The saving here is invisible to every other check: with this section
        # gone the router still routes, every other anchor still matches, and
        # the profile quietly becomes a fourth resident file again.
        self.set_section(ROUTER, "### 画像按需加载", "")
        self.assert_error("section '画像按需加载' has 0 characters of body")

    def test_making_the_profile_load_unconditional_is_caught(self):
        # The other half of the same regression, and the cheaper one to make by
        # accident: the section survives, but "load it when these three things
        # hold" turns back into "load it", and a tier the user already confirmed
        # gets recomputed every turn.
        self.replace(ROUTER, "以下情况才加载 00-project-profile.md",
                     "每轮开始都加载 00-project-profile.md")
        self.assert_only_error(
            "missing policy anchor: 以下情况才加载 00-project-profile.md")

    def test_dropping_the_high_risk_exception_to_the_skip_is_caught(self):
        # Without this line the skip is unsafe, not merely undocumented: a
        # HIGH-RISK project resumed at stage 8 skips the deepening row too, and
        # the stage documents no longer carry a replacement.
        self.replace(ROUTER, "只取表不重定档位", "按表补齐")
        self.assert_only_error("missing policy anchor: 只取表不重定档位")

    def test_a_deleted_status_script_is_caught(self):
        (self.root / "scripts/workflow_status.py").unlink()
        found = self.assert_error("missing scripts/workflow_status.py")
        self.assertTrue(
            any("does not exist: scripts/workflow_status.py" in e for e in found), found)

    def test_a_deleted_tests_directory_is_caught(self):
        shutil.rmtree(self.root / "tests")
        self.assert_only_error("missing tests/")

    def test_shuffled_lifecycle_stages_are_caught(self):
        ninth, tenth = "9. 测试、评审与集成", "10. 发布、监控、回滚与运行"
        swapped = (self.read("SKILL.md")
                   .replace(ninth, "<swap>").replace(tenth, ninth).replace("<swap>", tenth))
        self.write("SKILL.md", swapped)
        self.assert_only_error("SKILL.md lifecycle stages are out of order")

    def test_a_dropped_lifecycle_stage_is_caught(self):
        self.replace("SKILL.md", "11. 复盘、架构演化与下一条切片", "11. 复盘与演化")
        self.assert_only_error("missing lifecycle stage: 11. 复盘、架构演化与下一条切片")

    def test_an_unlisted_reference_file_is_rejected(self):
        self.write("references/12-extra-stage.md", "# Extra\n\n正文。\n")
        found = self.assert_error("unexpected active reference (add it to checker/map): "
                                  "references/12-extra-stage.md")
        self.assertTrue(
            any("12-extra-stage.md is not listed in the Reference Map" in e for e in found),
            found)

    def paste_into_router(self, text):
        """Put a copied rule at the top of the router section that once held one."""

        heading = "## 路径深度与暂停"
        self.replace(ROUTER, heading, f"{heading}\n\n{text}\n")

    def test_the_lean_exemption_list_cannot_be_copied_into_the_router(self):
        # The exact drift the single-authority rule exists for: a compressed
        # copy in the always-loaded router that also gives up the clean clone.
        # Whoever loads the router reads it as the rule and never opens
        # 00-lean-path.md, so the two documents disagree and nothing breaks.
        self.paste_into_router(
            "- LEAN 减免速查：05a 整个阶段跳过，除非鉴权是现在必须有；07 不要求部署到 staging；"
            "09 不要求合同测试；06 的干净 clone 验证可以省略。")
        found = self.assert_error("00-progress-router.md restates LEAN 减免清单")
        self.assertTrue(
            any("single authority for this rule is references/00-lean-path.md" in error
                for error in found), found)

    def test_the_high_risk_deepening_list_cannot_be_copied_into_the_router(self):
        self.paste_into_router(
            "- HIGH-RISK 加深速查：05 由非作者做一次独立架构评审；09 评审人与实现者分离。")
        found = self.assert_error("00-progress-router.md restates HIGH-RISK 加深清单")
        self.assertTrue(
            any("references/00-project-profile.md" in error for error in found), found)

    def test_the_claiming_rules_cannot_be_copied_back_into_the_state_file(self):
        # 99 is resident all session, so a copy there is what agents actually
        # read; the pointer sentence turning back into the rule is how the
        # migration out of 99 gets quietly undone.
        self.replace(STATE, "不替它背这一段。", "同一 owner 只能持有一条在途切片。")
        found = self.assert_error("99-state-and-handoff.md restates 切片认领与归还规则")
        self.assertTrue(
            any("references/07-vertical-slice.md" in error for error in found), found)

    def test_the_authority_file_may_repeat_its_own_wording(self):
        # The guard is about a second copy elsewhere, not about how often the
        # owning file states its own rule; a checker that cannot tell the two
        # apart gets disabled the first time it fires on the authority.
        self.write(LEAN, self.read(LEAN) + "\n再说一遍：09 不要求合同测试。\n")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_a_pointer_to_the_authority_is_not_a_copy(self):
        # Every other file is supposed to say this much; if the guard rejected
        # it, the only way to pass would be to say nothing about the rule.
        self.write(RETRO, self.read(RETRO) + "\nLEAN 的减免清单见 00-lean-path.md，这里不复制。\n")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_guarded_wording_must_stay_in_the_authority_file(self):
        # Reworded in the owner and nowhere updated, the phrase guards nothing
        # and copies of the new wording spread unchecked.
        self.replace(SLICE, "只能持有一条", "只能同时持有一条")
        self.assert_only_error(
            "07-vertical-slice.md no longer contains the 切片认领与归还规则 wording")

    def test_dropping_one_claiming_rule_is_caught(self):
        # The heading and two rules survive this edit, which is why the anchors
        # name individual rules instead of just the section.
        self.replace(SLICE, "**一次一条。**", "")
        self.assert_only_error("07-vertical-slice.md is missing policy anchor: 一次一条")

    def test_a_reworded_lean_exemption_list_is_caught_in_a_stage_document(self):
        # Not a paste: no phrase from 00-lean-path.md survives, so the
        # single-authority table has nothing to match and stays silent. What
        # gives the copy away is the shape a rewrite cannot drop — bare stage
        # numbers, each followed by what that stage gets to skip.
        self.write(CONSTRAINTS, self.read(CONSTRAINTS) + LF.join([
            "", "## LEAN 速查", "",
            "- 05 只写一页决策表，不必写完整 ADR。",
            "- 05a 整个阶段可以省，除非鉴权是现在必须有的。",
            "- 07 不必部署到 staging，本地真实入口跑通即可。",
            "- 09 可以省掉合同测试，单元加一条真实集成即可。",
            "",
        ]))
        found = self.assert_error(
            "04-constraints-quality-risks.md section 'LEAN 速查' "
            "reads as a per-stage tier policy")
        self.assertTrue(any("references/00-lean-path.md" in e for e in found), found)
        # If the phrase table had caught this edit, the shape check would not be
        # the thing this case is testing.
        self.assertFalse(any("restates" in e for e in found), found)

    def test_a_reworded_high_risk_deepening_list_is_caught_in_the_router(self):
        self.paste_into_router(
            "- HIGH-RISK 另加：04 的实验必须先跑完；05 另加一次非作者评审；"
            "09 还要评审人与实现者分开；10 额外做一次迁移演练。")
        found = self.assert_error(
            "00-progress-router.md section '路径深度与暂停' "
            "reads as a per-stage tier policy")
        self.assertTrue(
            any("references/00-project-profile.md" in e for e in found), found)
        self.assertFalse(any("restates" in e for e in found), found)

    def test_a_pointer_to_the_tier_policies_is_not_a_restatement(self):
        # Naming the stages and naming the owning files is the behaviour the
        # guard exists to leave room for; rejecting it would leave "say nothing
        # about the tiers" as the only way to pass.
        self.paste_into_router(
            "- 档位的减免和加深都不写在这里：LEAN 见 00-lean-path.md，"
            "HIGH-RISK 见 00-project-profile.md；进入 05a、07、09 之前回去查对应那一行。")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_a_reference_filename_is_not_a_stage_number(self):
        # A pointer is written as a filename, and every filename here opens with
        # the stage's two digits. Reading those as stage numbers would make the
        # sentence that sends the reader to the owning file the thing that
        # fails: the guard firing on exactly the edit it asks for.
        #
        # Asserted against the pattern rather than through a document, because
        # a document cannot tell the two apart — the filenames are long enough
        # that the verb falls outside the 24-character reach anyway, so an
        # end-to-end case would pass with the lookahead removed and prove
        # nothing about it.
        pattern = check_consistency.STAGE_NUMBER
        for name in REFERENCES:
            with self.subTest(name=name):
                self.assertEqual([m[0] for m in pattern.finditer(name)], [])
        self.assertEqual(
            [m[0] for m in pattern.finditer("05a 整段跳过；07 不必上 staging")],
            ["05a", "07"])

    def test_a_paragraph_naming_two_stages_is_not_a_policy_list(self):
        # One under the threshold on purpose. Ordinary prose does name a stage
        # and say what it drops; a guard that fires on two of those is noise,
        # and a noisy guard gets switched off before it ever catches a list.
        self.paste_into_router(
            "- 快路径下 05a 可以省，09 的合同测试也可以省；其余门禁照原样执行。")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_the_owning_file_may_still_enumerate_every_stage(self):
        # 00-lean-path.md is nothing but the shape this guard rejects. Firing on
        # the authority would mean the only way to keep the tree green is to
        # delete the rule from the one file allowed to hold it.
        self.write(LEAN, self.read(LEAN)
                   + "\n- 05 不必写完整 ADR；07 不必上 staging；09 可以省掉合同测试。\n")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def test_the_takeover_review_keeps_its_fourth_answer(self):
        # "不知道" is the answer that stops a reviewer from filing a guess as
        # confirmed. Drop that row and the entry still reads as a complete
        # procedure, which is why the anchor names the row and not the section.
        self.replace("references/00-brownfield-entry.md", "| 不知道 |", "| 存疑 |")
        self.assert_only_error("00-brownfield-entry.md is missing policy anchor: 不知道")

    def test_an_incomplete_archive_is_reported(self):
        (self.root / ARCHIVE / "README.md").unlink()
        self.assert_only_error(f"archive is incomplete: {Path(ARCHIVE) / 'README.md'}")

    def test_an_installed_copy_without_the_archive_is_not_incomplete(self):
        # The README's install step deletes archive/ on purpose, and the README
        # also says to point --root at the installed copy to confirm it. While
        # the five archive paths were demanded everywhere, the two could not
        # both hold: every documented install failed with five errors.
        shutil.rmtree(self.root / "archive")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("NOTE  archive/ is absent", out)
        self.assertIn(f"{len(REFERENCES)} active reference files, 0 error(s)", out)

    def test_routing_through_the_archive_is_still_caught_without_it(self):
        # The half of the archive check that matters on an install is the
        # routing one: a reference into archive/ is broken exactly where the
        # directory is gone, so skipping completeness must not skip this.
        shutil.rmtree(self.root / "archive")
        self.write(RETRO, self.read(RETRO) + f"\n旧流程见 {ARCHIVE}/references。\n")
        self.assert_only_error("active SKILL/references must not depend on archived workflow path")


# The values the checker is required to hold. Repeated here rather than imported
# so that an edit to the checker has to be made twice, in two files, with a
# reason; importing them would assert that a number equals itself.
PINNED_SIZE_BUDGETS = {"SKILL.md": 8_000, "00-progress-router.md": 9_500}
PINNED_REFERENCE_BUDGET = 13_000
PINNED_BUDGET_WARN = 0.90

WHY_THE_BUDGETS_HOLD = """
SKILL.md and 00-progress-router.md are read again at the start of every turn of
every session, in every project that uses this skill. Their bytes are paid over
and over; a reference is paid once, when its stage is entered. That is what the
two smaller numbers buy, and it is why raising one is not a local edit: it moves
cost onto sessions nobody has started yet.

Going over a budget means the content is in the wrong file. The two repairs are
delete the duplication, or push the detail down into the reference that owns it
and leave a pointer. Raising the number is not a third repair, it is the record
of the decision being erased -- both gates go green and no diff explains why the
entry path got bigger.

Deleting a name from SIZE_BUDGETS is the same edit wearing a different hat:
SKILL.md without its entry falls through to the 13000-byte reference budget and
gains 5000 bytes for nothing, which is why the whole table is compared here and
not just its values.

If a different number really is the design change you want, change it in the
checker and in this test together, and say in the commit what got cheaper.
"""

WHY_THE_WARN_LINE_HOLDS = """
0.90 is not a budget. It is how much notice arrives before one bites -- 950
bytes on the router, roughly a paragraph, which is about one edit's warning.

It is pinned for the budgets' reason, one step earlier. The tree already prints
five WARN lines and the router is down to its last few hundred bytes, so the
cheapest way to make that output look clean is not to touch 9500, which reads as
a budget change to a reviewer, but to nudge this to 0.97, which reads as tuning
and silences every warning at once. The notice is the whole value of the line.

Lowering it is not free either. At 0.5 every file in the tree warns, and a line
that always prints is a line nobody reads; the warning is then gone in practice
while still looking present.
"""


class BudgetContractTests(unittest.TestCase):
    """Pin the four numbers the size gate is made of.

    Every other convention in this tree is enforced by something: a gutted
    section fails the anchor check, a pasted rule fails the phrase table. "Over
    budget means delete duplication, never raise the number" had nothing behind
    it. SIZE_BUDGETS is read by one function and, until this class, by no test,
    so `9_500` -> `10_500` was a one-character edit that left the checker at 0
    errors and the suite all green -- and it is the edit anyone who wants to add
    a paragraph to the router will reach for first, because it is the only one
    that does not cost them anything.

    These cases exist to make that a decision instead of a reflex. They cannot
    stop the number from changing; nothing can. They make it change in two files
    at once, with the reason above printed at the moment of the change.
    """

    def run_budgets(self, texts):
        errors, warnings = [], []
        check_consistency.check_size_budgets(texts, errors, warnings)
        return errors, warnings

    def test_the_budget_numbers_may_not_be_raised_to_fit_new_content(self):
        self.assertEqual(
            check_consistency.SIZE_BUDGETS, PINNED_SIZE_BUDGETS, WHY_THE_BUDGETS_HOLD)
        self.assertEqual(
            check_consistency.REFERENCE_BUDGET, PINNED_REFERENCE_BUDGET,
            WHY_THE_BUDGETS_HOLD)

    def test_each_budget_is_the_number_actually_enforced_on_that_file(self):
        # A constant is worth pinning only while it is still the number applied
        # to that name. This walks the boundary from the outside: one byte under
        # the pinned budget passes, one byte over is rejected and the message
        # names the pinned number, so rewiring which file gets which budget
        # fails here even with every constant left alone.
        budgets = {**PINNED_SIZE_BUDGETS, LEAF: PINNED_REFERENCE_BUDGET}
        for name, budget in budgets.items():
            with self.subTest(name=name):
                errors, _ = self.run_budgets({name: "x" * budget})
                self.assertEqual(errors, [], WHY_THE_BUDGETS_HOLD)
                errors, _ = self.run_budgets({name: "x" * (budget + 1)})
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(
                    f"is {budget + 1} bytes, over its {budget}-byte budget",
                    errors[0], WHY_THE_BUDGETS_HOLD)

    def test_the_warning_arrives_with_a_paragraph_of_room_left(self):
        self.assertEqual(
            check_consistency.BUDGET_WARN, PINNED_BUDGET_WARN, WHY_THE_WARN_LINE_HOLDS)
        # And the same boundary from the outside, so deleting the warn branch or
        # folding it into the error branch fails here too.
        budget = PINNED_SIZE_BUDGETS[ROUTER_NAME]
        notice = round(budget * (1 - PINNED_BUDGET_WARN))
        self.assertEqual(notice, 950, notice)
        _, quiet = self.run_budgets({ROUTER_NAME: "x" * (budget - notice)})
        self.assertEqual(quiet, [], WHY_THE_WARN_LINE_HOLDS)
        _, loud = self.run_budgets({ROUTER_NAME: "x" * (budget - notice + 1)})
        self.assertEqual(len(loud), 1, loud)
        self.assertIn(f"({notice - 1} bytes left)", loud[0], WHY_THE_WARN_LINE_HOLDS)


if __name__ == "__main__":
    unittest.main()
