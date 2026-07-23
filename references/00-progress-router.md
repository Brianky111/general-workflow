# Progress Router

Use this file first. Its job is to select the smallest next reference to read.

## Evidence Scan

Inspect, when available:

- the durable original user request/source and each promised observable outcome, non-goal, forbidden effect, explicitly requested write/refactor, and stated priority
- explicitly accepted deltas or supersessions, their authoritative source, and which original outcomes they change without rewriting the original-source history
- real production/runtime and minimum credible evidence for each original/accepted outcome, including whether it is implemented, reachable, verified, superseded, or blocked
- the current user request, especially refactor, cleanup, restructure, rewrite, simplification, delegation, parallel, or multi-agent wording
- whether a local multi-agent/subagent tool is present in the active tool list
- module boundaries, executor-sized tasks, independent review tasks, and any work that can safely be delegated
- before feature similarity triage, whether the request describes one independently acceptable feature or an application/client/platform/program outcome with several feature contributions or construction stages; treat a shared name stem and suffixes such as Android/iOS/web/desktop as weak naming evidence, not merge authority
- when one accepted aggregate outcome needs independently acceptable feature contributions, cross-application/module ownership, staged cross-feature construction, or aggregate proof: the compact solution outcome/non-goals, participating feature/owner/current-source map, dependency and batch order, aggregate proof, single total-progress source, and current aggregate gap
- active worktrees, branches, executor owner fields, handoff notes, uncommitted changes, and unmerged executor output for the same feature or micro-batch
- suspected bugs, failing tests, or design smells not mapped to the Delivery Anchor, and whether they actually falsify an anchor outcome or its minimum credible evidence
- proposed worktree purpose, target requirement/bug ID, approved write set, expected evidence, and closeout rule
- for existing code: the current production owner, runtime entry/registration path, nearest existing test suite and runner, reusable fixtures/helpers/fakes, and the baseline test result
- `docs/architecture.md`, `docs/glossary.md`, `docs/requirements-index.md`, `docs/domain-models.md`
- `docs/<module>/00-模块概述.md` for module boundaries
- the feature's active round `docs/<module>/<feature>/<round>/`: `00-*.md`, `01-*.md`, `02-*.md`, `99-进度.md`; `archive/` holds past rounds' frozen truth
- the round's `00-行为示例.md` or lightweight `## BDD 行为示例`, including `R/EX` traceability and pending questions
- the round's `use-cases/*.md`, `interfaces/*.md`, and `conflicts/*.md` for split use cases and contracts
- the round's `02-测试矩阵.md`, `09-集成验收.md`, and `09-完整性审计.md`
- declared frontend, shared-contract, backend, adapter, and E2E code homes for the feature slice
- `docs/workflow-state.json` (including its `mode` field), `docs/<module>/<feature>/status.json` (including `activeRound`)
- tests, recent diffs, PR descriptions, CI results, and review comments
- the finite `TOS` states and used correction/repair counters, delivery-level campaign IDs/limits and admission-cap use, authorized write-batch state, and triggered review/integration/governed gate state

The original request plus explicitly accepted deltas define **what** must be delivered. Production code/runtime, Git, tests, traces, and CI determine **whether** it has been delivered. Status files only summarize those facts and never override either authority; reconcile them when they conflict.

Evidence may live in the current request, an issue, an existing feature document, or a compact `00-功能.md`; a missing standalone file is not itself a workflow gap. For lean work, one compact source may hold the structured requirement, BDD examples, changed boundary clauses, executable plan, and sparse verification map.

## Delivery Anchor and First Decision

The **Delivery Anchor** is the immutable durable original user request/source plus only explicitly accepted deltas. Preserve the original history; an accepted delta updates the current anchor version rather than rewriting the source. Reuse existing acceptance, `R`, and `EX` identifiers when present. Structured requirements, BDD examples, contracts, plans, `TOS`, tests, review findings, and status are derived views or evidence—not independent sources of delivery scope.

