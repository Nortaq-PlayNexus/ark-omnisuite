# OMNI Discord bot guide

OMNI is an experimental, unofficial Discord slash-command bot for **ARK: Survival Evolved**. It uses the same limited calculations as the web prototype. It does not have live game-server access, creature/taming data, automated reminders, shared tribe records or RCON administration. Features are not claimed to be unique.

## Setup

From `build/`, with Python 3.9+:

```sh
python -m pip install -r bot/requirements.txt
python -m bot.main --dry-run
python -m unittest discover -s tests -p 'test_bot.py' -v
export DISCORD_TOKEN='your bot token'
# Optional: restrict this run's sync to one test guild (use your own actual server ID):
# export DISCORD_GUILD_ID='your numeric test server ID'
# Optional: choose a protected, persistent database location:
# export OMNI_DB_PATH='/secure/persistent/folder/omni.sqlite3'
python -m bot.main
```

Create your own dedicated application at https://discord.com/developers/applications and install the bot with `bot` and `applications.commands` scopes. Keep the token secret. Do not paste it into code, screenshots, logs or chat. Use least privilege; no message-content intent is needed. The bot must remain online for commands to work.

At startup OMNI **syncs its application-command tree**, globally by default or to the selected test guild. Sync can overwrite command registrations in that scope for the same application, so use a dedicated application or make a backup of your registration design first. Global propagation may take time. Test-guild and global command registrations are separate; changing modes can leave duplicate guild/global entries. No automatic deletion of registrations from the previous scope is performed. Do not use two live instances writing to different copies of the same DB. Setup and delivery have not been tested with a real Discord account/server.

## Command directory

Slash arguments are entered in Discord's command form. Calculation responses default to **ephemeral**; explicitly set `public` true to share a successful result. Input errors and `/plans` responses remain private. Mentions are disabled in replies.

| Command | Function and limits |
|---|---|
| `/omni` | In-Discord help and concise examples |
| `/ingots` | Ore for ingots; fuel excluded |
| `/forge` | One standard refining forge fuel/time baseline |
| `/mutation` | Mutation chance with both parental counters below 20, independent events only |
| `/inheritance` | Higher-stat inheritance odds under stated assumptions |
| `/craft` | One of five sourced recipe variants |
| `/tribute` | The Island Broodmother Gamma/Beta/Alpha, runs and optional inventory |
| `/queue` | Up to five crafting lines, shared stock, optional ingot expansion |
| `/incubate` | Maximum overlap of manually entered Celsius intervals |
| `/route` | Exact shortest straight-grid ordering of 1–8 manually entered pins |
| `/windows` | Compare up to four timezone-aware windows and show Discord timestamps |
| `/rates` | Preview six ASE INI rates; never touches server files |
| `/readiness` | Equal-weight, self-reported five-check score |
| `/advisor` | Simple priorities from time and flags, not telemetry |
| `/tamecompare` | Rank your own utility scores divided by your own estimated hours |
| `/plans add`, `/plans list`, `/plans edit`, `/plans done`, `/plans remove` | Private, owner-and-context-scoped persistent notes |

### Structured inputs

The commands below use `|` between fields and `;` between entries. Names cannot themselves contain those delimiters. Inputs are capped at 1,000 characters. All names and quantities are user supplied; no data is pulled from the game.

- `/queue` items: `smithy|2;spyglass|1`. Supported recipe IDs: `smithy`, `spyglass`, `metal_ingot`, `narcotic_mortar`, `narcotic_chemistry`. Optional stock: `Wood|20;Stone|100`. Counts must be nonnegative integers. Item names are case-sensitive and must be valid ingredient names in the small built-in recipe set. Repeated recipe lines are combined before batch rounding; outputs are not transferred to other queue lines. No fuel or mods.
- `/tribute` stock: `Artifact of the Hunter|1;Argentavis Talon|4`. Item names are case-sensitive; only Island Broodmother tribute names are accepted. The calculator does not check levels, gear, combat readiness, map variants or server settings.
- `/incubate` ranges: `Egg A|10|20;Egg B|20|30`. Closed Celsius ranges; results are mathematical overlap only, not egg safety, hatch speed or powered-incubator behavior.
- `/route` pins: `Base|50|50;Metal|30|70`, plus numeric start latitude/longitude (0–100). Euclidean grid distance ignores terrain, hazards, elevation, travel time and actual in-game distance; duplicate names are permitted. Optional return to start.
- `/windows` events: `Raid|2027-01-01T10:00Z|2027-01-01T12:00Z;Hatch|2027-01-01T11:00Z|2027-01-01T13:00Z`. Supply ISO timestamps with `Z` or an explicit UTC offset (e.g. `+11:00`). Ends are exclusive, so adjacent events do not overlap. Discord timestamp rendering is whole-second precision. These are not reminders and are not saved.
- `/tamecompare` candidates: `Anky|60|2;Argy|80|2`. These are **your** arbitrary utility scores and effort hours, not calculated creature stats or taming times.

## Private plans and database

Use `/plans add` with up to 120 characters. `/plans list` shows five records per page and provides numeric IDs. Use `/plans edit`, `/plans done` (set `complete` false to reopen), and `/plans remove` with an ID. Removal is immediate and irreversible; there is no confirmation dialog or automatic retention policy. A limit of 15 notes applies per user **per server**, including completed notes; DMs are a separate context. One user's commands cannot list or mutate another user's records, and server A's records are separate from server B and DMs.

The default database is `build/data/omni.sqlite3` on the **bot host**, not the user's device. `OMNI_DB_PATH` changes it. Newly created DB files use Unix mode 0600 where supported; secure the parent directory, backups and host as well. Existing files retain their existing permissions. Notes and Discord user/server IDs are stored in plaintext, so the bot operator and anyone with host/backup access can read them. Ephemeral Discord replies are not encryption. Avoid entering passwords, admin tokens or sensitive coordinates. Notes persist across bot restarts if the database is preserved, but not across ephemeral hosting resets or lost disks. Back up the database securely with SQLite's online backup facility or while the bot is stopped. `/plans` does not sync with web records, and there is no shared tribe board.

Tests use temporary databases and mocked interactions. They do not verify live Discord registration, permissions, posting, delivery, platform rate limits or production security. No bot database or secrets are included in the distributed ZIP.
