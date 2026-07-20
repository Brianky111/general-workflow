# Changelog

Skill package version is independent of the source document version (v3.8).

## 0.12.0 - 2026-07-20

Stage routing and completion are now anchored to the original request rather than to newly discovered workflow work.

- The immutable original user request plus explicitly accepted deltas form the Delivery Anchor. Structured requirements, BDD, plans, TOS, tests, reviews, and status are subordinate projections/evidence and cannot expand delivery scope.
- Before any stage selection or new discovery, the router classifies `ANCHOR-SATISFIED`, `ANCHOR-UNMET`, or `ANCHOR-BLOCKED`. Only `ANCHOR-UNMET` with one concrete source-backed `request_gap` may continue; no gap means closeout, quarantine/follow-up, or a newly authorized delivery.
- Multiple incomplete outcomes follow explicit user priority, then the dependency order required for the next user-visible vertical result. The former “earliest unresolved material risk” tie breaker is removed.
- `ORIGINAL-REQUEST-DONE` requires observable production-path outcomes, preserved non-goals, completed requested writes, applied accepted deltas, and no known reproducible anchor-falsifying counterexample. TOS green alone is insufficient.
- Every plan row, test obligation, discovery campaign, write batch, review, and blocking gate must cite the anchor outcome it completes or proves. An unanchored item is `INVALID-OBLIGATION`/follow-up: it cannot enter red, consume repair budget, or block completion.
- To keep the ordinary path implementation-forward, a plan declares its Anchor/current gap once and rows reuse existing AC/R/EX/obligation IDs. Default allowances are implicit, discovery is off by default, and counters/campaign details are recorded only when triggered, overridden, consumed, or handed off—never as an all-zero workflow ledger.
- Review, coverage, mutation, fuzz, CI, and executor findings affect the current delivery only when reproducible and when they actually falsify an original/accepted outcome or its minimum credible proof. Theoretical improvements and neighboring bugs no longer trigger another red/review cycle.
- Accepted changes append a delta to the current anchor version without rewriting original-source history. Verified drift inside an existing compatibility promise is evidence against that promise; unrelated drift remains a candidate until accepted.
- Status and diagrams now expose the anchor state and selected `request_gap` before subordinate stage/TOS details. Consistency checks protect this priority ordering against regression.

## 0.11.0 - 2026-07-20

Test execution now has a finite boundary and a mandatory terminal predicate.

- Planning freezes a finite Test Obligation Set (`TOS`) inside the existing sparse verification map. Ordinary work uses one rule obligation per distinct changed behavior/invariant and adds focused connection proof only for a named seam that can fail independently.
- Tests, reviewers, coverage tools, executors, and the orchestrator may discharge obligations or report candidates but cannot self-accept expansion. After freeze, only a user/authoritative-source/verified-drift contract or risk delta, or a distinct reproducible in-scope counterexample admitted under the delivery cap, can change the set.
- Every delivery declares one cumulative integer counterexample cap (ordinary default `1`) and a closed list of risk campaigns. Property, fuzz, mutation, adversarial, and anti-hardcoding limits cannot reset across reroutes, executors, or sessions; reaching a normal limit records `DISCOVERY-CLOSED`, while only missing required evidence or a known unadmitted in-scope blocker becomes `BLOCKED`.
- TOS states are canonical: `PENDING -> RED -> GREEN -> VERIFIED`, with same-key `GAP/REPAIRING` for bounded repairs. `PASS`, `EXISTING-PASS`, and accepted non-test proof are evidence kinds; faithful `UNEXPECTED-GREEN` moves the obligation to `VERIFIED`.
- `INVALID-RED` receives one mapping/setup correction per obligation in total; any later invalid red is `BLOCKED` regardless of category. Ordinary implementation also carries a finite same-failure attempt/time stop.
- Review, independent module review, integration acceptance, and completeness reconciliation can route only an existing frozen obligation back for repair. A re-review verifies the original finding set and cannot restart sampling or adversarial discovery.
- Counterexample recovery admits at most one representative regression obligation per distinct semantic failure, reuses existing failing protection, and never recursively starts another fuzz/property/mutation/adversarial campaign.
- Pure-refactor characterization tests are identified at intake but written only after a finite protection set is frozen. Scheduled CI discovery is independently bounded, deduplicates across runs, and produces candidates without reopening a completed delivery.
- The router evaluates `DELIVERY-DONE` before another test/review loop. It closes only after selected campaigns, all obligations, authorized write batches, runtime wiring/selection, triggered review/integration/governed gates, regression evidence, and in-scope blockers are resolved; then it performs one closeout update and must stop.
- `check_consistency.py` protects the finite-boundary, bounded-discovery, non-recursive recovery, and mandatory-stop anchors across the skill.

