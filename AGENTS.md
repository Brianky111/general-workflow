# Repository Guidelines

## Project Structure & Module Organization

This repository **is** the skill package. `SKILL.md` at the root is the entry point, `references/` holds the twelve load-on-demand guides, `scripts/` holds the repository checker, target-project guardrail CLI, vendor sync tool, and cross-tool installer, `vendor/pstack/` holds the pinned MIT-licensed Lauren Tan `pstack` skills and `comment-sicko` agent, `examples/` holds three runnable sample repositories, and `archive/` keeps frozen snapshots of v0.12.0 and v1.10.1.

```text
.
├── SKILL.md                             # resident entry: trust pyramid, principles, loops, Reference Map
├── agents/openai.yaml                   # Codex entry metadata
├── references/                          # 12 stage/topic docs (including 01c-01e conditional overlays)
│   ├── 00-router.md                     # resident: intent vs action, repo_guard CLI, routing, pstack dispatch, stop rules
│   ├── 01-intent-and-invariants.md      # 1-page intent + Frontier Grill + GLOSSARY, candor/prototype, vertical slices (WIP=1)
│   ├── 01a-stack-and-architecture.md    # scope gate, stack scorecard + AI fit, deep modules, root ARCHITECTURE.md
│   ├── 01b-dataflow-and-contracts.md    # state SSOT table, dataflow diagrams, code-level contracts, bounds, --check-arch handoff
│   ├── 01c-distributed-and-sync.md      # conditional: multi-store outbox, idempotency keys, fencing tokens, expand-contract
│   ├── 01d-high-assurance-bounds.md     # conditional: ledger conservation, paired assertions, static caps, deterministic seams
│   ├── 01e-client-state-flow.md         # conditional: 4-bucket client state de-complecting, pure reducers, optimistic rollback
│   ├── 02-codebase-guardrails.md        # directory context, reader-load/domain-modeling, anti-hardcoding, clean_scopes, escape hatches
│   ├── 03-verification-and-artifacts.md # Feature Map / verify_skill, scenario verify_cli, bug-fix/perf/forensics/visual-parity/hillclimb, PBT/TLA+
│   ├── 04-correction-and-gardening.md   # inverse pyramid correction, /correct + /reflect + /recall, attack-the-premise, parking-lot, AGENTS diet
│   ├── 05-outer-loop-factory.md         # L0-L3 maturity ladder, clean_scopes L2 promotion, bugbot-triage, unslop, blinded eval, irreversible gates
│   └── 06-repo-guard-contract.md        # .guardrails/ schema (project_kind, clean_scopes), --check-arch, repo_guard.py CLI, v1 migration
├── scripts/
│   ├── check_consistency.py             # validates this repository and vendor/pstack/
│   ├── repo_guard.py                    # ships with skill, runs --scan/--init, anti_patterns, file_limits on target repos
│   ├── install.py                       # cross-tool installer for general-workflow + vendored pstack skills
│   └── sync_vendor.py                   # offline verifier (--verify) and pinned raw fetcher (--fetch)
├── vendor/pstack/                       # pinned MIT snapshot (v0.15.46 @ aaeb0ea) of cursor/plugins/pstack
├── tests/                               # unittest suites for scripts, installer, and examples/
├── examples/                            # clean-app/ (L1), weeding-brownfield/ (L0), and verify-skill-app/ (L1)
└── archive/                             # read-only v0.12.0 and v1.10.1 snapshots (excluded on install)
```

Each rule has one authoritative file and other files point at it:
- Comment & escape-hatch policy: `02-codebase-guardrails.md`
- Behavioral artifact & freshness gates: `03-verification-and-artifacts.md`
- Inverse-pyramid correction ladder: `04-correction-and-gardening.md`
- `L0`–`L3` trust ladder & automation gates: `05-outer-loop-factory.md`

## Build, Test, and Development Commands

Run all gates after any change:

```powershell
python -X utf8 scripts/sync_vendor.py --verify
python -X utf8 scripts/check_consistency.py
python -X utf8 -B -m unittest discover -s tests -p "test_*.py" -v
```

Exercise `repo_guard.py` against the runnable examples (never `--root` against this skill checkout itself):

```powershell
python -X utf8 scripts/repo_guard.py --root examples/clean-app --run-check
python -X utf8 scripts/repo_guard.py --root examples/weeding-brownfield --run-check
python -X utf8 scripts/repo_guard.py --root examples/verify-skill-app --run-check
```

`check_consistency.py` enforces: frontmatter, 1:1 `Reference Map`, reachability from `SKILL.md`, trust-pyramid order, section/gate non-empty bodies (`POLICY_ANCHORS`), single-authority phrases (`EXCLUSIVE_PHRASES`), restated `L0`–`L3` ladder detection (`check_restated_trust_ladder`), script path resolution, `vendor/pstack/` manifest/checksum/frontmatter/reference integrity (`check_vendor`), archive integrity/isolation, and pinned LF byte budgets (`SKILL.md`: 6,500; `00-router.md`: 7,500; references `01`–`06` & `01a`–`01e`: 12,000; warn at 90%).

## Coding Style & Commit Guidelines

- Write UTF-8 with LF (`\n`) line endings; `check_consistency.py` and `repo_guard.py` normalize CRLF to LF before weighing bytes.
- Keep prose concise, concrete, free of emoji and marketing phrasing, and back non-obvious rules with counterexamples.
- Never raise a budget in `check_consistency.py` without also updating `BudgetContractTests` in `tests/test_check_consistency.py` and documenting why; prefer trimming duplication.
- Follow Conventional Commits (`feat(skill):`, `fix(skill):`, `docs:`, `test(skill):`, `!` for breaking state/contract changes) and update `CHANGELOG.md` for behavioral changes.
