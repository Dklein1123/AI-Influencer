# Sierra Calendar — week of 2026-05-11

_Trend pulse: 2026-05-07 · 4-bit rotation · slop pre-flight clean_

| # | Day | Date | Bit | Template | Status | Tag line |
|---|---|---|---|---|---|---|
| 1 | Monday | 2026-05-11 | 📖 sierra_reads | P32 | ✅ READY | I am SO decentered. |
| 2 | Tuesday | 2026-05-12 | 🙏 sierra_apologist | P25 | ✅ READY | Try that once. |
| 3 | Wednesday | 2026-05-13 | 📰 brad_finance | P32 | ✅ READY | My peace is not negotiable. |
| 4 | Thursday | 2026-05-14 | 📞 calling_my_dad | P32 | ✅ READY | And I am doing me. Hello? |
| 5 | Friday | 2026-05-15 | 📖 sierra_reads | P32 | ✅ READY | It's a meme. That's it. |

## How to ship this week

```bash
# Monday (2026-05-11) — sierra_reads
python -m tools.assembly.from_trend \
    --plan-from-file personas/sierra-frost/calendar/2026-05-11/01-monday-sierra_reads/plan.json
# Tuesday (2026-05-12) — sierra_apologist
python -m tools.assembly.from_trend \
    --plan-from-file personas/sierra-frost/calendar/2026-05-11/02-tuesday-sierra_apologist/plan.json
# Wednesday (2026-05-13) — brad_finance
python -m tools.assembly.from_trend \
    --plan-from-file personas/sierra-frost/calendar/2026-05-11/03-wednesday-brad_finance/plan.json
# Thursday (2026-05-14) — calling_my_dad
python -m tools.assembly.from_trend \
    --plan-from-file personas/sierra-frost/calendar/2026-05-11/04-thursday-calling_my_dad/plan.json
# Friday (2026-05-15) — sierra_reads
python -m tools.assembly.from_trend \
    --plan-from-file personas/sierra-frost/calendar/2026-05-11/05-friday-sierra_reads/plan.json
```