At every meaningful checkpoint, first absorb evidence already produced, then classify the current anchor before starting any new discovery or consulting the Stage Selection Table:

```text
ANCHOR-SATISFIED: every original/accepted outcome is delivered through the intended
                  production entry with minimum credible evidence, every non-goal is
                  preserved, required writes/gates are closed, and no known reproducible
                  counterexample falsifies an anchor outcome
ANCHOR-UNMET:     at least one concrete anchor-linked request_gap remains and can progress
ANCHOR-BLOCKED:   a concrete anchor-linked request_gap cannot safely progress within
                  authority, evidence, or its already frozen finite allowance
```

For an `ANCHOR-UNMET` decision, name exactly one current `request_gap` before continuing. It must be one of:

- an unmet original/accepted acceptance outcome or non-goal/forbidden effect;
- an explicitly requested or authorized implementation/refactor/write batch needed to deliver that outcome;
- a production/runtime/wiring edge needed to make that outcome reachable; or
- a finite proof or gate declared in advance as the minimum credible evidence for that outcome.

Then choose only the stage that most directly closes that gap and state the evidence the stage will produce. When several anchor items are unmet, follow the user's stated priority; otherwise follow the dependency order needed to complete the next user-visible vertical result. Do not order work by the newest finding, the earliest theoretical risk, a missing optional artifact, or what else could be explored.

A test, review, coverage result, mutation survivor, tool output, or executor finding can make the anchor unmet only when it is reproducible, maps to an original/accepted outcome or non-goal, and actually falsifies that outcome or destroys its minimum credible proof. Otherwise record it as a follow-up, out-of-scope candidate, or optional assurance item. It cannot add a `TOS` key, select a stage, or block completion.

If the anchor is `ANCHOR-SATISFIED`, perform one closeout and stop before querying any stage row. If it is `ANCHOR-BLOCKED`, report the exact blocking anchor item and stop without opening another loop. If no valid `request_gap` can be named, do not enter requirements, planning, test, review, discovery, or implementation; the only valid result is closeout, quarantine/follow-up, or a newly authorized delivery.

## Positive READY Gate

Evaluate this only for the selected `request_gap`, after `ANCHOR-UNMET`, and before routing by missing artifacts. Work is `READY` for code when all are true:

1. Observable behavior and non-goals are clear enough to distinguish success from failure.
2. No unresolved choice would change user-visible behavior, data meaning, external compatibility, irreversible effects, security/compliance posture, or accepted scope.
3. Any changed public API, event/schema, persistence meaning, or state transition is explicit; unchanged boundaries can be inherited from existing code and contracts.
4. Existing-code work names the production owner/runtime path and the nearest existing test home; new work names the intended runtime integration point.
5. At least one credible verification path exists for each changed behavior, with wiring/assembly evidence when a connection itself can fail.
6. When the selected aggregate outcome genuinely requires independently acceptable feature contributions, cross-application/module ownership, staged cross-feature construction, or aggregate proof, a minimal solution frame identifies each owned contribution, construction-stage ledger, and aggregate proof while exactly one owning feature gap is selected for immediate execution. A durable staged solution also names its active batch and single aggregate progress source.

The user's explicit request to implement counts as confirmation when the compact contract is a faithful restatement and no item 2 choice exists. If `READY`, route the selected anchor gap to code-reality planning, an admissible red, or implementation. Do not route backward merely because an optional document, approval timestamp, matrix cell, or status mirror is absent.

Expand beyond the lean path only for a named risk that maps to the selected anchor outcome/non-goal, including a repository governance rule already applied to that outcome as predeclared minimum evidence: contradictory intent; public or external compatibility; unknown third-party behavior; irreversible migration or money/permission effects; security/privacy/compliance; concurrency, idempotency, distributed consistency, or a complex state machine; cross-owner events/shared models; safety-critical behavior; or genuinely independent multi-owner delivery. A newly imagined technical concern or unrelated governance gate is a candidate, not an anchor delta. Read `00-feature-grading-and-splitting.md` for the expansion and budget rules.

