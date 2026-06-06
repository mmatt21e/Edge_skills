---
name: iterative-improver
description: Improve, optimize, refine, or polish anything you point it at — code, writing, docs, a prompt, a design described in text, a config, a resume — by running an autonomous multi-agent refinement loop. Use this whenever the user wants to make something meaningfully better, iterate on quality, run N rounds of improvement, or says things like "improve this", "make X better", "keep refining this until it's great", or "run 5 improvement passes on Y". It first evaluates the target, researches what excellent looks like, builds a measurable criteria rubric with a baseline score, then loops an improver agent and a critic agent for the number of iterations requested, keeping the best version each round and showing a diff and score after every pass. Works on a copy or git branch so the original is never lost.
---

# Iterative Improver

A general-purpose, autonomous improvement engine. Point it at almost anything and
tell it how many rounds to run; it figures out what "better" means for that thing
and drives toward it with a two-agent refine loop (an **improver** that rewrites
and a **critic** that scores and finds the next weaknesses).

It runs **end-to-end without pausing** once started — the safety net is that all
work happens on a copy or branch, the best version is kept every round (it can
never regress), and you see a diff + score after each pass.

## Inputs

- **Target** — what to improve (a file, a folder, a code module, a document, a
  block of text the user pasted, a prompt, etc.).
- **Iterations (N)** — how many refine rounds to run. If the user gave a number,
  use it. If not, ask once for the count (a sensible default is 3), then proceed
  autonomously.
- **Goal (optional)** — what the user cares about most ("make it faster", "make
  it persuasive", "tighten it up"). If absent, infer it in Phase 1.

This skill relies on spawning subagents (the Agent/Task tool). The improver and
critic must be **separate agents** so the critic judges with fresh eyes rather
than defending its own work.

---

## Phase 1 — Evaluate the target

Understand what you're improving before changing anything.

- Identify the **type** (code / prose / prompt / config / design-in-text / data
  analysis / mixed) — this drives the rubric and the agent instructions.
- Read it fully. Summarize its current purpose, audience, and the goal of
  improvement (use the user's stated goal, or infer it and state your inference).
- Note constraints to preserve: behavior, API, voice, length limits, format,
  factual content. Improvement must not silently break these.

## Phase 2 — Research what "excellent" looks like

Don't improve from intuition alone. Gather what distinguishes great examples of
this kind of thing:

- For well-known domains, recall established best practices; for anything where
  current/external knowledge helps (libraries, standards, style guides,
  competitor examples), **use web search** or spawn a research subagent.
- Capture 5–10 concrete, target-specific principles (not generic platitudes) as
  short research notes. These feed both the rubric and the improver.

## Phase 3 — Build the criteria rubric + baseline

Turn "better" into something measurable. Read `references/rubrics.md` for how to
build a good rubric for the detected target type.

- Produce **3–7 weighted criteria**, each with a 0–10 scale and a concrete
  description of what a low / mid / high score looks like. Favor objective,
  verifiable criteria; for code, include criteria you can *check* (it builds,
  tests pass) alongside judgment ones.
- Score the **original** against the rubric to get the **baseline**. Show the
  user the rubric and baseline score, then continue (no approval gate).

## Phase 4 — The refine loop

**Set up a safe workspace first:**
- Code in a git repo → create a branch: `git switch -c improve/<name>-<timestamp>`.
- Otherwise → copy the target into `.improve/<name>/` and keep iteration
  snapshots there. Track `best/` (current best) and the running best score.

Then for each round `i` from 1 to N, read `references/agents.md` for the exact
subagent prompts and scoring format, and run:

1. **Improver agent** — give it the current best version, the rubric, the
   research notes, and the critic's weaknesses from the previous round (none on
   round 1). It returns a full improved version, addressing the weaknesses
   without violating the preserve-constraints from Phase 1.

2. **Critic agent** — give it the new candidate and the rubric (and the previous
   best for reference). It returns a per-criterion score, a weighted total, and a
   ranked list of the most impactful remaining weaknesses. It scores against the
   rubric, not vibes. For code, it (or you) actually runs the build/tests and
   feeds the result into the verifiable criteria.

3. **Keep best-so-far.** If the candidate's score ≥ current best, it becomes the
   new best. If it's lower, keep the previous best as the baseline for the next
   round (no regression) but still carry the critic's weaknesses forward.

4. **Report the round**: score, delta vs. baseline, and a short diff of what
   changed. Keep these tight — one compact summary per round.

5. Feed the critic's weaknesses into the next round's improver. Repeat.

Run all N rounds the user asked for. (You may note when scores have clearly
plateaued, but don't stop early unless the user set a stop-on-plateau rule.)

## Phase 5 — Finalize

- Apply the **best** version to the real target: merge/keep the branch for code,
  or write `best/` back over the original for files. State exactly what changed
  and how to revert (the branch name or the backup copy).
- Report the **score trajectory** (baseline → each round → final), the final diff
  vs. the original, and a brief note on what drove the biggest gains.

---

## References

- `references/rubrics.md` — building measurable criteria per target type.
- `references/agents.md` — improver & critic subagent prompt templates + the
  scoring JSON the loop expects.

## Guardrails

- Never modify the original in place during the loop — always a copy or branch;
  apply the best result only at the end, reversibly.
- Keep best-so-far so a bad round can never make things worse.
- Improver and critic are separate agents; the critic scores against the rubric.
- Preserve the constraints captured in Phase 1 (behavior, voice, format, facts) —
  improving one criterion must not silently break another.
