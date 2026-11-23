# OMNI Discord expansion

## Implement
- Expose existing bounded, source-caveated core models as slash commands: crafting queue; user-entered incubation ranges, waypoint route, time-window conflict comparison, server-rate preview, readiness, advisor and utility/hour comparison. Keep existing commands and add example syntax in `/omni` and documentation. Small bounded structured strings replace attachments; these are not live game data.
- Add private personal `/plans` CRUD/list for actionable user notes, scoped by Discord guild/DM and user ID, stored in a local SQLite database across bot restarts, capped per owner. This is not a shared tribe board or web sync. Immediate deferred responses for disk operations, parameterized SQL, transaction-bound limit, suppressed mentions, escaped text, no token storage, configurable database path and file-permission guidance. Do not ship a user's database in the archive.
- Private responses by default, optional intentional public results for calculations only; plans remain private. No RCON, admin actions, background notification or fabricated game data. Move sync to setup hook and optionally use a test-guild sync.

## Verify
- Mocked interaction callback tests cover command registration, responses, parser/validation errors, public vs private/mention suppression, plans isolation, ownership, CRUD, concurrency limits and persistence across store instances. Existing core/API/browser tests remain green. No live Discord registration or delivery claim without credentials. Update README and verification.