## 0.10.0 - 2026-07-20

Implementation readiness and existing-code reuse now outrank document completeness.

- The router has a positive `READY` gate: once observable behavior, material contract deltas, the production write seam, and credible verification are clear, planning, red, and implementation may continue in the same run. Missing optional artifacts and approval timestamps no longer route work backward.
- Lean incremental delivery is the default. Ordinary pre-code work is capped at two new artifacts, 160 non-empty Markdown lines, one human pause, and 20% of expected effort or 30 minutes unless a named risk justifies expansion. Blueprint batching is explicit opt-in.
- Raw source, structured behavior, and BDD examples form the normal compact contract. Clarification asks only behavior-changing questions; a clean ambiguity pass records a concise result; separate interface, conflict, matrix, audit, and status documents are risk-triggered.
- Existing-code work carries a stable production node (`N-ID`) through reuse scan, planning, testing, red replay, implementation, and review. Each node binds the current owner, real runtime/composition-root path, nearest existing test home, and reused assets.
- `MODIFY_EXISTING` / `REUSE_EXTEND` is the default. New, replacement, or side-by-side owners require reuse-rejection evidence, a non-test runtime edge, wiring proof, and selection/retirement rules; unregistered `V2` implementations and parallel test harnesses are rejected.
- Red tests now have an admissibility path for wrong-SUT, unexpected-green, setup/discovery failures, and stale topology. Invalid red evidence is superseded and replanned rather than used to justify a parallel implementation.
- The default test strategy is a sparse behavior-to-proof map in the existing suite. Full cross-layer matrices and independent completeness artifacts are reserved for connection, safety, compatibility, audit, or multi-owner risk.
- Scope firewalls, executor charters, and worktree closeout remain available without requiring duplicate status mirrors; durable status is updated only at a human pause, handoff, or closeout in one selected surface.
- `check_consistency.py` now protects the cross-stage READY budget, stable production-node binding, sparse/risk-triggered mapping, invalid-red recovery, wiring, and review anchors in addition to reference integrity.

## 0.9.0 - 2026-07-14

BDD behavior discovery is now a first-class stage between structured requirements and interface contracts.

- New `03-bdd-example-mapping.md` and per-round `00-行为示例.md`: map each requirement scenario into observable `R/EX` Rules and concrete Given/When/Then examples, capture Questions before design, and review behavior through business, development, and test/risk lenses.
- Standard features require the BDD gate; lightweight features embed a minimal BDD section, while pure refactors and level-B/C work reuse accepted examples unless a behavior gap appears. Markdown is the default; executable Gherkin remains an opt-in kickoff decision.
- Router, blueprint pacing, clarification, ambiguity audit, interface contracts, conflict scans, planning, Feature Test Matrix, red tests, review, integration, completeness, change protocol, governance, and status schemas now trace `S/E/B -> R/EX -> contract -> test ID -> evidence`.
- Feature Test Matrix rows now key on accepted BDD examples or invariants while preserving their upstream requirement scenario IDs.

## 0.8.0 - 2026-07-13

Vertical full-stack feature delivery and evidence-based completeness replace the previous backend-shaped code-home and unit-green completion assumptions.

