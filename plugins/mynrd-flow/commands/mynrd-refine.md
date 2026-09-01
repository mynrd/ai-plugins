---
name: mynrd-refine
description: Refine a discussion thread into a formatted draft — Description/AC (Story, Task) or Repro Steps/AC (Bug). Local only — output goes to the terminal or the `.work/<slug>/` folder.
---

# /mynrd-refine

Take the current conversation (draft / discussion / planning / review) and synthesize it into a clean, formatted draft using the templates below.

This command does **not** create or update anything outside the local work folder. The output is for the user to review. Once they're happy, they'll typically take the draft into `/mynrd-plan`.

---

## What to do

1. Ask the user which type to refine for: **User Story**, **Task**, or **Bug**. If it's already obvious from the discussion, state your inference and ask them to confirm.
2. Read back through the conversation and extract: the goal, scope, decisions made, open questions, and any concrete requirements / repro details.
3. Produce the draft using the format for the chosen type (below). Output the draft inline, clearly labeled. If a `.work/<slug>/` folder already exists for this thread, offer to save the draft there as `.work/<slug>/DRAFT.md`.
4. Stop. Don't ask for approval, don't call any other tool. The user decides what to do next — usually `/mynrd-plan` to turn the draft into a plan.

---

## Format — Description (User Story / Task)

- Short context paragraph (what + why)
- Bullet list of scope / behavior
- Out-of-scope bullets if relevant
- Links or references at the bottom

## Format — Repro Steps (Bug)

1. Numbered list of exact steps
2. ...

**Expected:** _what should happen_
**Actual:** _what happens_
**Environment / build:** _if known_

## Format — Acceptance Criteria (all types)

Checkbox list, one criterion per line. Each item must be verifiable by a reviewer without asking the author.

```markdown
- [ ] <observable, testable condition>
- [ ] ...
```
