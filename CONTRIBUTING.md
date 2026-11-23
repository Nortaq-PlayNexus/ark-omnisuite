# Contributing

## Scope

ARK OMNISUITE is an unofficial prototype. Contributions should preserve honesty: no unverified game formulas, no claims of Dododex/A-Calc parity, no fake live-server verification.

## Setup

```powershell
git clone https://github.com/Nortaq-PlayNexus/ark-omnisuite.git
cd ark-omnisuite
python -m unittest discover -s core/tests -v
python -m unittest discover -s tests -p "test_*.py" -v
python -m web.server --host 127.0.0.1 --port 8000
```

For Discord bot development:

```powershell
python -m pip install -r bot/requirements.txt
python -m bot.main --dry-run
```

## Rules

- Cite sources for game mechanics/formulas in code/comments/docs.
- Add or update tests for calculator changes.
- Do not expose RCON to HTTP/Discord surfaces.
- Do not commit tokens, passwords, or private server data.
- Mark unverified behavior clearly in README/docs.
