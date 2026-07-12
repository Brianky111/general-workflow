# Project Identification

## Purpose

Decide whether the work is a new project, an old project, or a new module inside an old project. This controls how much code scanning is required later.

## Entry Conditions

- No `00-项目识别.md` exists for the feature, or it is incomplete.
- The agent cannot tell whether existing code must be preserved, extended, or ignored.

## Actions

1. Inspect repository structure, package manifests, existing docs, and obvious entry points.
2. Classify the work using the same tokens as `status.json`'s `projectType` enum:
   - `new`: new project, no existing behavior to preserve.
   - `existing`: old project, existing behavior may be affected.
   - `new-module-in-existing`: new area in an old project, but shared conventions still apply.
3. Record relevant files and areas that the interface/conflict stages must revisit.
4. Avoid making final conflict conclusions here.

## Output

Create or update `docs/features/<feature>/00-项目识别.md` in Chinese, using these fixed section names (downstream agents and template checks depend on them):

- `## 结论` — the classification and its basis,
- `## 已读资料` — evidence read,
- `## 后续接口层必须检查的区域` — areas requiring later code scan,
- `## 本层不做` — explicit non-goals for this stage.

## Stop Conditions

Stop and ask the user if classification changes implementation risk or project scope.
