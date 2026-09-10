---
name: mynrd-refine
description: Refine a discussion thread into a formatted draft — Description/AC for work, Repro Steps/AC for a bug. Local only — output goes to the terminal, or to DRAFT.md in an existing `.work/` folder if you say so.
---

# /mynrd-refine

Take the current conversation (draft / discussion / planning / review) and synthesize it into a clean, formatted draft using the templates below.

This command does **not** create or update anything outside the local work folder. The output is for the user to review. Once they're happy, they'll typically take the draft into `/mynrd-plan`.

---

## What to do

1. Decide the shape from the discussion and say it in one line: a defect gets the **Bug** format, anything else gets the **Description** format. Don't ask.
2. Read back through the conversation and extract: the goal, scope, decisions made, open questions, and any concrete requirements / repro details.
3. Produce the draft using the matching format (below). Output the draft inline, clearly labeled. If a `.work/<YYYY-MM-DD>-<slug>/` folder already exists for this thread, offer to save the draft there as `DRAFT.md`.
4. Stop. Don't ask for approval, don't call any other tool. The user decides what to do next — usually `/mynrd-plan` to turn the draft into a plan.

---

## Format — Description (non-bug work)

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

## Format — Acceptance Criteria (both)

Checkbox list, one criterion per line. Each item must be verifiable by a reviewer without asking the author.

```markdown
- [ ] <observable, testable condition>
- [ ] ...
```
