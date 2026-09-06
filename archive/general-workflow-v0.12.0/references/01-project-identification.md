# Project Identification

## Purpose

Identify only the repository context that changes implementation risk. Classification is evidence for the core contract, not a mandatory document gate.

## Entry Conditions

- The agent cannot tell whether existing behavior or shared conventions constrain the requested slice.
- Project type affects a concrete compatibility, migration, ownership, or code-scan decision.

## Actions

1. Inspect repository structure, package manifests, relevant docs, tests, and obvious entry points.
2. Classify internally using the same tokens as an enabled status source:
   - `new`: no existing behavior must be preserved;
   - `existing`: the requested behavior overlaps existing code;
   - `new-module-in-existing`: the area is new but shared conventions or contracts still apply.
3. Record only the relevant code homes, preserved behavior, and concrete boundaries that later work must respect.
4. Do not infer that an old repository needs a dedicated conflict report. Create one only when a concrete legacy overlap, uncertain migration boundary, or other risk trigger from `00-feature-grading-and-splitting.md` exists.
5. Decide an obvious classification from evidence without asking the user. Ask only when two plausible classifications would materially change project scope, observable behavior, public compatibility, data migration, or ownership.

## Output

For ordinary work, add a one-line classification and its evidence to the structured requirement or existing task/PR; do not create `00-项目识别.md`.

Create a dedicated `00-项目识别.md` only for formal audit, a long-running handoff, or a genuinely disputed classification. When required, keep these sections concise:

- `## 结论`
- `## 证据`
- `## 风险触发的后续检查`
- `## 非目标`

The dedicated file counts against the pre-code document budget in `00-feature-grading-and-splitting.md`.

## Stop Conditions

Stop only when the unresolved classification changes a material risk or scope decision. Otherwise record the evidence and continue in the same run.
