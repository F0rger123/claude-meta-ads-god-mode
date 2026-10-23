# Workflow: client onboarding

Trigger: `/ads:onboard <client>` or "Add D-Hauss Remodeling as a new ads client." Skill: [ads-client-onboarding](../skills/ads-client-onboarding/SKILL.md).

1. `adsgm resolve "<name>"` - if it already exists, switch to "update profile" and show current values.
2. Ask the 7 question groups from the skill, 3-5 questions per message. Accept "skip" and record unknowns as empty, not guesses.
3. Verify every account id with a read and confirm the account name with the user.
4. Suggest targets from economics when missing (show math, label HEURISTIC).
5. Recommend automation mode: `approval` (default) or `draft`. Explain `guarded_auto` limits if they ask for automation; never suggest `full_auto`.
6. `adsgm clients new <slug>` -> fill -> `adsgm clients validate` -> `adsgm clients check-isolation` -> `adsgm use <slug>`.
7. Summary + gaps + recommended first action (usually `/ads:tracking` then `/ads:audit`).

Done when: profile validates, isolation check passes, every account id was verified by a read in this session.