## Global Completion and Stop Rule

The executable plan owns one finite Test Obligation Set (`TOS`) inside its sparse verification map; it is not a new required artifact or a second definition of done. Every row must cite the anchor outcome/non-goal whose minimum credible proof it supplies. An unanchored row is `INVALID-OBLIGATION`: close it as invalid/superseded or move it to follow-up, never enter red for it, and never let it block completion. Use one canonical state machine for valid anchor-linked rows:

```text
new behavior:  PENDING -> RED -> GREEN -> VERIFIED
existing proof: PENDING -> VERIFIED  (evidence kind: EXISTING-PASS)
non-test proof: PENDING -> VERIFIED  (evidence kind: ACCEPTED-NONTEST)
repair:         VERIFIED/GREEN -> GAP -> [RED when recapture is needed] -> REPAIRING -> VERIFIED | BLOCKED
stop:           any active state -> BLOCKED
```

`PASS`, `EXISTING-PASS`, and `ACCEPTED-NONTEST` are evidence kinds, not obligation states. Default allowances are implicit: one planning-gap correction, one invalid-red correction per valid obligation, one aggregate repair/recheck, ordinary counterexample cap `1`, and no discovery campaigns. Do not create an all-zero ledger. Record a counter/campaign only when it is triggered, overridden, or consumed, in the existing plan/TOS row or executor handoff, and persist that use before a pause, owner/session handoff, or executor closeout so rerouting cannot reset it.

Evaluate this predicate before selecting another red, review, integration, counterexample, property, fuzz, mutation, or adversarial stage. First establish:

```text
ORIGINAL-REQUEST-DONE =
  every promised original/accepted observable outcome is present through the intended production entry
  AND every original/accepted non-goal or forbidden effect is preserved
  AND no explicitly requested/authorized write remains unimplemented unless evidence-backed no-op/superseded
  AND no accepted delta remains unapplied
  AND no known reproducible finding actually falsifies an anchor outcome
```

`DELIVERY-DONE` is true only when `ORIGINAL-REQUEST-DONE` is true and all of the following anchor-linked support is closed:

1. The compact behavior contract remains a faithful frozen projection of the current Delivery Anchor.
2. Every discovery campaign selected in advance as necessary to prove an anchor item is `DISCOVERY-CLOSED`—with an empty list closed by default—and every valid anchor-linked `TOS` obligation is `VERIFIED`; no such row remains `PENDING`, `RED`, `GREEN`, `GAP`, `REPAIRING`, or `BLOCKED`.
3. Every anchor-required implementation/refactor/write batch is integrated, or explicitly closed as evidence-backed no-op/superseded; no assigned executor/worktree for that work remains open.
4. Every production edge, wiring/assembly point, runtime selection, and retirement condition needed to expose an anchor outcome is verified.
5. Every review, integration, safety, compatibility, or governed gate declared in advance as minimum credible anchor evidence has run once and closed.
6. The selected minimum target/regression commands for the anchor outcomes are green, apart from explicitly quarantined pre-existing out-of-scope failures.
7. No reproducible anchor-linked blocking failure remains.

When `DELIVERY-DONE` holds, classify the anchor as `ANCHOR-SATISFIED`, route directly to one closeout update, report completion, and **stop**. Do not run another review sample, red test, mutation, fuzz, property, counterexample hunt, completeness pass, or “one more edge case.” Open a new red target only for a valid anchor-linked frozen `PENDING` obligation or a same-key `GAP` with unused aggregate-repair allowance; advance existing `RED`, `GREEN`, or `REPAIRING` work through its owning stage without creating another key.

