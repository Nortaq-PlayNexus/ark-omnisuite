# Product spec — prototype and roadmap

Vision: one shared ASE-aware core, Discord bot OMNI, and web Obelisk Console. Research is incomplete: ideas below are hypotheses, and novelty has not been established. This prototype does not claim Dododex parity or production server management.

## Implemented prototype features
1. **Obelisk Advisor** — priorities based on user-entered time, raid risk and metal shortage.
2. **Raid Readiness** — transparent checklist, not a measurement of actual in-game defenses.
3. **Evolution Clock** — local countdown to a manually specified event.
4. **Lost Dino Board** — create and remove locally stored, user-entered reports.
5. **Waypoints** — create and remove local user-entered latitude/longitude records; schematic, not a game map.
6. **Lineage Ledger** — track names, parents and mutation counters locally; no inferred genetics.
7. **Boss Prep** — editable, local checklist; no claim to accurate boss requirements.
8. **Tame Planner** — save a manually entered target and notes; no unverified tame calculations.
9. **Ingot Planner** — 2 Metal to 1 ingot, cited recipe.
10. **Mutation Odds** — probability of ≥1 mutation for both parents under the 20 counter threshold, assuming three independent 2.5% rolls. Other configurations are explicitly unsupported.

All data entered in planning boards stays in browser local storage; use export/import for portability. None has been established as a novel invention.

11. **Crafting Planner** — a five-variant sourced subset with batch rounding, optional ingot expansion and stock shortfalls.
12. **Server Rate Preview** — six validated settings output to the correct INI sections; no remote writes.

13. **Tame ROI** — ranks survivor-supplied utility and effort; no inferred game data.
14. **Schematic atlas** — user-entered coordinates plotted by world, with no terrain or imported geography.
15. **Local RCON CLI** — experimental, single reply packet; no web/Discord integration.

## Data model / future
Candidate entities: creature, item, recipe, server, tribe, user, waypoint, dino, event, listing. Future APIs require authentication, permissions, audit logging and credential isolation; no RCON endpoint is enabled in this prototype. Future surfaces: verified game-data imports, accurate taming/breeding/crafting/stat engines with external reference tests, maps with licensed geographic layers, server ops, trading, community moderation and alerts. Prior 80-command scope is not implemented.

## Priority
MVP: verifiable reference data + planner prototypes + bot. V2: tests and curated data for calculators, authenticated cluster ops. V3: maps and multiplayer collaboration. Market-wide parity remains an unmet requirement.
