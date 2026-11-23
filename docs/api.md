# API

The web server (`web/server.py`) provides a small local HTTP API used by the Obelisk Console UI. It is unauthenticated and intended for localhost.

## Running

```powershell
python -m web.server --host 127.0.0.1 --port 8000
```

## Endpoints

| Method | Path | Purpose |
|---|---:|---|
| GET | `/api/health` | Health/status check. |
| POST | `/api/ingots` | Ingot planning calculation. |
| POST | `/api/mutations` | Mutation odds calculation. |
| POST | `/api/breeding` | Breeding inheritance odds. |
| POST | `/api/forge` | Forge fuel/time calculation. |
| POST | `/api/crafting` | Crafting queue calculation. |
| POST | `/api/roi` | Tame ROI comparison. |
| POST | `/api/defense` | Raid readiness checklist score. |
| POST | `/api/ini` | Server rate INI snippet preview. |
| POST | `/api/expedition` | Broodmother tribute shortfall calculation. |
| POST | `/api/incubation` | Incubation range overlap. |
| POST | `/api/route` | Waypoint route sketch. |
| POST | `/api/operations/compare` | UTC operations window overlap/comparison. |

## Notes

- Request/response shapes are defined by handlers in `web/server.py` and consumed by `web/public/app.js`.
- Invalid/unsupported inputs return validation errors; calculators do not guess unsupported cases.
- No RCON endpoints are exposed.
- Do not expose this server publicly without adding authentication and security controls.
