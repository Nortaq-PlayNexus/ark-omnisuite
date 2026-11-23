# Event-coordination research and design constraints

2026-11-23; three targeted searches. This is a focused research increment, not an exhaustive ecosystem survey.

- Dododex already supplies breeding schedule and timers, so timeline planning is not a novelty claim: https://www.dododex.com/breeding .
- Discord has scheduled events; its own instructions describe event creation and permissions: https://support.discord.com/hc/en-us/articles/4409494125719-Scheduled-Events . This prototype does not create or sync them.
- A historical ARK Tribe Log Relay sends log entries to Discord; it is not evidence of event scheduling in this prototype: https://steamcommunity.com/app/346110/discussions/2/1692659769945785904/ .
- Discord timestamp formatting renders an instant for each viewer; examples and UTC/Unix format: https://discordtimestamp.org/blog/how-to-use-discord-timestamps-and-manage-time-zones and https://tomricky.substack.com/p/the-one-timezone-rule-for-discord . This prototype produces text tags only; it does not send messages or automatically determine organizer timezone.
- Date and timezone changes can cause ambiguous or missing local times. To avoid silently picking a DST occurrence, input windows explicitly in UTC; users must convert their intended local time themselves. Compare only actual instants; adjacent events are not overlaps.

## Selected improvements

- **Operations Window Comparator:** compare manually entered UTC start/end windows, show every overlapping pair and intersection, plus text tags for Discord. Initially unsaved; the next milestone adds one explicitly saved browser-local set. No live alerts, game-derived durations, automatic server-event discovery, recurrence or timezone conversion guarantee.
- **Route selection:** let users select any 1–8 plotted pins from a world rather than requiring every pin; exact grid algorithm and caveats unchanged.
- **Tribute stock inputs:** replace raw JSON in the UI with named numeric fields; preserve existing backend contract and validations. The user-entered stock remains local form state and is sent to the local API when calculated.
