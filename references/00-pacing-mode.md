# Pacing Mode

## Purpose

Choose project pacing without delaying the first verifiable vertical slice. Default to incremental lean delivery; use blueprint batching only when a named cross-feature risk requires coordinated freeze.

## Entry Conditions

- Project kickoff is underway and pacing affects the requested work.
- Existing pacing evidence conflicts with how delivery is actually proceeding.
- A proposed blueprint would hold several features behind a shared gate.

## Mode Selection

- **Incremental lean:** default for new projects, additions, fixes, and ordinary feature work. Complete the core contract and READY check from `00-feature-grading-and-splitting.md`, then plan, test, and implement that slice without waiting for unrelated features.
- **Blueprint:** opt in only when several in-scope features must agree on a shared public schema/event/state owner before any one can be implemented, a coordinated irreversible migration demands a single freeze, or formal multi-owner/regulatory approval requires a batch baseline.

Repository age, a major-version label, the number of features, or the availability of parallel agents does not by itself justify blueprint mode.

When state files are enabled, record `"mode": "incremental" | "blueprint"` in the one chosen status source. Otherwise record the exceptional blueprint decision in the project or feature contract. A clear user implementation request plus the default incremental choice needs no separate mode confirmation.

## Incremental Lean Rules

1. Apply the default document budget: at most two new pre-code artifacts, 160 nonblank lines, one human pause, and 20% of expected effort or 30 minutes.
2. Preserve or link the raw source, write concise structured requirements with BDD examples, and run the READY check.
3. Ask only questions whose answers change observable behavior or a named risk. Decide reversible internal implementation choices without a user gate.
4. When READY, freeze the core contract and continue into planning, tests, and implementation in the same run.
5. Add dedicated interface, conflict, matrix, fixture, or status material only for the risk triggers in `00-feature-grading-and-splitting.md`.

## Blueprint Rules

Scope a blueprint to the shared risky surface, not automatically to every project feature. State which features and shared contracts are held by the batch and which independent slices may continue incrementally.

Use only the necessary batch gates:

1. align the affected requirements and BDD examples;
2. freeze the shared public contracts, ownership, migration, or compliance baseline that triggered blueprint mode;
3. record focused cross-feature verification and implementation ownership;
4. release independent feature implementation as soon as its dependencies are frozen.

Consolidate blocking questions and human review into one batch pause when possible. Do not repeat per-feature confirmation for faithful restatements already authorized by the user. If a blueprint exceeds the default document budget, record the triggering risk and why the batch evidence is necessary.

## Re-entry

Do not redo mode selection when current evidence is coherent. In incremental mode, evaluate the current feature's READY state. In blueprint mode, check only the unresolved shared dependency that actually blocks the requested slice; do not hold it for unrelated missing documents.

## Output

- No dedicated pacing artifact is required for the default incremental mode.
- For blueprint mode, record its trigger, bounded scope, blocking shared surface, approval evidence, and release condition in the one chosen project status or contract source.

## Stop Conditions

Stop only when choosing blueprint changes scope or delays authorized implementation, or when a shared compatibility, migration, security, or ownership decision truly requires human approval. Otherwise use incremental lean and continue.
