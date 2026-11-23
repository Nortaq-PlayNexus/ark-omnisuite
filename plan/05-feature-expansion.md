# Feature expansion — researched plan

Research: `../research/03-feature-ideas.md`. These are enhancements for a small prototype, not claims of ecosystem novelty or parity.

## This milestone

1. **Breeding inheritance odds:** given count of differing target stats and independent breeding events, calculate `0.55^n`, probability of ≥1 success across events, and expected events (`1/p`). Source https://ark.wiki.gg/wiki/Breeding and https://ark.wiki.gg/wiki/Mutations. For n=0 all selected stats already match. Exclude mutation, gender, imprint and multiple-birth dependence. Shared Python core, HTTP API, web and tests.
2. **Refining Forge planner:** one forge, metal → ingots (20 seconds each, 2 metal per ingot), user choice of thatch/wood/sparkpowder/anglergel, burn time per unit from https://ark.fandom.com/wiki/Refining_Forge and https://ark.fandom.com/wiki/Metal_Ingot. `ceil(total_seconds / fuel_burn_seconds)`; avoid assuming partial fuel is reusable; no parallel forges, gasoline, start/stop inefficiency or rate adjustments. Shared core, web, bot where feasible; reference and boundary tests.
3. **Crafting queue:** aggregate multiple recipes in the existing five-variant catalog; group identical recipe variants before batch rounding, total shared ingredients, subtract stock once, and optionally consume owned ingots before expanding remaining ingots to metal. Queue outputs do not supply another item's ingredients; no custom recipe/quality/modded/server costs; verified recipe source links exposed. Use request-based API plus local web form. Batch allocation tests include split chemistry quantities and shared stock.

## Deferred

- Creature-specific tame/breeding/imprint numbers: require license-appropriate, versioned ASE species data and independent golden comparisons.
- Multiplayer inventory sync and RCON web controls: require authentication, authorization, secrets isolation, audit and multi-packet protocol support.
- Save-derived maps / OCR / texture map geography: need validated parsers or appropriately licensed map data and privacy review.

## Completion checks

- Core and HTTP tests and browser smoke tests; accessibility re-check if tooling exists.
- Documentation distinguishes manual inputs, assumptions and unverified data; screenshots contain labeled demo inputs.
- Existing zip predates this milestone; rebuild archive after verifying.
