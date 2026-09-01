---
name: mynrd-help
description: Conversational help — answers questions about how to use this plugin, grounded in the .help/ knowledge base. No guessing.
---

# /mynrd-help

Answers the user's questions about how to use this plugin. Reads grounded knowledge from the `.help/` files at `${CLAUDE_PLUGIN_ROOT}/.help/`; never fabricates answers.

**Read-only.** No writes outside `.help/`, no side effects. This command does not invoke other slash commands either — it explains them.

---

## Argument

None. `$ARGUMENTS` is ignored if present.

If the user typed something after `/mynrd-help` (e.g. `/mynrd-help how do I refine a bug?`), treat that text as their opening question and skip Step 1's "what do you need help with" prompt. Go straight to Step 2.

---

## Step 1 — Open the conversation

Print this short intro:

> **`/mynrd-help` — what do you need to know?**
>
> I can help with: command reference, the intake → plan → dispatch workflow, the `.work/<slug>/` folder and `progress.json`, common errors, terminology, or general orientation. Ask anything.
>
> If you're not sure where to start, type `start` and I'll give you a tour of the workflow.

Wait for the user's question.

---

## Step 2 — Load the index and route

When the user asks anything (or pasted their question as `$ARGUMENTS`):

1. **Read `${CLAUDE_PLUGIN_ROOT}/.help/INDEX.md`** first. It lists every topic file in `.help/` and what each one covers. The full set is: `INDEX.md`, `getting-started.md`, `commands.md`, `workflow.md`, `progress.md`, `faq.md`, `glossary.md`, `troubleshooting.md`.
2. **Identify which topic file(s) match the user's question.** It's fine to load multiple if the question spans them. Examples:
   - "How do I refine a bug draft?" → load `.help/commands.md` (for the `/mynrd-refine` Bug path) AND `.help/workflow.md` (for where refining fits in the flow).
   - "What goes in `progress.json`?" → load `.help/progress.md`.
   - "I'm new — where do I start?" → load `.help/getting-started.md`.
   - "`/mynrd-dispatch` errored" → load `.help/troubleshooting.md` AND `.help/commands.md`.
3. **Read the matched files using the Read tool.** Don't paraphrase from memory — the files are the source of truth, and they're versioned in the repo.

---

## Step 3 — Synthesize the answer

Once you have the relevant `.help/` content loaded:

1. **Answer the user's specific question.** Quote or paraphrase from the loaded files. Cite the file (e.g. "Per `.help/progress.md` → status values, ...").
2. **Be focused.** Don't dump the entire file at the user. Pull the relevant section.
3. **Use code blocks for examples.** Slash commands, file paths, error messages — all in inline code or fenced blocks.
4. **End with one of these:**
   - If the user might want more depth: a single pointer to "for more, see `.help/<file>.md` or `<other-source>`."
   - If the question is fully answered: just stop. No closing recap.

---

## Step 4 — Handle gaps

If the user's question **isn't covered** in any `.help/` file:

1. Tell them directly:
   > That's not covered in the help docs yet. The authoritative sources are:
   > - `${CLAUDE_PLUGIN_ROOT}/commands/<command-name>.md` (the command's own step-by-step flow)
   > - `${CLAUDE_PLUGIN_ROOT}/agents/<agent-name>.md` (what each specialist agent does)
   >
   > Want me to look there?

2. If the user says yes, **read those files** and answer from them. Cite the source.

3. If the answer IS in those authoritative sources and IS reasonable to add to the help docs, offer:
   > This would be useful in `.help/<file>.md`. Want me to add it?

4. **Only update `.help/` files with the user's explicit confirmation.** Use the Edit tool to add the new content to the matching file. `.help/` edits are still a documentation change worth doing carefully.

---

## Step 5 — Handle out-of-scope questions

If the user asks something this command shouldn't answer:

### Question about the state of a specific piece of work

> "What's left to do on the login-form work?"
> "Which ACs passed last dispatch?"

These need the actual work folder, not help docs. Redirect:

> That's the state of a specific work folder, not a help-doc question. Open `.work/<slug>/progress.json` (or `PLAN.md`) — that's where `/mynrd-dispatch` records every AC and test case.

### Question that needs the user to invoke another command

> "Can you refine this into a bug for me?"

`/mynrd-help` can describe how `/mynrd-refine` works, but it doesn't invoke other commands. Redirect:

> I can explain how `/mynrd-refine` works (see `.help/commands.md`) or `/mynrd-plan` (the discussion-first planning flow). To actually produce the draft, you'd run that command directly — `/mynrd-help` doesn't invoke other commands.

### Question that requires checking actual code or current state

> "Is `/mynrd-dispatch` picking up my plan?"

Help docs describe behavior; they don't debug current state. Suggest:

> That's a runtime check, not a help-doc question. Try running the command and inspecting the result. If something's wrong, `/mynrd-help troubleshooting <error message>` can help interpret errors.

---

## Step 6 — Closing

After answering, don't ask "anything else?" or add a recap. Just stop. If the user has more questions, they'll ask.

---

## What `/mynrd-help` NEVER does

- Invokes another slash command
- Modifies any file outside `.help/`
- Modifies a `.help/` file without the user's explicit confirmation
- Guesses at command behavior, file names, or workflow rules — if it's not in the loaded files, the command says so
- Answers questions about the state of a specific work folder (read `.work/<slug>/progress.json` for that)
