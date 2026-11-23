# Deployment

## Local / trusted use

ARK OMNISUITE is designed for local or trusted private-network use.

```powershell
python -m web.server --host 127.0.0.1 --port 8000
```

Do not bind to public interfaces unless you add authentication, TLS, rate limiting, and security review. The prototype has no auth.

## Discord bot

- Create a dedicated Discord application.
- Keep `DISCORD_TOKEN` secret; do not commit it.
- Understand startup sync scope (global/test guild) before launch.
- Secure the SQLite DB/host; notes are plaintext on host.

## RCON

- Only for servers you administer.
- RCON is plaintext: use VPN/private network, firewall the port, never expose publicly.
- Experimental: single-packet response handling.

## Release checklist

- [ ] Core and HTTP/bot tests pass.
- [ ] README limitations updated.
- [ ] Verification doc updated with what was/was not tested.
- [ ] No secrets/tokens/private server data committed.
- [ ] Tag release with notes.
