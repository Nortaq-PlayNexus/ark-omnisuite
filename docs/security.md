# Security

## Summary

ARK OMNISUITE handles local planning data, optional Discord bot tokens/notes, and optional RCON credentials. The main risks are accidental public exposure, plaintext RCON, token/DB mishandling, and untrusted input.

## Controls / boundaries

| Area | Control / note |
|---|---|
| Web app | No auth; bind to localhost by default. Do not expose publicly. |
| RCON | Plaintext Source RCON protocol; CLI only; not exposed via web/Discord. |
| Discord bot | Token via env; dry-run mode; notes scoped by user/context but plaintext on host. |
| Browser records | localStorage only; export/import user-controlled. |
| Inputs | Calculators validate/reject unsupported cases; tests cover core/HTTP/bot paths. |

## Known gaps

- No authentication/authorization for web app.
- No production hardening/rate limiting/audit logging.
- RCON single-packet responses may truncate long output.
- Live Discord registration/permissions/delivery not verified.
- No independent security audit.

See [SECURITY.md](../SECURITY.md).