After freeze, only an accepted Delivery Anchor delta, or a distinct reproducible counterexample that actually falsifies an anchor outcome and is admitted under the delivery's predeclared absolute cap, may add an obligation. Tests, coverage tools, reviewers, executors, and the orchestrator cannot self-accept expansion by renaming a candidate as a risk. Verified external drift covered by an existing compatibility promise is evidence that the same anchor item is unmet; drift outside that promise is only a change candidate until accepted. Discovery limits are cumulative for the current accepted delivery and cannot be reset by rerouting, a new executor/session, or a renamed campaign. Reaching a limit closes that pass as `DISCOVERY-CLOSED`; continue already admitted obligations. It is `ANCHOR-BLOCKED` only when minimum required anchor evidence could not be produced within the budget or a known reproducible anchor-falsifying failure remains unadmitted.

If no `PENDING` obligation remains while minimum anchor evidence is incomplete, map the `request_gap` to its existing obligation and repair/reconcile only that item. If no obligation owns proof that was declared necessary for an already frozen anchor item, the freeze is defective: stop as `PLANNING-GAP` before writing a test. The orchestrator may consume the delivery's single recorded `planning_gap_refreeze_used=0/1` correction only when the gap cites that original/accepted anchor item; another omission is `ANCHOR-BLOCKED`, while genuinely new behavior needs an accepted delta. Any second `INVALID-RED` after one correction for the obligation is `ANCHOR-BLOCKED`, regardless of failure category. A delivery-blocking downstream finding gets one repair plus one recheck; recurrence of the same obligation/failure bottom line is also `ANCHOR-BLOCKED`. Governance-only or unanchored findings cannot consume the allowance. Renaming identifiers or root-cause labels never resets an allowance.

## Stage Selection Table (`ANCHOR-UNMET` Only)

Do not consult this table until the first decision has produced one selected `request_gap`. Every matching row is implicitly qualified by: “this evidence prevents that named original/accepted anchor item from being delivered or credibly proven.” If the evidence cannot complete that sentence, the row is ineligible and the finding is follow-up/OOS/optional assurance.

