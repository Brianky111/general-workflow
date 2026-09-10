# Repository Guidelines

## Project Structure & Module Organization

This repository **is** the skill package. There is no separate skill folder to
build and no source manual to convert: `SKILL.md` at the root is the entry
point an agent loads, and everything beside it either ships with that entry
point or guards it.

```text
.
├── SKILL.md                            # resident entry: scope, principles, lifecycle, Reference Map
├── agents/openai.yaml                  # Codex entry metadata
├── references/                         # stage documents, loaded one at a time
│   ├── 00-progress-router.md           # resident: routing algorithm, stage table, global gates
│   ├── 00-project-profile.md           # profile, risk tier, HIGH-RISK deepening list
│   ├── 00-lean-path.md                 # LEAN one-page contract and the single reduction list
│   ├── 00-refactor-path.md             # refactor path: authorization, protection baseline, structure check, R-slice format
│   ├── 00-brownfield-entry.md          # takeover of an old repository: run it, survey it, derive requirements, review, baseline
│   ├── 01 … 11                         # one file per stage
│   └── 99-state-and-handoff.md         # state files, ledger, completion rules
├── scripts/
│   ├── check_consistency.py            # validates this repository
│   └── workflow_status.py              # ships with the skill, runs inside a user's project
├── tests/                              # regression tests for scripts/ and for examples/
├── examples/                           # two worked project trees: greenfield/ and takeover/
├── archive/general-workflow-v0.12.0/   # read-only previous version, not part of an install
├── AGENTS.md                           # conventions for editing this repo, not part of the skill
├── README.md
├── CHANGELOG.md
└── LICENSE
```

`SKILL.md` carries only what is true in every stage; the per-stage decision
lists, mechanism trade-offs and test boundaries live in `references/` and are
paid for one file per turn. A rule with two homes drifts, so each rule has
exactly one authoritative file and the others point at it: LEAN reductions only
in `00-lean-path.md`, HIGH-RISK deepening only in `00-project-profile.md`,
claiming and returning a slice only in `07-vertical-slice.md`, the refactor
slice's format and gates only in `00-refactor-path.md`, the takeover survey's
order and gates only in `00-brownfield-entry.md`. Two checks
enforce that, and both stop short of the whole job; the checker section below
says where.

`archive/` is a frozen copy of the pre-rewrite workflow. It must stay complete
and must never be referenced from `SKILL.md` or an active reference; the
consistency checker fails if the active tree routes through it. Completeness
is checked only where `archive/` exists: the README's install step deletes the
directory, so an installed copy reads as a tree without an archive rather than
as a broken one, prints a NOTE saying so, and only the routing check runs
there.

`examples/` holds two filled-in projects. `greenfield/` was built with the
workflow from scratch: contract, change record and a `docs/workflow/` state
directory. `takeover/` is an old repository brought in through
`00-brownfield-entry.md`: an as-is document, a derived requirements document
that carries every review answer, three change records and a no-owner `S-00`
baseline. `workflow_status.py` exits 0 on both. The consistency checker does
not read them, but `tests/test_examples.py` runs the status CLI against each
and asserts the shared contract fields, so a template change in `references/`
that an example does not follow fails the suite rather than sitting there
stale.

## Build, Test, and Development Commands

There is no application build. Two commands gate every change, and neither
covers the other, so run both:

```powershell
python -X utf8 scripts/check_consistency.py
python -X utf8 -B -m unittest discover -s tests -p "test_*.py"
```

`-X utf8` matters on a console that is not UTF-8: without it the documents'
Chinese body text can turn a readable report into a `UnicodeEncodeError` and a
nonzero exit, which reads as a failing check rather than a failing terminal.

The two scripts have different objects.

`check_consistency.py` validates **this repository's own contract**: the
Reference Map matches the files on disk, every reference is reachable from the
router, the eleven stages and P0 exist in order, each stage's key gates are
present *and their sections still have a body*, each single-authority rule is
still in the file that owns it and in no other, no other section reads as a
retyped per-stage tier policy, `scripts/workflow_status.py` and `tests/` exist,
every `scripts/*.py` path mentioned in the docs resolves, no file exceeds
its size budget, and the archive, where the tree carries one, is complete and
never routed through. It warns at 90% of a budget instead of only failing at
100%.
It does not read `README.md`, `CHANGELOG.md` or this file. Its `--root`
defaults to the tree that contains the script; point it at another copy of the
skill tree to check an installed copy or a fixture:

```powershell
python -X utf8 scripts/check_consistency.py --root "C:\path\to\a\skill\copy"
```