- `00-business-taxonomy.md`: a Feature is now one user-visible vertical boundary with declared homes across frontend, runtime contracts, backend layers, adapters, cross-feature handlers, and E2E. The generic backend `models/` drawer is removed; DTOs, commands/results, domain objects, persistence records, and shared wire schemas live in their owning layers.
- New `06-test-strategy.md` and per-round `02-测试矩阵.md`: a canonical Feature Test Matrix coverage view maps every scenario/invariant across Domain, Use Case, frontend, adapter/repository, contract, feature-integration, cross-feature, E2E, and adversarial layers; a linked evidence register resolves stable test IDs to files, commands/environments, fixtures/seeds, assertions, owners, and proof. Blank cells, bare checkmarks, unknown IDs, and unsupported PASS claims are forbidden.
- TDD now runs as behavior-sized red -> green -> refactor micro-batches; router, planning, red-test, implementation, and anti-cheat rules all track evidence per batch.
- `04-interface-contract.md` now contracts the whole slice: UI states, runtime schemas, state machines, events, ownership, idempotency, and downstream effects, not just HTTP methods.
- `09-integration-acceptance.md` now verifies real-layer contracts, persistence after reload, cross-feature effects, UI failure/retry states, accessibility, and critical browser paths.
- New `09-feature-completeness.md` and per-round `09-完整性审计.md`: integration green is no longer terminal. Closeout requires a reconciled test matrix and evidence-backed Definition of Done before archiving.
- Progress/status schemas, governance, blueprint pacing, refactor intake, change handling, UI metadata, README, and the pipeline diagram were updated for the new gates.

## 0.7.0 - 2026-07-13

Change rounds: each add/remove/modify of a feature gets its own numbered document set, archived on acceptance. The `docs/features/` path segment is gone — the canonical tree is `docs/<module>/<feature>/<NN>-<round>/`.

- `00-business-taxonomy.md`: round directories (`01-初建`, `02-<slug>`...) hold the full 00-99 set per change; each round's contract is complete, never a delta, so the newest archived round is the feature's current truth; level B/C work stays inside the active round; `fixtures/` and `status.json` sit at feature level across rounds — counterexamples are permanent regression assets that tests reference by path, so they never move with an archive.
- `status.json` gained `activeRound` with consistency rules (must point to an existing round; archived rounds are read-only — corrections open a new round).
- Change protocol level A opens a round; similarity-triage revision opens a round; integration acceptance archives the round at closeout; the document-set checklist applies to the active round.
- All `docs/features/<feature>/` path references swept to the new canonical forms.

## 0.6.1 - 2026-07-13

- Code homes nest under their module as the canonical form — `src/<module>/<feature>/` mirrors `docs/features/<module>/<feature>/`; a project that flattens one tree flattens both (`00-business-taxonomy.md`, `00-project-kickoff.md`).
- Business-specific example names removed; placeholders only.

## 0.6.0 - 2026-07-13

Business taxonomy with physical arrangement, and per-feature code homes — the requirements tree and the code tree mirror each other, bridged by the contract.

- New `references/00-business-taxonomy.md`: the 产品/模块/功能特性/使用场景/子功能/任务 hierarchy is arranged physically with granularity decreasing by depth — modules and features are directories (`docs/features/<module>/<feature>/`, module overview in `00-模块概述.md`), use cases and sub-features are files (`use-cases/UC<n>-*.md` and `interfaces/*.md`, both split-on-size with the parent doc as index), tasks are tracked entries (`status.json` modules, `99-进度.md` sections). One requirement one doc set unchanged; tiny projects may flatten.
- Use-case splitting mirrors the contract-split idiom: inline `S/E/B` groups until triggers fire, then one file per use case with the roster staying in `00-整理后需求.md` so the user still confirms a single scenario list.
- Placement rules: module-sized requests split before capture; use-case-sized requests merge via similarity triage; use cases outgrowing their feature get promoted; every feature declares `所属模块`.
- Code layout: every feature gets one code home decided at kickoff and recorded in `architecture.md` (default `src/features/<feature>/` with api/application/domain/infrastructure/models/tests, adjusted by the four layer questions; large codebases nest `<module>/<feature>` too); the plan's method-assignment table maps methods to concrete code-home paths; shared code lives in a declared shared kernel.
- Wiring: router evidence scan covers module overviews and split use cases; capture scans module overviews in triage and owns the use-case split trigger; refactor intake recertifies `use-cases/*.md`; kickoff gains code-home, module-grouping, and use-case-threshold tuning items; the document-set checklist covers split use cases.

