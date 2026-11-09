---
name: mynrd-verified
description: Record the user's own verification of a mynrd-flow build in progress.json. Use only when the user requests recording their completed human check, never merely because tests passed.
---

# mynrd-verified

In Codex, first read [the runtime adapter](../../adapters/codex.md), then follow [the shared verification workflow](../../commands/mynrd-verified.md) with those translations. In Claude Code, follow the shared command natively.

Read [the progress schema](../../PROGRESS-SCHEMA.md). Preserve all gates and fields owned by other stages. An ambiguous folder needs clarification; unfinished work is refused. This records the user's verdict and does not perform verification itself.