| Evidence | Current stage | Read next |
|---|---|---|
| A same-feature executor/worktree/branch holds work needed for the selected anchor gap and is active, unmerged, uncommitted, lacks a handoff, or would lose/conflict with that work | Orchestration closeout | `00-orchestration-policy.md` |
| A writable worktree/executor is requested but no concrete feature, micro-batch, bug/counterexample ID, write set, expected evidence, or closeout rule is defined | Worktree charter missing | `00-orchestration-policy.md`, then route to planning/status instead of opening it |
| A new repository explicitly adopts project-wide workflow governance and lacks a decision needed for the first vertical slice | Minimal project kickoff | `00-project-kickoff.md` |
| The user explicitly requests blueprint batching, or multiple owners require a shared pre-implementation freeze | Pacing mode | `00-pacing-mode.md` |
| Before feature similarity triage, the request may describe an application/client/platform/program outcome whose scope contains several independently acceptable features, cross-application/module ownership, staged cross-feature construction, or aggregate proof; or such a solution lacks its outcome/non-goals, feature-owner map, stage/dependency order, aggregate proof, active batch, or total-progress source | Solution framing | `00-solution-framing.md` |
| A risk mapped to the selected anchor outcome/non-goal—including a governance rule predeclared as that outcome's minimum evidence—may require more than the lean budget or a split contract | Risk grading | `00-feature-grading-and-splitting.md` |
| User asks to refactor/cleanup/restructure/rewrite/simplify, or a plan selects refactor-before-implementation, and this batch lacks a current classification/protection baseline | Refactor intake | `00-refactor-intake.md` |
| The selected anchor item explicitly includes governance/CI behavior, or its only credible proof depends on changed guardrails (CI workflows, hooks, audit scripts, CODEOWNERS) or append-only fixtures | Governance audit | `00-governance-ci-hooks.md` |
| Whether existing behavior/structure must be reused is genuinely unclear after a quick repository scan | Project identification | `01-project-identification.md` |
| After the solution candidate gate is explicitly rejected or the aggregate solution is framed, one routed behavior overlaps or resembles an existing feature's requirement | Similarity triage | `02-requirements-capture.md` |
| The selected original/accepted outcome cannot yet be enumerated well enough to judge completion | Requirements capture | `02-requirements-capture.md` |
| The selected outcome exists but its success/failure cannot be distinguished without a concrete Given/When/Then example | BDD Example Mapping | `03-bdd-example-mapping.md` |
| A real unresolved question would change observable behavior or a material safety boundary | Clarification gate | `03-requirements-clarification.md` |
| A source-citing suspicion could show that the compact requirement/BDD mistranscribed the selected anchor item, and its one proportionate cold-read has not closed | Ambiguity audit | `03-ambiguity-audit.md` |
| A material public/runtime boundary changes and the delta is not explicit in existing contracts or the compact bundle | Interface contract delta | `04-interface-contract.md` |
| Contract uses external service examples, protocol samples, or mock data without matching captures in `docs/<module>/<feature>/fixtures/contract/` | Fixtures and probes | `04-fixtures-and-probes.md` |
| Existing-code work does not yet identify the current production owner, runtime path, reuse candidates, nearest existing test home, or real conflict | Code reality and reuse scan | `05-conflict-scan.md` |
| The selected anchor outcome is unmet or implemented-unproven, but no executable reuse-first plan maps its remaining production delta, write batches, finite `TOS`, delivery cap, and verification commands | Planning | `06-planning.md` |
| A source-backed risk required for the selected anchor outcome needs expanded coverage, but the sparse verification map does not yet prove that connection or invariant | Risk-triggered test strategy | `06-test-strategy.md` |
| An executable plan contains a material behavior/safety/compatibility decision the user has not made | Combined decision gate | Ask the exact decision, record it in the owning compact contract, then return to `06-planning.md` |
| Minimum regression/wiring/risk evidence for the selected anchor item cannot be mapped to an obligation in the frozen `TOS` | Planning-freeze defect | Stop before testing; allow one explicit `PLANNING-GAP` correction tied to that already frozen anchor item, otherwise require an accepted delta |
| A pure refactor has a frozen `PENDING` characterization obligation | Protection capture | `00-refactor-intake.md`; add only the planned characterization in the existing test home, verify it against the current owner, then return here |
| The frozen `TOS` contains a concrete anchor-linked `PENDING` obligation for the selected gap that requires test-first proof through its approved production node, and the batch is not a pure refactor | Red tests | `07-red-tests.md` |
| An existing anchor-linked frozen obligation is `GAP`, its finding falsifies the selected anchor item, its aggregate repair/recheck allowance is unused, and regression capture must fail before repair | Same-obligation regression red | `07-red-tests.md`; keep the same obligation key and finding set |
| Test/implementation commits need audit or red proof is suspect | Anti-cheat/red replay | `07-anti-cheat-and-red-replay.md` |
| An admissible anchor-linked red exists and the selected outcome's implementation is incomplete, refactor intake classified its requested write batch as pure refactor, or the selected remaining gap is visual-track only | Implementation | `08-implementation.md` |
| Implementation exists for the selected anchor outcome and its production result or minimum frozen regression/wiring proof still needs verification | Review and verification | `09-review-and-verification.md` |
| A source-backed risk or independently owned module needed for the selected anchor item claims done but its one required independent review is missing | Module initial review | `09-module-initial-review.md` |
| A connection, cross-feature, persistence, public-contract, or critical-UI risk needed for the selected anchor outcome lacks real-layer evidence | Integration acceptance | `09-integration-acceptance.md` |
| Anchor-linked high-risk/governed work has integration evidence but still needs its predeclared final independent evidence reconciliation | Feature completeness | `09-feature-completeness.md` |
| A distinct reproducible production failure that actually falsifies an anchor outcome has been admitted as a counterexample obligation within the declared admission budget | Counterexample recovery | `10-counterexample-recovery.md` |
| An anchor-linked planned discovery pass reaches its cumulative limit and no unadmitted anchor-falsifying blocker remains | Discovery closed | Record `DISCOVERY-CLOSED`, keep only admitted obligations, and never reset this delivery's budget |
| Minimum anchor evidence could not be produced within budget, a known anchor-falsifying failure remains unadmitted, any second invalid red occurs after one correction for its obligation, or a delivery-blocking downstream finding repeats after one repair/recheck | Bounded blocker | Classify `ANCHOR-BLOCKED`, report the affected anchor item and evidence, and do not open another test, review, campaign, or discovery loop |
| Reproducible bug or failing test does not falsify an anchor outcome or block its minimum evidence | Scope quarantine | Record as out-of-scope/follow-up; continue only the already selected anchor gap, or stop if none remains |
| The user or an accepted authoritative source changes an anchor item, or an external-drift candidate is explicitly accepted | Change protocol | `10-change-protocol.md` |
| The selected human-maintained status source contradicts production/Git/test/CI evidence so the selected anchor item's completion cannot be judged | State reconciliation | `99-status-and-evidence.md` |
| `DELIVERY-DONE` holds for the Delivery Anchor and its minimum anchor-linked implementation/evidence | Feature closeout | Sync the one selected status source per `99-status-and-evidence.md`, report completion, and stop |

