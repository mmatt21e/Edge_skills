# Building a Measurable Criteria Rubric

A good rubric is what turns "make it better" into something a loop can actually
optimize. Without it, the improver chases vibes and the critic's scores drift.

## Principles

- **3–7 criteria.** Fewer can't capture quality; more dilutes focus and makes
  scoring noisy.
- **Weighted.** Not all criteria matter equally — weight them to sum to 100%, and
  let the user's stated goal pull the weights (e.g. "make it faster" → performance
  gets the most weight).
- **0–10 scale with anchors.** For each criterion, describe what a ~2 (poor),
  ~5 (adequate), and ~9 (excellent) looks like *for this specific target*. Anchors
  are what keep the critic consistent across rounds.
- **Prefer verifiable over subjective.** Whenever a criterion can be checked
  mechanically (it compiles, tests pass, word count under limit, no broken
  links, reading-grade level), say how to check it. Mix these with judgment
  criteria; don't pretend everything is objective.
- **Derive from research, not a template.** The Phase-2 research notes should
  directly inform the criteria so they're specific to the domain.

## Scoring

Weighted total = Σ(criterion_score × weight). Report it on a 0–100 scale so
progress across rounds is easy to read. Keep the rubric **fixed** for the whole
run — changing it mid-loop makes scores incomparable.

## Starting points by target type

Adapt these; don't use them verbatim.

**Code**
- Correctness (verifiable: builds, tests pass) — usually highest weight
- Performance (complexity, allocations, queries) — weight by goal
- Readability / maintainability (naming, structure, comments where needed)
- Robustness (error handling, edge cases, input validation)
- Consistency with the surrounding codebase's conventions

**Prose / docs**
- Clarity (a reader gets it on first pass)
- Structure / flow (logical order, good headings)
- Concision (no filler; verifiable-ish via word count vs. information)
- Correctness / accuracy (claims supported; nothing invented)
- Audience fit / tone

**Prompt (for an LLM)**
- Task clarity and unambiguous success criteria
- Robustness across inputs / edge cases
- Output-format specification
- Concision (no contradictory or dead instructions)
- Triggering/scoping (does it fire when it should and not otherwise)

**Design described in text / UX copy**
- Goal achievement (does it serve the user's job)
- Clarity & hierarchy
- Consistency
- Accessibility considerations

**Data analysis / report**
- Correctness of method
- Insightfulness (non-obvious, actionable findings)
- Clarity of presentation
- Reproducibility / transparency of assumptions

Whatever the type, write the anchors in concrete terms tied to the actual target
so a different agent scoring the same artifact would land on a similar number.
