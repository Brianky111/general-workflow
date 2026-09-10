# Changelog

## 1.9.0 - 2026-09-09

Refactoring is back in the workflow, as a path rather than a stage. A refactor
walks the same 05-to-09 line a feature does, with every gate in place and the
evidence swapped: instead of claiming acceptance ids it keeps the delivered
ones, and instead of a behavior test going red it has a structure check that
fails before the change and passes after it. The carrier is a second kind of
slice file, `R-<n>.md`, and the status script gates it.

- New `references/00-refactor-path.md`: the three entries (a user request, a
  decision in the stage 11 review table, a boundary problem found in 07 or 09
  whose fix crosses the current slice's write_scope), authorization, the
  pure/behavior-changing/unprotected classification, the protection baseline,
  the structure check, claiming, execution, the exit gate and the stop
  conditions. The ideas come from the archived refactor intake; its vocabulary
  does not.
- A refactor slice claims no A-ID. The script rejects acceptance rows in an
  `R-` file and a backlog row that points at one -- the failure the old
  workflow fixed by rule in 81fea85 and then could not enforce. Its ledger is
  a `## Protection` table of delivered A-IDs (or `P-<n>` characterization
  rows) with a baseline call at the start commit and the same call again at
  the closing commit, and a `## Structure` table whose before/after cells
  carry the check's output. Baseline and before are required while the slice
  is live; evidence and after must end at a different anchor than the cell
  beside them, because one anchor means one of the two runs did not happen.
- `authorized_by` is required on a live refactor slice and must be a pointer
  (`C-<n>`, a document path with an optional heading, or a link). The router's
  "do not start a refactor on your own" rule now has a check behind it: a
  cleanup an agent noticed has nothing to point at.
- Refactor slices take part in the one-live-slice-per-owner rule and the
  write_scope overlap check. The one exception is a feature slice paused for
  its owner's own refactor, declared with `- waiting_on: R-<n>`: that pair may
  share an owner and overlapping paths, and the script says so when the pause
  is missing, when it names something that is not a refactor slice, or when
  the refactor is already closed. Returning the feature slice instead would
  throw away its rows.
- The report gains `kind` on every slice, `protected`, `reverified` and
  structure counts on refactor slices, and a top-level `refactors_in_flight`.
  `scope_complete` is unchanged -- scope is the A-ID ledger -- and the rendered
  report prints the refactor in flight next to it, because 99's task closeout
  now waits for it. A live refactor also carries the cursor, so `next_action`
  may rest while one is open.
- Routing: the stage table sends an authorized refactor to the path; step 2
  no longer lists refactoring among the non-Greenfield triggers (a brownfield
  repository with no ledger still goes through the compatibility-surface
  confirmation and is explicitly outside the path for now); the end-of-round
  rule points at where a refactor is opened. Stage 7 names the pause exception
  beside the one-live-slice rule and sends a boundary fix that leaves the
  slice's write_scope to the path; stage 8 says which refactors stay in its
  Refactor step; stages 9 and 11 route a failed architecture constraint and an
  adopted evolution proposal there; stage 3's firewall says the follow-up
  queue is not authorization. The LEAN reduction list and the HIGH-RISK
  deepening table each gain one refactor row, in their own files.
- No state migration. The kind is read from the filename, `waiting_on` and
  `authorized_by` are new fields, and a project with no `R-` file sees no new
  rejection.
- Sixteen tests cover the new rejections and the two accepted shapes; the
  consistency checker lists the new reference and anchors its sections.

## 1.8.0 - 2026-09-09

Closed the gates that read as checks but accepted anything, gave the state file
a format version so a missing field can be told apart from an old layout, and
collapsed the rules that had grown a second copy. Pre-1.6 single-file state is
recognized instead of read as a new project, and the size budgets are pinned by
a test, so raising one is a two-file decision rather than a one-character edit.
The README was rewritten around the lifecycle map and what a first user has to
do.

- Four checks in the status script were passing values they were supposed to
  reject. `delivery_target` was only tested for being nonempty, so a target
  ending in "差不多做完就行" named a completion boundary and closeout stopped
  wherever the reader decided; it is now read as `<pointer> / <endpoint>`, the
  endpoint being the segment after the last ` / ` and one of
  `implementation-and-tests`, `release-ready` or `deployed:<environment>`. The
  pointer half is required too, and required to reach something: a bare
  `release-ready` left closeout with nothing to check off item by item, and
  `差不多那些 / release-ready` then cleared the not-a-placeholder test while
  still opening nothing, so that half has to be a document path, a
  `C-<number>` or a URL -- the same shape the change-record pointer takes. The
  two halves fail with separate sentences because they need separate repairs.
  `lifecycle`, `tier` and `path` were not validated at all, so `BUILDNG` passed
  and then silently decided nothing; they are checked against their enums, and a
  value that still contains ` | ` is reported as an unedited placeholder rather
  than as an unknown value. `evidence` required an arrow but nothing that could
  be found again, so `pytest -> passed` was a delivered row nobody could
  re-run; it now needs `@ <commit or ref>` or a link, and the anchor itself has
  to name a place -- `@ later` and `@ 稍后` promise one instead of giving one,
  and a promise cannot be checked out and re-run. The change-record pointer
  matched any hyphenated word, which let `follow-up` justify dropping an
  acceptance id; only `C-<number>`, a document path carrying its extension, or a
  URL count now, because taking any string with a slash in it made `ask/bob` and
  `推迟到 v2/以后` change records.
- The evidence anchor stopped exempting an entire class of projects. It looked
  for a link anywhere in the string, and an HTTP entrypoint carries a URL in
  every invocation, so `curl https://api.example.com/orders -> 200 OK`
  anchored itself on the address it called: for HTTP and web projects the
  requirement cost nothing, and the same row passed with `@ later` still
  attached. The anchor is now read where a reader looks for it, at the end of
  the observed-result half, so the URL a request was sent to is no longer the
  proof that this run happened -- it says the entrypoint exists, not that
  anyone called it. `@ HEAD` was the other way through: it is ref-shaped and
  walks past any table of placeholder words, but it resolves to whoever
  committed last, so the row keeps reading as anchored while pointing at
  different code six months later; `HEAD~1`, `main`, `master`, `origin/main`
  and `latest` move the same way and are rejected with it. The ceiling is the
  same as any word list -- `@ dev` and `@ feature/x` move too and still pass.
  A test had frozen the old behaviour as the expected one, asserting that the
  URL row was valid evidence, so the hole had a green test defending it; that
  case is now the negative one.
- Reading the anchor off the tail also has to leave something behind. Once the
  arrow and the trailing ref were each checked on their own, `cmd -> @ abc123`
  satisfied both -- two halves, and an anchor a reader can check out -- while
  recording no observed result at all, which is the half the arrow was added to
  require. Copying the URL the call was sent to onto the right of the
  arrow does the same, and it is the natural move for anyone who has just been
  told the URL no longer counts as the anchor. The result half is now read after
  the trailing anchor is removed, and an empty remainder is rejected with its own
  sentence, because the repair is different from a missing anchor: write down
  what came back. The anchor says where to find the run; it is not the run's
  result.
- `state_version: 2` is required in `project.md`. Releases 1.6 and 1.7 both
  changed what the state means, and with no version marker the script could not
  distinguish "this field was never written" from "this file predates the
  field", so every migration error arrived as a field-level complaint. The
  missing-line error prints the exact line to add, a wrong version points at the
  migration procedure, and that procedure now exists as its own section in
  `99-state-and-handoff.md`: what version 2 asserts, and what a human has to
  rewrite in an older file. It ends with the two things an older file was never
  checked on and therefore never got right by accident -- the three enum fields,
  and the change-record note behind every deferred or dropped row. It also
  starts one step earlier than the rewrites, because they assume a
  `docs/workflow/` directory and the versions before 1.6 kept everything in one
  `docs/workflow-state.md` (or `WORKFLOW-STATE.md`), where there is no shard to
  fix. The procedure now says where each part goes first -- the cursor fields
  to `project.md`, `stage` to the slice file the cursor names, the scope ledger
  split between `backlog.md` and that slice file.
- Skipping that split used to be silent. The script only looked at
  `docs/workflow/`, so a project whose whole ledger sat in the single file
  printed `no workflow state` and told the reader to create one this round, at
  exit 0; whoever took it over read that as a fresh start, built an empty state
  next to the old file, and the A-IDs and evidence already written were never
  opened again. A check that misses something leaves the work where it was; this
  line moved someone to bury it, which is the worse of the two. When
  `docs/workflow/` is absent the script now looks for `docs/workflow-state.md`
  and `WORKFLOW-STATE.md`, and reports `state_status: legacy` with the file it
  found, what has to be carried over, and the instruction not to start a fresh
  state beside it. The exit code stays 0, because nothing here is broken: the
  state is in the older shape, and the migration is a human's. `legacy` is a
  fourth status rather than a variant of `uninitialized` for the same reason:
  "uninitialized" is precisely the reading that causes the loss, so it cannot
  also be the reading the script hands back. It knows the two filenames the older
  layout used, and no others; state parked elsewhere still reads as a new
  project.
- `next_action` gives stages 1-6 a cursor. Before the first slice exists there
  is no `stage` field anywhere, only the project-level `lifecycle`, so a session
  picking up a project stalled halfway through stage 5 had to reconstruct which
  decisions were already made from the ADRs -- and reconstructing it wrong meant
  redoing or skipping work. The field holds the next executable action and the
  command that verifies it; the script requires it once the ledger has rows,
  while no slice is in flight and scope is still owed, and lets it stay empty
  once a slice's `stage` carries the cursor. Words that only say the work
  continues -- "下一步继续", `proceed`, `ongoing` -- are rejected, and both the
  script and the state reference say
  where that check stops: rewrite it as "继续推进登录模块" and it passes. It
  catches an empty cursor, not a wrong one; whether the named action is really
  executable, and whether the command beside it really verifies it, stays with
  the stage gate and the person writing the line.
- Returning a slice used to lock its owner out. The rule said to delete the
  unfinished acceptance rows and fix the backlog, but not to clear `owner` and
  `claimed` -- and a slice with an owner and no delivered row counts as in
  flight, so the abandoned file stayed live forever and the owner's next claim
  failed with `owner holds two live slices`. Returning is now three steps, and
  that error message spells out the third one instead of only naming the
  collision.
- The report no longer dies on a console that cannot encode it. `stdout` and
  `stderr` are reconfigured to UTF-8 with `backslashreplace`, so an English
  Windows console at cp1252 prints the state instead of raising
  `UnicodeEncodeError` and exiting 1, which read as "your state is invalid".
- `acceptance_source` failures say which one happened. An unreadable file, a
  heading that is not there, a heading that is there twice and a selection with
  no A-ID table each need a different repair, and they were arriving as one
  sentence about an expected nonempty table.
- The profile template said it could be merged into `project.md` wholesale, and
  doing that broke the file: `lifecycle` and `tier` appear in both templates, and
  a field set twice is an error, so the documented shortcut produced a
  `set twice` rejection. The templates now say to write those two lines once,
  name the seven fields the script actually parses, and use `snake_case`
  throughout -- `runtime units` and `users/entrypoints` could never match the
  field pattern and were being dropped without a word.
- The LEAN reduction list exists in one place. It had been copied into the
  router, `SKILL.md` and the README, and the copies had already drifted: one of
  them implied stage 6's clean-clone check could be skipped. `00-lean-path.md`
  is now the single authority, it states per stage what is reduced and what is
  not, and it names the two things LEAN never gives up -- the clean-clone check
  with one pipeline, and one real-entrypoint call per acceptance id. `SKILL.md`
  and the router point at it and list nothing themselves. `README.md` does not:
  its tier table still restates those two rules in two lines, because that table
  is where a reader decides whether LEAN fits their project, and the decision
  turns on what the tier refuses to discount. The page says of those two lines
  that they are a copy and that nothing but a person keeps them in step. The
  consistency checker anchors those two sentences in `00-lean-path.md`, but a
  sentence being where it belongs says nothing about
  where else it is, and the second copy is the one that drifts -- so the checker
  now holds a table of the list's wording and asserts, for each entry, that it
  is still in `00-lean-path.md` and appears in no other `SKILL.md` or
  `references/` file. Pasting a compressed copy back into the always-loaded
  router fails the gate; a test does exactly that. That table compares literal
  substrings, so it sees copy-paste and only copy-paste -- and retyping the
  rule in one's own words is exactly what a reader who wants it to hand does.
  A second guard covers part of that gap for the two tier policies by shape
  instead of wording: three or more bare stage numbers inside one block, each
  followed within a couple of dozen characters by an exemption or deepening
  verb, is reported as a transcribed per-stage policy however it is phrased,
  and the two files that own those policies are exempt. Stated as what a green
  run does and does not mean: a pasted copy in `SKILL.md` or `references/` is
  caught, a reworded per-stage LEAN or HIGH-RISK list in those same files is
  caught, and nothing else is. A reworded copy of the claim rules has no stage
  numbers to count and gets past both. A sentence naming two stages is under
  the threshold on purpose, because a guard that fires on ordinary prose gets
  switched off before it ever catches a list. And a copy in `README.md` or
  `AGENTS.md` is invisible to both, which never read either file -- the README's
  two lines are one such copy, kept on purpose and labelled as one. The phrase
  table also guards the HIGH-RISK deepening list and the claim rules below.
- The claim rules moved to `07-vertical-slice.md`. Claiming happens in stage 7,
  but the rules lived in the always-resident state file, so every session paid
  for seven rules it mostly could not use. Stage 7 carries them, the state file
  keeps one pointer, and the exit gate now names the section a slice file has to
  satisfy.
- HIGH-RISK has a per-stage deepening list in `00-project-profile.md`. The tier
  previously offered five summary bullets while individual stage documents
  invented their own "high-risk projects must also..." requirements, so nobody
  could say what the tier actually adds. The table is the only authority, and
  stage documents are read against it.
- `SKILL.md` now names the tier load for both tiers, not only for LEAN. It told a
  LEAN project to read `00-lean-path.md` and said nothing about HIGH-RISK, which
  was survivable while every stage document carried its own high-risk
  requirements; this release deleted those and left the deepening table as the
  only place they exist. The two tiers are not symmetric, and that asymmetry is
  the whole reason the second line is needed: the reduction list is a file of its
  own, so it survives any decision not to read the profile, while the deepening
  list lives inside the profile -- and the router, in this same release, stopped
  loading the profile by default. A HIGH-RISK session could take that skip and
  have nowhere left to read what its tier adds. The router carries the same
  instruction at the point where it would otherwise skip the profile. Saying it
  in both places duplicates a pointer, not a list -- what drifts when it is
  copied is the table, and neither file holds the table.
- Compressed `05-architecture-design.md`. It sat 159 bytes under its budget,
  which is not a margin: the next correction to stage 5 would have had to pay
  for itself by shaving unrelated prose, and the cheapest prose to shave is
  never the least useful. Nothing here changes what the stage asks for. The
  `目的与入口` section is gone because the sections after it said the same
  things again; the five-topic mechanism checklist is one line, since
  `05a-mechanisms-and-contracts.md` carries those same five sections; and the
  sentence that spelled out how deep a low-risk and a high-risk project each
  have to go now points at the profile instead of being a second place that
  states it. One bullet was actually removed -- whether a migration lets old
  and new code coexist -- and the deployment section of the same file already
  decides it. About 1,200 bytes free.
- The router says what happens after a non-Greenfield boundary is confirmed. It
  used to flag old APIs, old data or an existing deployment as a risk and stop
  there, which left the agent to guess between proceeding as if greenfield and
  switching to the archived legacy workflow. Confirmation now sets
  `compat_surface`, carries the old interfaces into stages 4 and 5, adds
  compatibility and migration evidence at 09, and makes 10's rollback cover both
  versions running side by side; declining it narrows the work instead.
- The router no longer rebuilds the project profile every session. Reading
  `00-project-profile.md` was an unconditional step of first contact, so a
  session resuming a project at stage 8 re-derived a tier the user had already
  confirmed -- and deriving it differently silently changed the depth of
  everything after it, while holding a fourth document resident all session. A
  status script that exits 0 has already checked `tier` and `path` against their
  enums, so the answer is in the state; the profile is loaded for a project with
  no state directory, when those two fields are missing, print as `?` or
  contradict what the repository shows, or when a P0 return is triggered. A
  `tier: HIGH-RISK` project needs one condition more than those three. None of
  the three holds for a HIGH-RISK project resumed at stage 8, and the same release
  had just made the profile's deepening table the only authority -- stage
  documents no longer carry high-risk requirements of their own -- so the skip
  took the stage-8 deepening row with it and left nowhere to read it from. The
  router now sends a HIGH-RISK session back for that one row before entering
  any stage, taking the table without re-deciding the tier. The saving itself
  is anchored now too: the conditional-load heading is checked as a policy
  anchor whose section must still have a body, and the skip and the HIGH-RISK
  exception are checked as substrings inside it, because deleting them left
  every other check green -- the router still routed, every
  other anchor still matched, and the profile was quietly a fourth resident
  file again.
- A placeholder was accepted as the observed result. The result half only had
  to be nonempty once its trailing anchor was removed, so `cmd --run -> 见上
  @ abc123` recorded a real commit next to a word meaning "see above". The
  script already keeps a table of words that promise a place instead of naming
  one; it was applied to the anchor and not to the half the anchor exists to
  locate. That half is now held to the same table. The ceiling is unchanged and
  stated where the other word tables are: a result phrased outside the table
  still passes, and nothing here can tell the URL a call was sent to from the
  link to its run.
- A half-migrated project stopped hiding the ledger beside it. An empty
  `docs/workflow/` next to a full single-file state reported only "missing
  project.md", which is the reading that makes the next agent fill in the empty
  shards and leave every old A-ID unread; the rendered report now names the old
  file and points at the split. `legacy_state` is `[]` in the "uninitialized"
  and "ready" reports and carries that file in an "invalid" one, which the
  module docstring previously denied.
- Corrected three descriptions that had drifted past what the code does. The
  handoff reference still said the script reports `no workflow state` for a
  single-file project and exits 0 -- the behavior this release replaced -- so
  it was teaching that the guard does not exist while the README described the
  new one. The README and AGENTS.md both said the shape guard counts stage
  numbers "inside one section"; it counts them inside one block, the lines
  written directly under a heading, so splitting a restated list across two
  subheadings separates the counts. Both also said a reworded copy cannot dodge
  it, which holds only while the reduction verbs stay: change those too and the
  guard sees nothing.

- Reordered the routing algorithm. "Is this a question or a job?" was step 1 of
  the algorithm but had to be answered before the algorithm ran, and the
  blocking criteria were listed twice with different wording. The first-contact
  section answers the question, the algorithm has one blocking list, and the
  read-only status command is inlined in the router so a session that only wants
  to check state does not load the state reference to find it.
- The default response shape has two tiers. One six-item report per turn meant a
  stage 8 session re-reported the project profile every round, burying the one
  thing that had changed. The full six are for handoff or a change of tier or
  stage; continuing inside a stage reports what changed, the gate status and the
  next action with its verification command.
- `check_consistency.py` takes `--root` and has its own tests. It hardcoded the
  tree it lives in, so nothing could point it at a fixture and its own checks
  were never exercised -- a broken assertion looked exactly like a clean run.
  The suite now builds a copy of the tree, breaks one thing at a time and
  asserts the checker notices.
- The size budget counts the same bytes on Windows and on Linux, which it had
  only appeared to do. The newline normalization ran on the result of
  `Path.read_text`, which applies universal newlines, so there was never a
  `\r\n` left for it to replace -- dead code, and two tests were crediting it
  with a behaviour they would have passed without it. Files are read as bytes
  and decoded before the newlines are collapsed, so the count no longer moves
  by one byte per line between checkouts: a document that fits under 13,000 in
  a `core.autocrlf` checkout no longer fails there while passing everywhere
  else, for an edit nobody made. The frontmatter check now depends on the same
  normalization -- `startswith("---\n")` is the first thing a raw CRLF decode
  breaks -- so a whole tree rewritten with CRLF is checked end to end, not only
  weighed. The two budget tests assert what they always claimed to: delete the
  normalization and they turn red.
- The three budget numbers and the 90% warning line are pinned in
  `test_check_consistency.py`. Every other convention in this tree is held up by
  something a change has to get past -- a gutted section fails the anchor check,
  a pasted rule fails the phrase table -- and "over budget means delete the
  duplication, never raise the number" was the one held up by nothing.
  `SIZE_BUDGETS` was read by one function and by no test, so `9_500` ->
  `10_500` was a one-character edit that left both gates green, and it is the
  first edit anyone wanting one more paragraph in the router will reach for,
  because it is the only one that costs them nothing. The pinned copies are
  written out in the test rather than imported, so a change has to be made twice
  in two files, with the reasoning printed as the assertion message at the moment
  it fails. The whole table is compared, not only its values: dropping
  `SKILL.md`'s entry lets it fall through to the 13,000-byte reference budget and
  buys 5,000 bytes with a deletion. Each budget is also walked from the outside,
  one byte under and one byte over, so rewiring which file gets which number
  fails even with every constant untouched. The warn line is pinned one step
  earlier for the same reason: with five WARN lines already printing, the
  cheapest way to make the output look clean is not to touch 9,500, which reads
  to a reviewer as a budget change, but to nudge 0.90 to 0.97, which reads as
  tuning and silences all five at once. None of this can stop a number from
  changing, and nothing could. It makes the change a decision instead of a
  reflex.
- The gate descriptions in `README.md` and `AGENTS.md` had not caught up with the
  two single-authority guards this release added. Both pages listed a smaller set
  of checks than the checker runs, so the guard most likely to be tripped by an
  ordinary edit -- moving a rule's wording into the file where it gets read -- was
  the one nobody had been told about, and it would have arrived as an
  unexplained failure. Both now name `check_single_authority` and
  `check_restated_tier_policy`, what each one catches, and where each stops:
  literal substrings for the first, so it sees paste and only paste; stage-number
  shape for the second, so a reworded per-stage list is caught and the claim
  rules, which have no stage numbers, are not; and neither reads `README.md` or
  `AGENTS.md`, so a copy in either page is invisible to both.
- Added `examples/`: one filled-in LEAN project -- contract, change record and a
  `docs/workflow/` state directory the status script exits 0 on. The templates
  had only ever been shown as fragments inside prose, so a first user assembled
  a state directory out of separate excerpts and learned which parts were wrong
  from the gate. `tests/test_examples.py` runs the CLI against it, so the
  example cannot quietly fall behind the templates it demonstrates. The README
  sends readers there to see all four values the backlog's assignment column
  takes, and the example showed three: `dropped` was missing, and it is the
  value most easily handled by deleting the row instead -- which the script
  accepts, and which shortens the ledger by exactly the promise someone decided
  not to keep. The row is there now, and each README snippet is checked line by
  line against the file it says it was cut from, so the page and the example
  cannot drift apart again unnoticed.
- Rewrote `AGENTS.md`. It described a repository that was still going to produce
  a skill: a `<skill-name>/` tree that does not exist here, a source manual
  (`通用开发工作流-v3.8-环节拆分版.md`) deleted several versions ago, and a Skill
  Creator validator to run "after a skill folder exists". Anyone following it
  went looking for files that are not in the checkout. It now describes the tree
  that is here, separates the two scripts by what each validates and what
  `--root` means for each -- the checker defaults to its own directory, the
  status script has to be pointed at a consuming project -- names the three test
  files and what each one covers, and lists what has to be true before a commit.
- Rewrote the README around the lifecycle map and how the workflow is actually
  used. It explained the workflow to a reader already persuaded by it and never
  said how to install the skill, what to type to start, what appears inside your
  own project, or what a filled-in state file looks like -- so the four things a
  first user needs were the four the page left them to guess. The main line was
  a text block, and a text block cannot show the LEAN branch and where it
  rejoins, the conditional load of `05a-mechanisms-and-contracts.md`, the
  `delivery_target` decision that sends a finished slice to release or back to
  claim the next one, or the loop from retrospective into the next slice; it is
  a rendered diagram now. The page also gained the three layers of "done" with
  the accepted and rejected evidence forms side by side and the callable
  surface per project shape, so a frontend-only or split project can see itself
  in it, and turned the routing, tier and return rules into tables that link to
  the reference owning each one instead of restating it.
- Then reworked that README's install, verification and reference sections.
  `Copy-Item -Recurse general-workflow <dest>` and `cp -r general-workflow <dest>`
  copy the source *into* an existing target, so anyone reinstalling over a
  previous version ended up with a nested `general-workflow/general-workflow` and
  a skill directory that no longer loaded; both blocks now remove the target
  first. The bash block also needed `mkdir -p ~/.claude/skills`, because the two
  commands are not equivalent: `Copy-Item -Recurse` creates the missing parent
  and `cp -r` does not, so on a machine where `~/.claude/skills` did not exist
  yet the documented install exited 1 with nothing copied. The rest of the page
  had drifted the same way -- it printed its own copy of the LEAN reduction
  list, showed a `project.md` with no `state_version` and no `next_action`,
  described the status gate's rejections as they stood two releases ago, and
  drew a repository tree with no `AGENTS.md`, no `examples/` and a single test
  file. A reader trusting it built state that the gate then refused. The tier
  table now points at the single authority instead of copying it, the install
  check prints the two exact lines a working install produces, and the
  validation section splits the two scripts by what they check, what `--root`
  means for each, and where the checks stop.
- Ignored `.claude/settings.local.json`. It is per-machine editor state; it was
  neither tracked nor ignored by the repository, so it showed up as untracked
  noise for anyone whose global ignore file does not already cover it.

## 1.7.0 - 2026-09-09

Made preliminary completion mean a real call was made, not that an agent read
the code and concluded it looked right.

- A row reaches `delivered` only when someone actually invoked the real
  entrypoint and recorded what came back. Reading the diff does not qualify,
  and neither does a green test run on its own: a passing test proves an
  assertion held, not that the entrypoint can be called and returns what the
  acceptance row promises. Stage 9's per-A-ID gate now leads with that
  requirement and names the callable surface for each shape -- HTTP/RPC routes,
  CLI and scheduled entrypoints, a real page route or mount for a frontend, and
  both sides plus one crossing call when they are split.
- `evidence` is written as `<invocation> -> <observed result> @ <commit>`, and
  the status script rejects a value with nothing on one side of the arrow. A
  bare command, a bare CI link, and "the code is finished" all fail now.
  Existing projects must rewrite their delivered rows in this shape.
- Stage 8 records the call at Green rather than reconstructing it later, and
  stage 6 asks the scaffold to leave one repeatable way to invoke the real
  entrypoint and see the result -- without it every acceptance row reinvents
  the call and the habit degrades into "just run the tests".

## 1.6.0 - 2026-09-08

Closed the review findings that let a project report completion it had not
reached, and the ones that made the concurrency guard pass while two people
held the same paths.

- Split stage 9's Definition of Done into "a single A-ID may be marked
  delivered" and "this batch may enter stage 10". They were one batch-scoped
  list, so marking one acceptance id required evidence for all of them plus
  artifact traceability and a rollback checklist -- questions a single behavior
  cannot answer. The ledger rule in the handoff reference now points at the
  first section.
- `delivery_target` gains an endpoint: `implementation-and-tests`,
  `release-ready` or `deployed:<env>`. It is written in the goal contract and
  the LEAN one-pager as `delivery_endpoint`, and the status script now requires
  the field before it will report scope completion. It was previously reported
  and never checked, so a project whose user asked for a release could close out
  after stage 9 with the gate green.
- Empty-value markers are recognized in both languages the templates are written
  in. `无`, `待补`, `TODO`, `—` and `pending` were all accepted as an evidence
  pointer, which made `scope_complete=true` reachable with no evidence at all.
- `deferred` and `dropped` now need a note that actually points somewhere -- an
  id such as C-03, a path, or a link. "以后再说" satisfied the old check, so a
  backlog could be emptied into terminal states and still report complete. The
  change record's shape, C-ID numbering and home file are now defined in stage 3
  and registered in the state's authoritative sources; the LEAN one-pager points
  at that definition instead of being the only place it existed.
- Fields are read from the slice header only, above the first `##`. A handover
  note in Blockers reading `- owner: waiting on carol` used to win over the real
  owner field, which silently disabled the one-live-slice-per-owner check. Code
  fences are skipped, and a field set twice is an error rather than
  last-one-wins.
- `write_scope` is validated before it is split. The unedited placeholder
  contains the separators it documents, so splitting first turned one rejected
  value into fragments that each passed as a plausible path and overlapped with
  nobody.
- A slice is in flight from the moment it has an owner, not from its first
  `in-slice` row. Claiming happens before acceptance rows are written, so a
  fresh claim was invisible to owner uniqueness, claim dates and scope overlap.
  A slice whose rows are all delivered still releases its paths.
- Added release and mid-flight scope adjustment to the claim rules. Stage 7
  tells an agent to abandon a slice whose architecture hypothesis failed, but
  nothing said how to give one back, so the obvious move looked like the
  "delete rows to look finished" anti-pattern.
- The slice file has one format. Stage 7's slice map used the same heading as
  the state file's slice template with a different set of fields; a file written
  from stage 7 failed the status gate with an error that pointed at the backlog.
  The map is now a `## Slice map` section inside that file, and owner, claimed
  and write_scope joined the Slice Ready gate.
- `H-ID` is created in stage 5's architecture validation plan. Three stages
  consumed it and none produced it, so slices invented a hypothesis nobody had
  approved. Stage 4's risk table header now matches its own example (`K-ID`).
- Renamed the profile's fields to the ones the state file and the script
  actually read: `lifecycle` for the lifecycle state, `maintenance_horizon` for
  the maintenance dimension, `tier` for the risk tier. `lifecycle` named two
  different things across the two documents, and `risk tier` could never match
  the field pattern, so the tier read as unknown.
- The LEAN reduction list is reachable from the router. Stages 9-11's reductions
  existed only inside the fast-path document, which a later session at stage 10
  never loads, and stage 10's Release Ready gate demanded a staging environment
  and a three-way environment split with no LEAN equivalent. Those two bullets
  are now tier-qualified and the fast path states the local equivalent.
- Stage 6's CI gate accepts a local equivalent when there is no remote or CI
  provider: commit the pipeline definition, run the same commands once in a
  clean directory, and record `ci: local-only` as an open decision. Repeatability
  was the requirement; a hosting provider was not.
- Fixed three routing rows: the LEAN row lost the fast path's entry conditions
  and outranked "we do not know whose problem this is"; the 05a row was narrower
  than the mechanism list that owns it; and nothing said whether a slice that
  passes stage 9 goes to release or back to claim the next one.
- Corrected SKILL.md's description of LEAN. Only stages 1-4 merge into one
  document; the rest keep routing and get a reduction list.
- Policy anchors are checked inside their own section, which must still have a
  body. Emptying three whole sections of the release reference while keeping
  their headings used to pass. Bare-word anchors became the table cell or
  template line that carries the rule.
- The checker now asserts `scripts/workflow_status.py` and `tests/` exist and
  that every `scripts/*.py` path mentioned in the docs resolves -- it required
  the archived scripts while the live one could be deleted with the checker
  green -- and warns at 90% of a size budget instead of only failing at 100%.
- `AGENTS.md` binds the unittest suite to changes under `scripts/` and `tests/`.
  Disabling a check in the status gate left the consistency checker green.
- Added the compatibility surface to the profile and to the P0 return triggers,
  so a project that turns out to be brownfield at stage 6 has a defined return
  path rather than a one-time question at first contact.
- Untracked `scripts/__pycache__` and added a `.gitignore`.

## 1.5.1 - 2026-09-08

Strengthened requirement coverage, verification, and handoff; closed six review
findings in completion and the status gate.

- Define completion boundaries from the original request and accepted changes in
  the existing Goal/LEAN contract before decomposition. Map every promised outcome
  to acceptance and verify the full result again at integration and closeout.
  MVP deletion analysis cannot silently defer explicit commitments; ledger
  completion does not prove that the original requirement was fully decomposed.

- Added module-scoped `AGENTS.md` guidance to slice preparation, implementation,
  and review. Read applicable instructions before editing, create local guidance
  only for distinct module rules, and update it when verified boundaries,
  entrypoints, or validation commands change. P0 returns also recheck affected guidance.
- Connected BDD scenario semantics to TDD evidence in the existing acceptance
  mapping. Review actual assertions, production wiring, test execution, and
  available Red/Green evidence without copying requirements into agent documents
  or treating a checklist as proof of passing tests.
- Added a P0 return path when decomposition exposes ambiguous intent,
  conflicting core goals, or invalid project assumptions. Resolve intent from
  existing decisions or a targeted user question, update affected contracts and
  acceptance, then revalidate the earliest affected gates. LEAN uses the same
  return path; local requirement or assertion issues stay in stages 1–4.
- Centralized completion rules in the handoff reference. Claiming all IDs no
  longer satisfies stage 7; passing stage 9 completes acceptance scope only.
  Closeout also requires the delivery target already requested by the user,
  including release and observation when those are in scope.
- Added `acceptance_source` to project state, pointing directly to the current
  version's authoritative Markdown acceptance table, with an optional exact
  heading. The gate rejects missing, extra, duplicate, or unreadable IDs instead
  of deriving the expected set from backlog. Undefined draft scope is incomplete.
- Added `delivery_target` as a pointer to the authorized handoff endpoint. Existing
  projects fill these fields from their current contract and request, preserving
  IDs and evidence. The script does not verify source authenticity or release results.
- Resolved write scopes relative to the project, including dot segments,
  existing links, and Windows case normalization. Reject unsupported globs and
  paths outside the project; require valid owners, claim dates, and write scopes
  on live slices, with at most one live slice per owner.
- Invoke the installed skill's script by absolute path with an explicit target
  `--root`. Missing partial state now fails; uninitialized projects remain usable,
  and both cases preserve JSON output and cannot report completion.
- Added consumer-project CLI regression tests for completion, source coverage,
  path conflicts, ownership, and invocation outside the skill and project folders.

## 1.5.0 - 2026-09-08

Made the workflow safe for a second person to join at any moment, which meant
sharding the state and shipping the first gate an agent cannot talk itself past.

- Split the single state file into `docs/workflow/`: `project.md` for what
  rarely changes, `backlog.md` for which slice owns each acceptance id, and one
  file per slice for the rest. A slice is the natural unit of ownership -- no
  one claims half a slice -- so status updates, the most frequent write, only
  ever touch a file with a single owner.
- Moved `stage` from the project to the slice. Two people working two slices
  are genuinely at two different stages; a shared field cannot express that,
  and merging it is not a resolution because both values are correct. This is
  a modelling fix, not a merge workaround.
- `backlog.md` records assignment only, never status, so the two never disagree.
- Added claim rules: claiming edits the file you are claiming, so it cannot
  conflict; do not take a slice whose owner has fresh evidence; check
  `write_scope` against in-flight slices before starting, because overlapping
  scopes collide in code rather than on paper; hold one slice at a time.
- Added `scripts/workflow_status.py`, shipped to projects using the workflow.
  It reports slice owners, stages, unclaimed ids and whether scope is complete,
  and exits non-zero on delivered-without-evidence, backlog/slice disagreement,
  an id in two slices, overlapping write scopes, deferred or dropped without a
  change record, and owner set without a claim date. Sharding makes it
  necessary -- "how much is still owed" no longer fits in one file -- and it is
  the only gate here that does not rely on an agent judging itself.
- Same layout for solo projects. A conditional guarantee of "anyone can join"
  is not a guarantee, and the migration would land exactly when someone is
  trying to join.

## 1.4.0 - 2026-09-07

Pulled the test-first discipline forward from implementation to requirements,
without restoring the archived obligation-set machinery that did it before.

- Stage 2 scenarios must now be written in executable shape: a concrete
  entrypoint, concrete input values, a concrete assertion, the forbidden
  effect, and the seam the assertion needs. A scenario you cannot turn into a
  failing assertion is an unfinished requirement, not a testing problem. The
  assertions are not run yet -- the scaffold arrives at stage 6 -- but they
  become stage 8's red tests unchanged.
- The seam column is the new link between requirements and module boundaries.
  Naming what a test must double is a boundary decision made against observed
  behavior rather than imagined layering.
- Stage 5 takes the union of those seams as input to module boundaries, and
  states the limit: seams fix the outer edges, domain modelling fills the
  inside. Letting acceptance tests drive internal layering produces modules
  that mirror test cases instead of domain boundaries.
- Stage 3 decides the MVP by deletion -- "remove this row; is the desired
  outcome still observable?" -- rather than by Must/Should/Could judgement,
  with security and data-integrity boundaries as the stated exception. Where
  deletion and the priority label disagree, deletion wins.
- The LEAN contract template carries the same seam column and deletion rule.

## 1.3.1 - 2026-09-07

First forward test: a LEAN internal CLI taken from profile to delivered
acceptance. Six defects surfaced; five are closed here.

- The fast-path gate required "a verification path you can run" and the ledger
  required a change record for deferred and dropped rows, but the one-page
  contract template had a field for neither. Both fields added -- a gate that
  asks for something the template cannot hold is not a gate.
- Restored the constraint-conflict check the merge had dropped. The full path
  gates on "conflicts between quality goals are explicitly recorded"; nothing
  carried it into the fast path, so the test run wrote a contract requiring
  both "never send dependency lists to third parties" and "look up known
  vulnerabilities" and no check caught it until the architecture stage. The new
  sixth minimum also requires re-checking after a resolution, because the first
  fix attempted (cutting vulnerability scanning) did not remove the conflict.
- Narrowed the fast-path entry condition from "privacy" to "personal privacy or
  regulatory compliance". Internal secrets are not by themselves an escalation
  reason, only sending them to a third party is -- the old wording would have
  pushed most internal tools onto the eleven-stage path.
- Said which gate governs after a merge: the merged stages' own gates remain
  the floor, and the fast path's boundary list is a waiver list against them.
- Defined "real entrypoint" to include calling the composition root in-process,
  so a subprocess is not mistaken for a higher standard.

Not fixed, needs a decision: a LEAN run still reads 66% of the document set
(66.6 KB of 100.5 KB), because 00-lean-path.md says what is relaxed rather than
what to do, so stages 6 through 10 still get read in full.

## 1.3.0 - 2026-09-07

A subtraction pass. Nothing was added: six places said the same thing twice,
and the fast path had only been made fast in its front half.

- Cut the return table from stage 11. The router's stage table, stage 11's own
  observation classification, and that table were three statements of one
  mapping; the classification list survives and now names files rather than
  bare stage numbers. Removed check_return_table with it -- a guard that keeps
  two copies in sync is worth less than not having two copies.
- Compressed SKILL.md's twelve principles to six. Ten of the twelve were
  restated by the stage document that owns them; what remains is what has to
  be true before you know which stage you are in.
- Replaced the six prose completion conditions in SKILL.md with the ledger
  test: no remaining and no in-slice rows. Stages 9 and 10 own the gates that
  move rows, so the entry file no longer summarizes them.
- Merged the back half of the LEAN path. It collapsed stages 1-4 but left six
  stages standing behind them; LEAN is now four steps, with the clean-clone
  check and one CI pipeline as its single non-negotiable gate.
- Cut stage 9's CI layering block (a restatement of the 运行时机 column in its
  own table), stage 8's scope firewall (owned by stage 3), and stage 5's
  decision-order list (a prose table of contents for its own sections).