## Lean Fast Path

For an authorized ordinary change, prefer this continuous path:

```text
immutable original request + accepted deltas = Delivery Anchor
→ classify ANCHOR-SATISFIED / ANCHOR-UNMET / ANCHOR-BLOCKED
→ if unmet, select one source-backed request_gap
→ before feature merge/revision triage, run the solution candidate gate
→ when independently acceptable feature contributions, staged cross-feature construction, or aggregate proof are required, frame the minimal solution, select its active batch, and choose one owning feature gap
→ concise structured behavior + BDD examples only as needed to judge that gap
→ actual-question clarification only
→ one cold read (findings or concise clean result)
→ freeze a faithful compact projection of the anchor
→ existing-code owner/runtime/test-home scan
→ smallest anchor-linked executable plan and frozen finite TOS
→ consume each pending obligation: admissible red/existing-pass → green → verified
→ targeted regression and wiring evidence
→ re-evaluate original request before any new loop
→ DELIVERY-DONE → ANCHOR-SATISFIED → one closeout update → stop
```

Contract freeze, planning, red, and implementation may occur in the same run. A clean audit, an empty risk category, or the absence of an optional file never creates another user gate. If a test against the actual production owner is unexpectedly green, use it as existing evidence for the same frozen obligation. If that evidence plus production reachability shows the anchor outcome was already delivered and no requested write remains, close it as an evidence-backed no-op. Sharpen the test only when the frozen anchor already contains a distinction the test failed to express; never invent a new behavior or parallel SUT merely to manufacture red.

## Orchestration Overlay

Subagent availability does not select the workflow stage. After choosing the stage, decide whether to load `00-orchestration-policy.md`.

Load it when the task is non-trivial and any of these are true:

- local subagent tools are available;
- the work has executor-sized modules, tests, reviews, probes, or audits;
- independent evidence would reduce risk;
- the main thread would otherwise start implementing while also trying to coordinate.

In orchestrated mode, the current conversation is the orchestrator. It may inspect state, plan, launch executors, monitor outputs, integrate results, resolve conflicts, run final verification, and report to the user. It must not simultaneously implement the same delegated scope.

Before launching another executor/worktree for a feature, run the closeout gate in `00-orchestration-policy.md`. If a previous loop has not been integrated into the current document set and Git evidence, route to orchestration closeout and then `99-status-and-evidence.md` before selecting the next implementation loop.

Before opening any writable worktree, require the worktree charter in `00-orchestration-policy.md`. If the request is exploratory or vague, use a read-only executor/discovery pass in the current workspace and return to planning before code edits.

## Tie Breakers

