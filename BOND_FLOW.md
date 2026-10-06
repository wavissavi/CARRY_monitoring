# UST Exhaustion / Flow Turn: observation-only pilot

The panel helps read three questions: is yield momentum slowing, does easing persist, and do independently dated positions accompany it? Its weight in RISK and ADD is zero. It does not confirm an exhaustion high, establish buying motives, start a Reversal clock, or override a veto. No backtested hit rate has been established.

## Dated observations

2026-10-06: Investing.com completed weekday closes through October 5 produce Wilder RSI(14) 75.7547, versus 80.3040 at the preceding 20-session highest close on September 30. The close is higher and RSI lower, a descriptive slowdown candidate. The most recent two completed sessions show rising RSI; latest easing streak is zero. This corrects earlier non-reproducible RSI figures. Intraday October 6 quotes are excluded.

The September 29 CFTC futures-only report for UST 10Y NOTE, code 043602, shows leveraged gross shorts increased by 151,495 contracts. This weekly observation predates the candidate and cannot confirm October 5 covering. Weekly OI must never fill missing daily OI. Gross futures shorts may include cash/futures basis hedges. A change does not establish the motive of a specific trader.

The futures source label “Dec 26 (TYU26)” has inconsistent delivery-month identifiers. Futures RSI is null until the exact contract or continuous series and roll adjustment are verified. Daily OI is null until sourced with matching instrument/date coverage. Missing data is pending, not zero or a negative signal.

## Reproduce and refresh

Run from the repository root:

```sh
python3 scripts/build-bond-flow.py data/bond-flow-raw-20261006.json
```

Raw captures include source URL, retrieval time, actual rows and CFTC report dates. The generator excludes weekend quotes and the current session, seeds RSI with the first 14 arithmetic-average gains/losses, and then smooths with Wilder's 13/14 formula. It uses 152 completed weekday closes starting March 2. These are a separate Investing daily-close series, not CNBC RSI and not the existing morning UST snapshot.

For subsequent daily monitoring, capture completed sessions from the same verified source; validate each date and available row rather than treating calendar weekdays as guaranteed sessions. Create a new dated raw file, update its asof, and regenerate the observation snapshot. The generator also appends dated observations to bond-flow-history.json; old dated raw captures and snapshots must be retained. Do not overwrite history.json or feed this panel into levels(), effectiveBondState() or addDecision(). This addition does not create a new scheduler or promise an unattended data feed.

Before CFTC data is updated, verify report date, market code, futures-only scope and all-expiries coverage. Previous-week positions here are reconstructed from this report's published weekly change; they are not independently fetched prior reports.

## Direction arrows (October 6 display update)

Arrows annotate the first completed session meeting both filters: at least two consecutive same-direction changes and cumulative magnitude at least 5bp for yield or 5 points for yield RSI. These fixed thresholds are provisional display conventions, not calibrated trading thresholds or statistical significance tests. Red up arrows indicate that plotted series increased; blue down arrows indicate it decreased. Yield direction is opposite bond-price direction.

Only one arrow is emitted per uninterrupted monotonic run. A flat, missing value or opposite-direction move resets the run. The full captured series is evaluated before restricting marks to the displayed 20-session window. Marks are anchored on the confirmation session and value, never backdated to an earlier pivot. Hover details and the visible date/change list give the exact comparison start and cumulative move. Previously saved observations do not use future data. Unverified futures RSI and flow data do not receive arrows.

The current reviewed window has yield up arrows on September 9, September 24 and October 5; yield-RSI up arrows on September 9 and September 24 and a down arrow on September 22. This display update does not alter the existing slowdown candidate interpretation, RISK, Bond Reversal or ADD logic.

## Pilot review procedure

Record candidate dates before later outcomes are known. At each subsequent completed session, retain whether momentum and yield easing persisted, whether the candidate high was exceeded, when independent positioning became available, and the existing Bond Reversal/ADD result. Review examples of both continuation and false turns before proposing an engine change. Overlapping candidates from one shock are not independent tests. Numerical thresholds and promotion rules require a separate decision after evidence accumulates; there is no automatic promotion.

The current descriptive pair rule is latest completed close greater than the preceding 20-session maximum close and latest RSI below RSI at that prior maximum. Streaks count consecutive decreases ending at the latest completed session. These are organizing conventions, not calibrated predictors.