- Narrowed stage 5's deployment section to the four decisions that constrain
  the data model and contracts; the execution checklist belongs to stage 10.
- Tightened the size budgets to lock the reduction in: SKILL.md 8000, any
  single reference 13000.

## 1.2.0 - 2026-09-07

Made the line past the first slice as well specified as the line up to it.
Surveyed how the highest-starred agent workflow projects track outstanding
scope -- superpowers, spec-kit, OpenSpec, BMAD-METHOD, and claude-task-master
-- and adopted the two conventions they share.

- Generalized `07-vertical-slice.md` from the first slice to every slice. The
  map and the gates are shared; only the selection weights differ, and the
  document now states that difference in a table. An architecture hypothesis of
  `none` is a legitimate result for a later slice rather than a blank to fill.
  None of the surveyed projects keeps a separate document for the first
  iteration, and neither does this one now.
- Added a scope ledger to the state file: one row per A-ID with a status of
  remaining, in-slice, delivered, deferred, or dropped, plus an evidence
  pointer. It holds identifiers and pointers only, never scenario text.
- A row reaches `delivered` only by passing the stage 9 Definition of Done with
  an evidence pointer filled in, and `delivered` is monotonic -- reopening
  scope goes through the change protocol in stage 3 rather than editing the
  ledger backwards. Both rules come from the survey: BMAD refuses status moves
  that go backwards, and OpenSpec makes delivery a move between directories so
  a status field cannot drift from reality.
