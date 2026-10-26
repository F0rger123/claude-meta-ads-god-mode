# Workflow: learning loop

Trigger: `/ads:learn [client]`, weekly sweeps, "what's working for this client", "did that change work".

```
plan a change ──► predict (metric, direction, baseline, read date, tags)
      │                                   │
  approve + apply                    read date passes
      │                                   ▼
      └──────────────► snapshot ──► judge: worked / failed / inconclusive
                                          │
                                   lessons by tactic tag
                                          │
                              next recommendations for this client
```

1. **Predict at plan time.** Every `adsgm plan` for a meaningful change adds `--predict-metric --predict-direction --baseline --baseline-n --read-after --tags`. Tags name the tactic, reusable across clients:
   - `budget-up-20`, `budget-down`, `negatives`, `pause-loser`
   - `ugc-hook`, `offer-card`, `free-consult-offer`
   - `broad-match`, `advantage-audience`, `geo-tighten`
2. **Read at the read date.** `adsgm learn due` lists what's ready. `adsgm learn auto --client X` judges from the latest snapshot. If the metric isn't in the snapshot, read it and `adsgm learn record --client X --prediction prd_... --value V --n N`. Changes that were never applied record `--not-executed`.
3. **Grade honestly.** Under 10 results, or a move within noise (±100/√n %), counts as inconclusive. Say so instead of claiming a win.
4. **Capture other lessons.** Creative test readouts, landing-page changes, offer changes: `adsgm learn lesson --client X --tags ... --verdict ... --text ...`.
5. **Use the lessons.** Run `adsgm learn summary --client X` before recommendations:
   - "Worked" tactics with MODERATE/HIGH confidence go first in the next plan.
   - "Failed" tactics need a new hypothesis before being tried again.
   - Proposals about limits (e.g. budget steps) go to the human. Never edit limits yourself.
6. **Share across clients only as a heuristic.** `adsgm learn summary --portfolio` shows tactic win rates across clients, without moving any client's data into another client's work.