The two authority checks are worth knowing in detail, because a green run is
easy to read as "this rule has one home" and neither check says that.
`check_single_authority` works from a table of phrases and compares literal
substrings. It asserts each phrase is still in its owning file -- a table
guarding wording that no longer exists guards nothing -- and that the phrase
appears in no other `SKILL.md` or `references/` document. So it catches paste,
and only paste. `check_restated_tier_policy` covers part of the remainder by
shape rather than wording: three or more bare stage numbers inside one block -- the lines written
directly under a heading, not its subsections --
each followed within a couple of dozen characters by an exemption or deepening
verb, is reported as a transcribed tier policy no matter how it is phrased.

Two gaps stay open, and only a reader closes them. A rule with no stage numbers
to count -- the claim and return rules in `07-vertical-slice.md` -- can be
reworded into another file and pass both checks. And both read `SKILL.md` and
`references/` only, so a copy in `README.md` or in this file is invisible to
them; the README's two-line summary of what LEAN never gives up is kept in step
with `00-lean-path.md` by hand.

`workflow_status.py` is shipped to projects that use the workflow. It reads the
target project's `docs/workflow/` and has nothing to say about this repository,
so `--root` must point at a *project*, never at this checkout:

```powershell
python -X utf8 scripts/workflow_status.py --root "C:\path\to\a\project" --json
```

Exercise it against `examples/greenfield` or `examples/takeover`, which are
projects of exactly that shape and exit 0, or against a scratch project.
Running it against this checkout only proves that the script starts.

## Coding Style & Naming Conventions

Write Markdown in UTF-8. The size budgets are measured after normalizing CRLF
to LF, so a Windows checkout and a Linux one report the same number and the
budget never depends on which machine ran the check.

Prose follows the existing voice: short sentences, one clause each, a reason
rather than a slogan, and a concrete counterexample when explaining why a gate
exists. No emoji, no marketing phrasing.

In `SKILL.md`, include only the YAML frontmatter fields `name` and
`description`, and keep the description broad enough to trigger the skill in
the right situations. Field names in the state templates are `snake_case` and
must match what `workflow_status.py` parses -- a leading `- `, then the name,
then a colon, with horizontal whitespace only, because `\s` there would match
the newline and let an empty value swallow the line below it. A name with a
space or a slash is silently ignored by the parser. Use fenced code blocks with
a language label such as `powershell`, `text`, `json` or `markdown`.

## Testing Guidelines

Any change under `scripts/`, `tests/` or `examples/` must pass the unittest
suite. The consistency checker does not exercise the scripts, so a disabled
check in the status gate stays green there and is only caught by the suite.
The suite has three parts: `test_workflow_status.py` for the shipped status
gate, `test_check_consistency.py` for this repository's own checker (it builds
a copy of the tree and points `--root` at it), and `test_examples.py`, which
runs the status CLI against both trees under `examples/` the way a consumer
would.

`test_check_consistency.py` also pins the three size budgets. Raising a number
is the only edit that gets oversized prose past the checker with both gates
still green, and it costs its author nothing, so the numbers are asserted
there too: changing one now means changing two files and reading, at that
moment, why an over-budget file means deleted duplication instead of a larger
budget.

New behavior in a script needs a test that fails without it. Prefer a test that
builds a small state tree and asserts on the *error message*, not only on the
exit code: the messages are the interface, and four different failures sharing
one sentence send people to the wrong repair.

For documentation changes, check three things before review: the frontmatter
loads, the instructions are short enough to be worth their context, and every
reference is reachable from `SKILL.md`. For substantial edits, forward-test with
a realistic prompt such as "Use this skill to plan a new feature workflow" and
revise wherever the agent hesitates or loads more than it needs.

## Commit & Pull Request Guidelines

Before committing: both commands above exit 0; `git diff --check` is clean; no
file is newly over its size budget, and no budget was raised to make that
true; `CHANGELOG.md` has an entry for any change in behavior; and `README.md`
plus this file still describe the tree that actually exists.

Follow the Conventional Commit style already in `git log` -- `docs:`,
`feat(skill):`, `fix(skill):`, `refactor(skill):`, `test(skill):` -- with `!`
for a change that invalidates existing project state, such as
`feat(skill)!: delivered requires a real call`. The body should say what used to
go wrong, not only what was added.

Pull requests should summarize the behavior change, list the affected files,
include the validation commands that were run, and call out any change to
trigger behavior or to the state-file format that existing projects must
migrate.

## Security & Configuration Tips

Do not store secrets, credentials, tokens, private host details or
project-specific business data anywhere in this skill, including examples,
tests and fixtures. Keep every example generic so the skill stays reusable
across repositories, and keep local editor or tool configuration out of the
tree by adding it to `.gitignore` rather than committing it.
