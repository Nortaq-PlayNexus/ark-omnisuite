# Security Policy

## Reporting

Report vulnerabilities privately through GitHub private vulnerability reporting if enabled, or contact the maintainer directly. Do not open public issues for exploitable vulnerabilities.

## Scope

In scope:
- RCON credential handling / command injection / unsafe exposure
- Web server input validation / path traversal / unsafe file serving
- Discord bot token handling, permission issues, unsafe command behavior
- Data storage issues in local bot notes/records
- Dependency vulnerabilities in `bot/requirements.txt`

Out of scope:
- Game balance/mechanics inaccuracies (report as bugs, with sources)
- ARK server vulnerabilities not caused by this project
- Social engineering or use against servers you do not administer

## Security notes

- RCON sends passwords and commands in plaintext; use only on trusted private networks/VPNs.
- The web prototype is unauthenticated; do not expose it to the public Internet.
- Discord bot notes are stored plaintext on the bot host and are operator-accessible.
- Live Discord/RCON production hardening is incomplete.
