# Intelligent Faculty Management System (UI prototype)

Static Django proof of concept of the four wireframe screens. **No logic and no database reads yet**:
every screen is a plain template with hard-coded placeholder content, because the database design is still being decided.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py runserver 8765      # any free port
```

| URL | Screen |
|---|---|
| `/` | Employee home (bracketed `[placeholder]` version) |
| `/wellness/` | Wellness |
| `/admin-dashboard/` | Admin dashboard |
| `/dashboard/` | Employee dashboard, 1920x1080 proof of concept with sample data |

## Where things are

- `hr/templates/hr/` – one template per screen, plus `base.html` (header/footer), `base_sidebar.html` and `_mood.html`
- `hr/static/hr/css/app.css` – all styling (design tokens at the top: maroon `--maroon`, gold `--gold`)
- `hr/urls.py` – plain `TemplateView` routes (no views, no queries)

Buttons and forms are inert on purpose. Nav links that have no screen yet (My records, Attendance, Career, Messages) point to `#`.

## Parked: earlier database draft

`hr/models.py`, `hr/migrations/`, `hr/admin.py` and `hr/management/commands/seed_mock_data.py` hold a first-guess schema and mock data
based on the six modules in the proposal. **Nothing in the UI uses them.** Delete or replace them once the real database design is settled.

Run tests with `.venv/bin/python manage.py test`.
