# Help Index - mynrd-flow

This is the table of contents that `/mynrd-help` reads first. Every entry maps a topic to a file in `.help/`.

**For the model running `/mynrd-help`:** read this file first. Match the user's question against the topics below. Load the matching file(s). Synthesize a focused answer. If the question isn't covered by any topic file, say so directly - **never guess**. Offer to add it to the relevant `.help/` file.

---

## Topics

| Topic | File | When to load |
|---|---|---|
| First-time orientation, install, "what is this", "where do I start" | [getting-started.md](getting-started.md) | The user is new and asks for a tour, how to install, or what to do first |
| Project setup, permission prompts, `settings.local.json`, `CLAUDE.local.md` | [commands.md](commands.md) (`/mynrd-init`) | The user asks how to set a project up, why dispatch keeps prompting, or what the rules block is |
| What a specific command does, its arguments, its behavior | [commands.md](commands.md) | The user asks about a specific `/mynrd-*` command or how to pick one |
| The end-to-end sequence: which stage am I in, what comes next | [workflow.md](workflow.md) | The user asks how the flow fits together, what to do after a stage, or why a build was refused |
| `.work/<date>-<slug>/`, `progress.json` - what it holds, who writes it, what the statuses mean | [progress.md](progress.md) | The user asks about the state file, `implemented` vs `pass`, where the build loop's state lives, or why a step says `skipped` |
| Starting on something that just came in | [commands.md](commands.md) (`/mynrd-plan`) + [workflow.md](workflow.md) | The user asks where to start with a new request |
| The build loop, specialist agents, test tiers, blocked ACs | [commands.md](commands.md) (`/mynrd-dispatch`) + [progress.md](progress.md) | The user asks what `/mynrd-dispatch` runs, which agent handles what, or why an AC is blocked |
| Common questions, "how do I X" | [faq.md](faq.md) | The user has a procedural question that isn't covered elsewhere |
| Errors, refusals, what they mean, how to fix | [troubleshooting.md](troubleshooting.md) | The user hit an error or a refusal and wants to know what happened |
| Definitions: AC, brief, dispatch loop, evidence, etc. | [glossary.md](glossary.md) | The user asks "what does X mean" for a plugin-specific term |

---

## How `/mynrd-help` should answer

1. **Load this INDEX first.** Identify which topic file(s) match the user's question. It's fine to load multiple if the question spans them.
2. **Quote or paraphrase from the loaded files.** Don't fabricate answers. If a file partially answers but has gaps, note the gaps explicitly.
3. **Never guess at command behavior or workflow rules.** If the answer isn't in `.help/`, say:
   > That's not covered in the help docs yet. The authoritative source is the command file itself under `commands/`. Want me to look there?
4. **Offer to extend `.help/`.** If the user's question is reasonable and the answer ISN'T in the help docs but IS findable in the command files, offer to add the new content to the relevant `.help/` file - but only with the user's confirmation. Updating `.help/` is a documentation change, not a workflow action.
5. **Be direct.** No fluff, no "great question," no closing recap. Answer and stop.

---

## What `/mynrd-help` does NOT do

- Does **not** invoke any other slash command. It can describe what `/mynrd-dispatch` does; it cannot run it for the user.
- Does **not** edit source files, run tests, or touch `.work/`. Help content lives in markdown files, period.
- Does **not** modify `.help/` files unilaterally. Updates require user confirmation per § "How `/mynrd-help` should answer" above.