## 0.5.1 - 2026-07-13

Two refinements from forward-testing session binding (an agent reviewing a freshly claimed module surfaced both).

- Session binding: when the user's own request collides with a fresh claim, surface the collision (owner, freshness, work in progress) before starting — the user may not know the scope is taken (`00-orchestration-policy.md`).
- Review evidence now has a machine-checkable home: `status.json` modules gained optional `reviewer` / `reviewEvidence` fields, `99-进度.md` sections gained a 审查 line, consistency rules require `reviewEvidence` for `done` and `reviewer != owner`, and module initial review records both on pass (`99-status-and-evidence.md`, `09-module-initial-review.md`).

## 0.5.0 - 2026-07-13

Two more mechanisms adopted from Trellis, adapted to this skill's evidence philosophy.

- Session binding (one session, one scope): a conversation claims a feature or executor scope by writing the `owner` field in `status.json` and `99-进度.md` — repo-visible evidence, not a runtime file; scopes with fresh owner evidence are not claimed; stale takeover needs user confirmation and a handoff note; switching features requires closing out through the router; cross-feature parallelism means parallel sessions (`00-orchestration-policy.md`, `SKILL.md`).
- Role-isolated trio as the default for non-trivial module batches: read-only research executor → worker executor (keeps commit rights — red/green commit order and purity are the anti-cheat audit surface, deliberately unlike Trellis) → independent check executor; findings re-checked after fixes; no executor implements and reviews the same scope; the reviewer is never the implementer (`00-orchestration-policy.md`, `09-module-initial-review.md`).

## 0.4.1 - 2026-07-13

Self-review of the 0.3.x/0.4.0 additions found six issues, two of them regressions of the same classes fixed earlier (over-broad rule, always-true router condition).

- Context manifests now bind bounded (worker/review) executors only; discovery tasks — conflict scans, code mapping, sampling, adversarial probing — get a declared search scope instead of a closed file list (`00-orchestration-policy.md`).
- Visual-track-only features no longer loop at the red-tests router row and can enter implementation without a test phase (`00-progress-router.md`, `08-implementation.md`).
- The similarity-triage question now has a home: hard stop in conversation, parked in `requirements-index.md`'s holding area when the file exists (`02-requirements-capture.md`).
- `99-进度.md` gained the feature-level `## 全局` section the document-set mirror rule assumed (`99-status-and-evidence.md`).
- Lightweight features' merged contract+planning gate is now acknowledged in both gate sections — no double human pass (`04-interface-contract.md`, `06-planning.md`).
- Legacy decision records get `D` IDs on first touch, append-only (`03-requirements-clarification.md`).

## 0.4.0 - 2026-07-13

Five mechanisms adopted from a comparative study of Superpowers, GSD, and Trellis.