- "Current scope is delivered" now has one authoritative answer: no remaining
  and no in-slice rows. Stage 11 selects the next slice from the remaining
  rows and reports what is left in its closeout.

## 1.1.1 - 2026-09-07

Closed five routing defects found while auditing the 1.1.0 branch points.

- The LEAN row in the router's stage table stated a mode ("tier is LEAN"), not
  an unmet fact, so it matched for the whole life of a LEAN project and routed
  finished work back to the project contract. It now states the deficiency, and
  the table says explicitly that satisfied rows are skipped.
- The profile gate hardcoded stage 1 as its successor, so a project whose tier
  was just set to LEAN could not reach the fast path by following the profile
  document's own gate. The gate now branches on tier.
- The retrospective's return table still sent mechanism failures to stage 5
  after mechanisms moved to 05a, and wrote "07/08" as bare numbers rather than
  resolvable links. Both fixed, plus a row for fast-path escalation.
- The state cursor was only mentioned at end of round, while stages may advance
  several at a time. Cursor advance is now part of the shared stage gate, so it
  applies at every gate rather than once per conversation.
- The fast path emitted only A-IDs while stages 5, 7, and 9 name R-ID and Q-ID
  in their entry conditions, so a LEAN project reached stage 5 against a gate it
  could never satisfy. `00-lean-path.md` now maps must entries to R-ID and
  quality_targets to Q-ID, and names the two cases that must escalate instead.
