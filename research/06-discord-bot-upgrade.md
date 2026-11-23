# Discord bot upgrade research

2026-11-23. Focused bot/Discord/SQLite research; not exhaustive or proof of originality.

- Arkbuddy already offers Discord taming, crafting, calculator and server-tracking functions: https://arkbuddy.app/discord-bot . OMNI does not match its dataset or live server functionality.
- Ark Breeder advertises editable Discord breeding lines: https://top.gg/bot/1439724666984857770 . A private notes ledger is a basic personal workflow, not an original invention or a breeding calculator.
- Ark Helper advertises creature management, breeding, server settings and exports: https://top.gg/bot/1482352518527975484 . Verify availability and behavior before making competitive claims.
- Discord interaction responses must begin within three seconds, and allowed mentions should filter user text: https://docs.discord.com/developers/interactions/receiving-and-responding . Defer database commands immediately and disable mentions.
- discord.py command registration via `setup_hook` avoids repeated `on_ready` sync on reconnect: https://github.com/Rapptz/discord.py/discussions/8967 ; app command API: https://discordpy.readthedocs.io/en/stable/interactions/api.html . Guild test sync and global sync are distinct; switching can leave duplicate registrations: https://sillydev.co.uk/guides/discord-slash-commands-not-showing .
- SQLite serializes writers; a write transaction should protect the per-user note limit: https://www.sqlite.org/isolation.html . This design targets one bot instance, not a distributed deployment.

The Discord prototype deliberately has no live game-server access, public administrative controls, reminder delivery, authentication beyond Discord interaction identity, server-sync state or taming database.