- Decision coverage gate (from GSD): answered questions become numbered `D` decisions (`03-requirements-clarification.md`); the ambiguity audit flags decisions with no landing clause (`03-ambiguity-audit.md`); contract clauses cite the `D` IDs they implement (`04-interface-contract.md`); the planning gate blocks on unconsumed decisions like unconsumed `C` conflicts (`06-planning.md`).
- Executor context manifest (from Trellis/GSD): the orchestration brief lists exact files with reasons; executors read only the manifest plus their write paths, never pasted history, and report back instead of browsing when it falls short (`00-orchestration-policy.md`).
- Rationalization table (from Superpowers): seven predictable excuses with rebuttals added to `07-anti-cheat-and-red-replay.md`.
- Model tiering (from Superpowers/GSD): briefs assign a model tier by task nature — cheap for mechanical, default for implementation, strongest for architecture/security/adversarial review; reviewers never below default (`00-orchestration-policy.md`).
- Lessons pass (from Trellis): feature closeout proposes promoting what worked into project-level docs — glossary, architecture, CI gates, tuning checklist (`09-integration-acceptance.md`).

## 0.3.2 - 2026-07-12

Refactors are no longer capturable as features.

- `00-refactor-intake.md`: "Not a Feature" rule — no feature folder, `00-原始需求.md`, or roster entry for a refactor; documentation home is the owning feature's `02-规划.md` preflight (one per affected feature for cross-cutting refactors) or the change protocol. The missing-requirements branch backfills docs for the touched behavior, never records the refactor itself.
- `02-requirements-capture.md`: entry guard — refactor requests route to intake; a backfilled folder is named after the behavior, not the refactor.
- `SKILL.md` / router: the refactor rules state the same invariant.

## 0.3.1 - 2026-07-12

The numbered document set (00-… through 99-…) is now explicitly the user's dashboard.

- `99-status-and-evidence.md`: Document Set Checklist — every numbered doc, the stage that produces it, the user question it answers (需求是否符合预期 / 进度如何 / 还差哪些), and its done-criteria; progress reports go against this checklist, not from memory.
- `SKILL.md`: operating rule for keeping the set complete and current as part of the deliverable; the Default Response Shape now includes document-set status (existing docs, missing docs, next unpassed gate).

## 0.3.0 - 2026-07-12

New mechanism (extends beyond the v3.8 source document): one-requirement-one-doc-set as an explicit organizing instinct, plus similarity triage for incoming requests.

- `SKILL.md`: operating rule — every incoming request lands in exactly one document set (new folder, merge into an unconfirmed sibling, or change-protocol revision of a confirmed one); splitting inside a folder is fine, a second folder for the same behavior never is.
- `02-requirements-capture.md`: Similarity Triage section — scan `requirements-index.md` and existing feature goals/scenarios before creating any folder; classify new/merge/revision; when uncertain, stop and ask the user with a fixed shape (similarity points, the case for merging, the case for revising, plus a new-feature option); record the outcome in `requirements-index.md`.
- `00-progress-router.md`: similarity-triage routing row and tie breaker.
- `10-change-protocol.md`: entry condition for triage-classified revisions.

## 0.2.2 - 2026-07-12

Forward-tested the installed skill with Codex CLI on three live scenarios (mid-workflow takeover, refactor in a plain repo, trivial task in a bare repo). Triggering, stage routing, progressive loading (3 files per run), gate discipline, and the kickoff guard all behaved as designed.

- `00-refactor-intake.md`: codified the fallback the refactor scenario exposed — in repositories that never adopted this workflow, treat current public interfaces, observed behavior, and green tests as the protection contract instead of routing to requirements capture; add characterization tests or stop when no protection exists.

## 0.2.1 - 2026-07-12

Round-2 review of the 0.2.0 changes themselves (adversarial diff review plus fidelity spot checks).

