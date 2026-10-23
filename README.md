# Intelligent Faculty Management System (UI prototype)

Static Django prototype built on the **Portal Layout** handoff: a persistent sidebar, a sticky page header
and a scrolling content column. Every screen in `docs/plan.md` §9.2 is built with invented sample data and works in
the browser (forms, approvals, exports, dialogs), but **nothing is saved** and pages make **no database queries**.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py runserver 8765      # any free port
```

There is no login. Pick a role with **View as** in the sidebar footer; each role has its own sample person,
sidebar and landing page, and a screen outside the role's permissions (plan §7.4) shows a no-access notice.

| Role | Sample person | Lands on |
|---|---|---|
| Employee | Robin Cruz, Teacher II, Basic Education | `/me/` |
| Department Head | Dean Ellis Ramirez, College of Engineering | `/department/` |
| HR Officer (default) | Alex Rivera | `/` |
| HR Admin | Corin Abella | `/settings/` |
| Executive | Dr. Aurora Lim | `/executive/` |
| Wellness Officer | Lia Manalo | `/wellness-office/` |

The usability tasks in plan §10 map to these roles: tasks 1–9 as Employee, 10–11 as Department Head,
12–14 as HR Officer and 15 as Executive. `/ui/` (HR Officer) is the UI kit, to copy markup from.

## Where things are

- `hr/pages.py` – the one list of screens: route, sidebar section, title, icon, and the roles that may open it;
  also the roles themselves and their landing pages. Add a screen here.
- `hr/views.py` – a single `PageView` that renders a screen inside the shell for the current role, and `view_as`
- `hr/sample_data.py` – invented, generic sample data per screen (and per role where it differs). The figures are
  built to agree across screens, and `hr/tests.py` checks that they do.
- `hr/charts.py` – geometry for the inline sparklines, bars, lines and meters (no chart library needed)
- `hr/templates/hr/` – `base.html` (shell and page header), `_sidebar.html`, one template per screen, and shared
  partials starting with `_`
- `hr/static/hr/portal/` – the handoff's `tokens.css`, `bundle.css` and Tabler icon font. Keep these as delivered;
  new icon glyphs go in the "Icons added for this project" block at the end of `bundle.css` (the font has them all).
- `hr/static/hr/css/app.css` – the project layer (`fms-` classes)
- `hr/static/hr/js/shell.js` – the shell, plus the shared hooks every screen uses: tabs, dialogs, the flash
  message (`data-say`), table export (`data-csv-table`), stat export (`data-csv-stats`), `fmsPrint()` and View as.
  Other scripts are per screen; `verify.js`, `leave_queue.js`, `faq.js` and `me_time.js` are shared by several.

To build a screen, give its `Page` a `template=` name and `roles=`, and create `hr/templates/hr/<name>.html`
extending `hr/base.html` (blocks: `scripts`, `actions`, `content`, `dialogs`). Link CSS, JS and images with
`{% load fms %}{% asset 'hr/…' %}`, not `{% static %}`: it adds the file's version, so browsers never keep a stale copy. The tests fail on a button with no
behaviour, an undefined icon, or a link to a screen the viewer's role cannot open.

## Parked: earlier database draft

`hr/models.py`, `hr/migrations/`, `hr/admin.py` and `hr/management/commands/seed_mock_data.py` hold a first-guess schema and mock data
based on the six modules in the proposal. **Nothing in the UI uses them.** Delete or replace them once the real database design is settled.

Run tests with `.venv/bin/python manage.py test`.
