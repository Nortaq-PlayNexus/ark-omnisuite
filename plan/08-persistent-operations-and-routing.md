# Next milestone: saved operations and leg-by-leg routing

## Goals
1. Save a validated four-window comparison set in browser storage on explicit request, restore it when returning or reloading, and include it in existing JSON export/import. Keep comparison without saving. Existing backups without the new optional field must still import; malformed new fields must be rejected before replacing records. Clearly disclose browser-only storage, no alerts, and UTC input.
2. Extend the exact waypoint solver with per-leg grid lengths and cumulative totals, and render a numbered schematic route in the existing panel. All calculations remain Euclidean grid units, not actual in-game distances, terrain, speed or hazards. Preserve existing endpoint fields and the eight-pin limit.
3. Test old/new backups, rejected imports, overwrite/cancel, reload persistence, clear action, independently calculated route legs, optional return segment, HTTP API, browser interaction and accessibility. Update documentation and rebuild the archive.

## Non-goals
No live ARK server integration, automated notifications, timezone inference, Discord posting or claim of original novelty. Existing discovery gate and missing validated tame/breeding datasets remain open. See `research/05-event-coordination.md` for competitor overlap and scheduling sources.

## Subsequent candidates (not implemented)

- Safe per-record editing with explicit conflict/overwrite handling and backup migration tests, rather than deleting and recreating notes.
- A manually entered tribe packing manifest with shared-stock and assignment accounting; research existing tools and define units before implementation.
- Additional sourced ASE recipes or boss manifests only after verifying version, map, base quantities, station outputs and independent golden cases.
- Authenticated shared records and notifications only after threat modelling, access control and a durable service design; no open RCON bridge.
