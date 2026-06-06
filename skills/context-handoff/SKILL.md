---
name: context-handoff
description: Capture the current conversation into a persistent handoff file and produce a ready-to-paste restart prompt, so the session can be cleared or restarted without losing context. Use when the context window is getting full, before running /clear or /compact, or when the user asks to checkpoint, save, hand off, or "capture and restart" the conversation.
---

# context-handoff

A skill cannot clear its own context window — that's a harness action. What it
*can* do is preserve everything needed to continue, so a `/clear` or session
restart loses nothing. This skill writes a structured handoff to
`.claude/handoff.md` and then hands back a restart prompt to paste into the
fresh session.

## When to use

- The context window is filling up and you want to clear and continue cleanly.
- Before `/clear` or `/compact`, to checkpoint the work.
- "Save the context / hand this off / capture and restart."

## Steps

1. **Gather objective state** with a single batch of commands (don't rely on
   memory for these):

   ```bash
   git branch --show-current
   git status --short
   git log --oneline -5
   git diff --stat
   ```

2. **Ensure the file won't be committed by accident.** Create `.claude/` if
   needed, and make sure `.claude/handoff.md` is in the project's `.gitignore`
   (add the line if missing).

3. **Write `.claude/handoff.md`** using the template below. Fill every section
   from the actual conversation and the git output — be specific and concrete.
   Favor facts a fresh session would otherwise have to re-derive (exact file
   paths, decisions already settled, the precise next action). Omit a section
   only if it is genuinely empty.

4. **Print the restart prompt** (see "Output" below) in a code block so the user
   can copy it. Tell them the sequence plainly: *run `/clear`, then paste this.*

5. **Do not** run `/clear` yourself or commit the handoff — leave both to the
   user.

## Handoff file template

```markdown
# Session Handoff — <YYYY-MM-DD HH:MM>

## Goal
<The overall objective in 1–3 sentences. What "done" looks like.>

## Status / progress
<Where things stand right now. What's finished vs. in progress.>

## Decisions & rationale
- <Decision> — <why, so it isn't relitigated>

## Files & git state
- Branch: <branch>   | Last commit: <hash + subject>
- Modified/created:
  - `path/to/file` — <what changed and why>
- Uncommitted changes: <yes/no + summary>

## Commands & results
- `<command>` → <outcome, e.g. tests pass, build green, error X>

## Open questions / blockers
- <Unresolved question or thing waiting on the user>

## Next steps
1. <The very next concrete action to take>
2. <Then…>
```

## Output (restart prompt to give the user)

Print exactly this, filled in:

```
Resume the previous session. First read .claude/handoff.md for full context,
then briefly confirm the goal and the next step in one line — and continue with:
<the single most important next action from the handoff>.
```

Keep the handoff **lean but complete**: a fresh session should be able to
continue confidently from it alone, without the prior transcript.
