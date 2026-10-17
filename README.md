# Intelligent Faculty Management System (UI prototype)

Static Django prototype built on the **Portal Layout** handoff: a persistent sidebar, a sticky page header
and a scrolling content column. **No logic and no database reads yet.** Every screen from `docs/plan.md` §9.2 exists as
a route; the Dashboard shows the full layout with placeholder figures, and the rest are placeholder pages that list
what each screen will hold.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py runserver 8765      # any free port
```

| URL | Screen |
|---|---|
| `/` | Dashboard (employee landing page, sample data) |
| `/ui/` | UI kit: every component, to copy markup from |
| everything else in the sidebar | Placeholder page: "Not built yet", plus the plan's list for that screen |

## Where things are

- `hr/pages.py` – the one list of screens: route, sidebar section, title, icon, and what is planned. Add a screen here.
- `hr/views.py` – a single `PageView` that renders a screen inside the shell (no queries)
- `hr/sample_data.py` – invented, generic sample data per screen, merged into the template context
- `hr/charts.py` – geometry for the inline sparklines and meters (no chart library needed)
- `hr/templates/hr/` – `base.html` (shell and page header), `_sidebar.html`, `dashboard.html`, `placeholder.html`, `ui_kit.html`
- `hr/static/hr/portal/` – the handoff's `tokens.css`, `bundle.css` and Tabler icon font. Keep these as delivered;
  new icon glyphs go in the marked block at the end of `bundle.css`.
- `hr/static/hr/css/app.css` – the project layer (`fms-` classes): rail, collapsible nav groups, page grids, dialog
- `hr/static/hr/js/shell.js` – remembered rail, mobile drawer, nav groups, and the UI kit demos

To build a screen, give its `Page` a `template=` name and create `hr/templates/hr/<name>.html` extending `hr/base.html`
(blocks: `actions`, `content`, `dialogs`). Buttons and forms are inert on purpose.

## Parked: earlier database draft

`hr/models.py`, `hr/migrations/`, `hr/admin.py` and `hr/management/commands/seed_mock_data.py` hold a first-guess schema and mock data
based on the six modules in the proposal. **Nothing in the UI uses them.** Delete or replace them once the real database design is settled.

Run tests with `.venv/bin/python manage.py test`.