- Added check_return_table to check_consistency.py: every reference the router
  can route into must also appear in the retrospective's return table, so the
  two routing tables cannot drift apart again.

## 1.1.0 - 2026-09-06

Tuned the Greenfield main line for how it actually gets executed: less constant
cost, fewer load spikes, a real fast path, and state that survives a session
boundary. No change to the eleven-stage lifecycle or to the Greenfield-only
scope.

- Added `references/00-lean-path.md`: LEAN projects merge stages 1-4 into a
  single project contract with explicit minimums and escalation triggers, so
  the fast path is executable instead of a paragraph in the router.
- Split `references/05-architecture-design.md` (16.7 KB) into shape/boundary/
  data/stack/deployment decisions plus `05a-mechanisms-and-contracts.md` for
  auth, async, transactions, API/event contracts, and observability. The
  mechanisms file loads only when the architecture stage marks an item as
  required or risk-triggered.
- Added `references/99-state-and-handoff.md`: a cursor-and-index state file in
  the target repository, with read/verify rules on session start and update
  rules on session end. It holds pointers, never copies; repository facts win
  on conflict.
- Removed the architecture, implementation, and verification checklists that
  `SKILL.md` restated from stages 5, 8, and 9, keeping only cross-stage policy.
  The anti-fake-green rule moved into the evidence principle rather than being
  dropped.
