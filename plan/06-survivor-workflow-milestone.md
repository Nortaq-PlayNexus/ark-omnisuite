# Survivor workflow milestone

Evidence and limitations: `research/04-survivor-workflows.md`. These designs combine capabilities; they are hypotheses and are not asserted to be globally novel.

## Build now

1. **Tribute Manifest:** The Island Broodmother Gamma/Beta/Alpha × run count, backed by the cited official wiki table. Subtract user-entered stock once and show deficits; explicitly exclude player level, map variants, gear and custom server requirements. Tests for difficulty, repeated runs, inventory validation.
2. **Incubation Range Mixer:** accept 1–10 user-entered egg names and closed Celsius intervals, validate bounds, identify a temperature maximizing the count of intervals that include it, and report both included and excluded names. This is interval arithmetic, not a game-derived hatch-rate or temperature safety guarantee. Test overlaps, touching endpoints, ties and input validation. No assumed creatures or temperatures.
3. **Waypoint Route Sketch:** solve a shortest straight-grid route from supplied start through at most eight same-world user waypoints. Use dynamic programming, not an unbounded factorial search; optional return to start. Return ordered names and length in abstract grid units. Explicitly not terrain-aware or a real-game distance/time estimate. Validate against brute-force oracle and test empty/duplicate/invalid data.

## Shared architecture

Pure Python core; validated JSON endpoints; themed web forms; optional bot command for tribute. Browser-local coordinates remain user-owned. No authenticated live server operations. Tests: independent core and API, browser smoke and accessibility re-scan when available. Update README, verification and rebuilt ZIP only after tests.

## Deferred

Species-specific timed breeding, live map, automated save integration, timers as alerts when app is closed, and cross-tribe sync require reliable datasets, runtime facilities or authentication. No claims of original invention or complete research.
