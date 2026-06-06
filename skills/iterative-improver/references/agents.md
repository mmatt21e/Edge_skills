# Subagent Prompts & Scoring Protocol

The refine loop uses two **separate** subagents each round. Keeping them separate
matters: a critic that just wrote the improvement will rationalize it; a fresh
critic judges honestly. Spawn them with the Agent/Task tool.

## Improver agent

Give it everything it needs to make one strong pass — and nothing that biases it
toward trivial edits. Template:

```
You are improving a <target type>. Goal: <improvement goal from Phase 1>.

CURRENT BEST VERSION:
<the current best artifact, or its location for code>

RUBRIC (optimize for the weighted total):
<the full rubric with weights and anchors>

RESEARCH NOTES (what excellent looks like here):
<the Phase-2 principles>

WEAKNESSES TO ADDRESS THIS ROUND (from the critic; empty on round 1):
<ranked critic feedback>

CONSTRAINTS YOU MUST NOT BREAK:
<behavior/API/voice/format/length/factual constraints from Phase 1>

Produce a full improved version. Prioritize the highest-impact weaknesses and the
highest-weighted criteria. Make real, substantive improvements — not cosmetic
tweaks — but never sacrifice one criterion to game another, and never violate the
constraints. For code, make the edits in the working copy/branch and ensure it
still builds. Return the complete improved artifact (or the list of files you
changed) plus a 2–3 line note on what you changed and why.
```

## Critic agent

```
You are critically evaluating a <target type> against a fixed rubric. Be a tough,
fair judge — your job is to find what still holds it back, not to praise it.

CANDIDATE (new version):
<the improver's output / changed files>

PREVIOUS BEST (for reference):
<prior best>

RUBRIC:
<the full rubric with weights and anchors>

For each criterion, give a 0–10 score justified by specific evidence from the
candidate (quote or cite lines). Compute the weighted total on a 0–100 scale.
Then list the most impactful remaining weaknesses, ranked, each with a concrete
suggestion. For any verifiable criterion (builds, tests pass, word count, links),
actually check it and report the result — don't guess.

Return JSON exactly in this shape:
{
  "scores": [
    {"criterion": "Correctness", "score": 8, "weight": 0.30, "evidence": "..."}
  ],
  "weighted_total": 74,
  "weaknesses": [
    {"issue": "...", "impact": "high", "suggestion": "..."}
  ],
  "verifiable_checks": [
    {"check": "tests pass", "result": "pass/fail", "detail": "..."}
  ]
}
```

## Driving the loop

- **Consistency:** keep the rubric text byte-identical across rounds, and pass the
  previous best to the critic so scores stay comparable. If you suspect scoring
  drift, have the critic re-score the previous best in the same call and compare
  relatively.
- **Best-so-far:** compare `weighted_total` to the running best. Higher (or equal)
  → promote to best. Lower → discard the candidate's content but keep its
  `weaknesses` to inform the next improver pass.
- **Per-round report to the user:** one compact block — round number, score and
  delta vs. baseline, top 1–2 changes, and a short diff. Don't dump full outputs
  every round.
- **Cost/time:** the loop is inherently sequential (each round depends on the
  last). If a single improver pass is weak for a hard target, it's fine to spawn
  2–3 improvers in parallel for that round and let the critic pick the best — a
  tournament fallback within the refine structure.