- Router: pacing-mode row gained a completion predicate (it was always-true in blueprint mode); governance-audit row narrowed to guardrail-weakening changes (it previously matched every document PR); closeout row defers regression capture to the integration report.
- `00-pacing-mode.md`: re-entry exit added (recorded mode no longer loops back into mode selection); blueprint batches skip grading; conflict reports also cover new modules in old projects; state-file-less projects record mode in kickoff notes.
- `06-planning.md`: planning gate routes pure refactors to implementation, not red tests; stubs generate for new methods/modules only and never overwrite existing code. `04-interface-contract.md` now defers the stub instruction to planning.
- `03-requirements-clarification.md`: questions go into the document being closed out (requirement, contract, or `00-功能.md`), not always `00-整理后需求.md`; self-proof rule moved to Hard Stop. `02-requirements-capture.md` closes every draft through clarification unconditionally.
- `01-project-identification.md`: classification tokens aligned with `status.json`'s `projectType` enum.
- `00-project-kickoff.md`: restored the implementation-strategy-template checklist item; split-threshold and state-file items complete again.
- `08-implementation.md`: pure refactors keep the protection suite green throughout (no red phase).
- `10-change-protocol.md`: restored the probe exception and level B's merge-on-green-CI rule.
- README: documented `PYTHONUTF8=1` for `quick_validate.py` on GBK-default Windows.

## 0.2.0 - 2026-07-12

Fixes from a multi-dimension review (trigger metadata, router state machine, source-document fidelity, engineering hygiene).

### Trigger metadata

- `SKILL.md` description no longer binds triggering to "Codex"; covers new-project kickoff and lists Chinese/English trigger phrases.
- `agents/openai.yaml` short_description now names the domain.

### Router state machine

- Added a terminal "feature closeout" row; the table previously had no match for a successfully finished feature.
- Pure refactor now routes to implementation with existing green tests as protection; it previously dead-ended at red tests, which pure refactors cannot and must not write.
- Fixtures and conflict-scan rows gained completion predicates (they were always-true for old projects, causing circular routing).
- Governance audit is now routable for existing projects, not only via kickoff.
- Lightweight features' merged `00-功能.md` is recognized by the router, interface contract, and refactor intake.
- Kickoff requires user confirmation before bootstrapping governance in a repository with no workflow docs.
- Evidence scan now covers `interfaces/*.md`, `conflicts/*.md`, `domain-models.md`, and the `mode` field.
- New operating rule: after completing a stage's Output, return to the router.

### Source-document fidelity

- New `references/00-pacing-mode.md`: blueprint vs incremental pacing, batch gates, cross-contract consistency check, consolidated question list, probe-first discipline.
- `06-planning.md`: restored the visual track and the standard/enhanced/adversarial tier definitions (pairwise/PICT tables; contract-only attack agent with three-way independence; mutation threshold), and the planning gate (human review, then freeze, then stub generation).
- `04-interface-contract.md`: ambiguity audit is unconditional before the contract gate; merge preconditions, six-question review checklist, and stub generation restored.
- `05-conflict-scan.md`: scan no longer decides implementation strategy (that belongs to planning); added the `## 总结` section and hard rules.
- `03-requirements-clarification.md`: ask-back alignment is a mandatory closing step; fixed `## 待确认反问` / `## 决策记录` section names and the `【答复】：` marker.
- `99-status-and-evidence.md`: added `workflow-state.json` / `status.json` minimum schemas and the `99-进度.md` module-section shape; removed dev-repo-specific instructions.
- `00-project-kickoff.md`: added `requirements-index.md` creation, pacing-mode selection, and the project tuning checklist.
- `04-fixtures-and-probes.md`: fixture paths rooted at `docs/features/<feature>/fixtures/`.
- `01-project-identification.md`: fixed Chinese section names for `00-项目识别.md`.
- `00-feature-grading-and-splitting.md`: "stages 0-5" replaced with concrete reference files; added Output.
- Added Output/Stop Conditions to `00-governance-ci-hooks.md`, `07-anti-cheat-and-red-replay.md`, `10-counterexample-recovery.md`; review/acceptance stages now update status files on pass, and integration acceptance defines the terminal state.

### Engineering

- New `scripts/check_consistency.py`: verifies references ↔ Reference Map ↔ mention links and router reachability.
- README install/validate commands are machine-portable; documented robocopy `/MIR` semantics and exit codes.
- AGENTS.md no longer claims the checkout has no Git history.

## 0.1.0 - 2026-07-09

Initial split of 通用开发工作流 v3.8 into a progressive-disclosure skill package.