- First decide whether the Delivery Anchor is satisfied; no stage, finding, risk, or missing artifact outranks this question. If multiple anchor items are incomplete, follow explicit user priority, then the dependency order needed for the next user-visible vertical outcome. Within that one item, choose only the smallest stage that closes its named `request_gap` and produces the stated completion evidence.
- `DELIVERY-DONE`/`ANCHOR-SATISFIED` outranks every discovery or review row, and the closed TOS never reopens. A later accepted user/authoritative-source delta creates a new delivery with a newly frozen finite boundary. Verified drift covered by an old compatibility promise may falsify that promise before closeout; unrelated drift or a “stronger evidence” suggestion cannot revive a closed delivery.
- If the user explicitly asks for a later-stage task, check earlier evidence only for substantive blockers. Skip missing optional documents and do not report them as prerequisites.
- If refactor is requested and this batch lacks a current classification/protection baseline, run refactor intake before code changes. Once that evidence is recorded, do not re-enter intake unless behavior/protection evidence changes. Never record the refactor as a new feature or requirement.
- If an incoming request resembles an existing feature, first run the solution candidate gate in `00-solution-framing.md`. Naming resemblance—including a common product stem or platform suffix—cannot merge an aggregate application/client delivery into one feature. After rejecting or framing the solution, run the similarity triage in `02-requirements-capture.md` for each routed behavior: one requirement owns one behavior source.
- A solution is an aggregate delivery projection, not a scope authority or permanent parent in the module/feature taxonomy. Use it only to coordinate independently acceptable contributions, cross-feature construction stages, and aggregate proof; keep each behavior in one feature contract. A shallow finite batch ledger and aggregate progress record are required for a durable staged solution, but detailed child-feature planning remains just in time unless blueprint pacing is explicitly justified.
- If clarification changes an accepted rule, example, precondition, outcome, or failure bottom line, route back to `03-bdd-example-mapping.md` before ambiguity audit or contract work.
- If refactor intake classified the batch as pure refactor, skip behavior-red work. First verify any finite frozen characterization obligations as existing green evidence, then route to `08-implementation.md` with that protection baseline.
- Red/green work advances one anchor-linked frozen obligation at a time, and several ready obligations may continue in the same run only while each closes a named anchor gap and until the finite `TOS` is exhausted. Re-evaluate the Delivery Anchor at meaningful checkpoints; do not continue merely because another obligation or possible test can be imagined.
- A bounded discovery pass stops at its first declared wall-clock/attempted-case/mutant/admission limit. Count attempts, not only unique seeds. Its delivery-level budget cannot be renewed by rerouting, a new executor/session, or a renamed campaign. Duplicate seeds, equivalent mutants, already-covered examples, theoretical reviewer concerns, and out-of-scope failures do not create obligations.
- If a campaign reaches its limit while another obligation is `PENDING`, first record the campaign's one-way `DISCOVERY-CLOSED` transition, then select the existing obligation. This bookkeeping transition neither blocks delivery nor consumes or renews a test stage.
- A micro-batch is not finished just because an executor returned or a worktree exists. Treat it as unfinished until the orchestrator has integrated or rejected code/test/doc changes, run verification, recorded the handoff in the selected status surface when one exists, and released or advanced ownership.
- Do not route every discovered bug into repair. Only a reproducible production finding that maps to and falsifies an anchor outcome or its minimum credible proof can select repair. Otherwise quarantine it as a follow-up; if fixing it would expand behavior, architecture, or ownership, require an accepted change through `10-change-protocol.md` before editing.
- If local subagent tools are present, make an orchestration decision after stage selection. Do not treat tool availability alone as a stage or as permission for the main thread and executors to work on the same scope in parallel.
- If the repository has no workflow docs and the user has not asked for project-wide governance, do not bootstrap it. Use the lean compact contract in the current issue/conversation or one existing project document and begin the first vertical slice when ready.

## Output

State the Delivery Anchor source/current accepted delta, `ANCHOR-SATISFIED` / `ANCHOR-UNMET` / `ANCHOR-BLOCKED` result, and decisive production evidence first. Only for `ANCHOR-UNMET`, name the one selected `request_gap`, subordinate stage, `READY` result, next reference, and immediate anchor-closing code/test action. For `ANCHOR-SATISFIED`, close once and stop; for `ANCHOR-BLOCKED`, report the exact anchor item and exhausted/missing authority without launching another loop.