- Routed the new entry points: the router now looks for the state file first,
  branches on path depth, and lists the mechanisms document as its own row.
- Added size budgets to `check_consistency.py` for the always-loaded entry path
  and for any single reference, so stage detail cannot drift back into
  `SKILL.md` unnoticed. Reference names may now carry a letter suffix (`05a`).

## 1.0.0 - 2026-09-04

Reframed the skill around Greenfield project delivery, using the supplied `project-dev-workflow` package as the baseline and expanding it for architecture-led development.

- Added a project-profile entry point that evaluates product shape, runtime units, data, team, lifecycle, and risk before selecting architecture depth.
- Added explicit stages for requirements/goals, scenarios/acceptance, scope/non-goals, constraints/quality attributes, architecture decisions, scaffolding/CI, vertical slicing, implementation, testing/integration, release/operations, and retrospective evolution.
- Expanded architecture guidance to cover system shape, direct layering vs modular vs hybrid organization, data ownership and invariants, authentication/authorization, asynchronous work, API/error conventions, observability, deployment, migration, and rollback.
- Made the first vertical slice an architecture-validation path rather than only a feature list.
- Kept behavior-sized red/green/refactor, layered testing, CI/CD, migration, secrets, monitoring, and rollback guidance from the reference package.
- Archived the previous feature/change-oriented workflow under `archive/general-workflow-v0.12.0/`; archived material is reference-only.
- Replaced the old consistency checks with checks for the Greenfield stage graph, reference reachability, architecture decision coverage, release/operations coverage, and archive separation.
