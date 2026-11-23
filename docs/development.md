# Development

## Prerequisites

- Python 3.11+ (3.9+ may work; CI uses 3.11).
- Optional: `pip install -r bot/requirements.txt` for Discord bot.
- Optional: Playwright + Chromium deps for `tests/browser_smoke.py`.

## Run

```powershell
python -m unittest discover -s core/tests -v
python -m unittest discover -s tests -p "test_*.py" -v
python -m web.server --host 127.0.0.1 --port 8000
```

Bot dry-run:

```powershell
python -m pip install -r bot/requirements.txt
python -m bot.main --dry-run
```

## Checks

```powershell
python -m unittest discover -s core/tests -v
python -m unittest discover -s tests -p "test_*.py" -v
node --check web/public/app.js  # if node installed
```

## Notes

- Do not add unverified game formulas. Cite sources.
- Keep RCON local-only; no HTTP/Discord command passthrough.
- Browser smoke and axe checks require Playwright/Chromium; not run in default CI.
