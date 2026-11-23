# KeyFit: Know Before You Buy

KeyFit is a Django web app that checks whether a keycap set will fit a mechanical keyboard
**before** you buy it. A user describes a board once as a profile (layout, stem type, form
factor, socket and mounting style). KeyFit then compares it against a curated keycap
database and reports **Compatible**, **Incompatible** or **Partial**, with a key-by-key
**Missing Keys** report.

## Project Development 2: core feature

**Keycap Set Compatibility Checking** (a full vertical slice: PostgreSQL/Supabase -> Django -> templates)

| Part | What it does |
|---|---|
| Keyboard Profiles (CRUD) | Members add, view, edit and delete their own boards (max 10, unique names). |
| Keycap Set Checker | A member picks one of their boards and an approved keycap set; the engine compares stem type, height class and key coverage. |
| Missing Keys report | For a Partial result, lists every key the set is short of, with required vs. available quantity. |
| Check history | Every check is saved with its result and time; members can view or delete their own. The dashboard shows the 10 most recent. |

### How a result is decided
1. Stem type differs from the board's stem -> **Incompatible** (`STEM_MISMATCH`)
2. Keycap height class differs from the board's form factor -> **Incompatible** (`HEIGHT_CLASS_MISMATCH`)
3. Otherwise, if the set has at least the required quantity of every key the layout needs -> **Compatible**
4. Otherwise -> **Partial**, with the short keys listed

Incompatible always takes priority over Partial.

### Roles
- **Member:** full CRUD on their own boards, runs checks, views/deletes their own history. Cannot see other users' data.
- **Admin:** read-only view of all boards and checks on the admin dashboard; manages the catalog (keycap sets, layouts, key definitions) through the Django admin. Admins cannot open member pages (403).

### Standard features (Project Development 1)
Registration, login/logout, role-based dashboards, user profile (all still working).

## Tech stack
Django (templates) and PostgreSQL via Supabase.

## Setup
```bash
git clone https://github.com/MiguelCarlosSibi/KeyFit-Sibi-Miguel-G6.git
cd KeyFit-Sibi-Miguel-G6
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your Supabase database values and a secret key
(use the **Session pooler** connection details), then:

```bash
python manage.py migrate
python manage.py seed_reference        # stem types, key definitions, layouts
python manage.py seed_keycap_sets      # sample keycap sets so the checker can be tried
python manage.py createsuperuser
python manage.py runserver 8080
```

New accounts are members. To make an admin, set the user's role:

```bash
python manage.py shell -c "from accounts.models import User; u=User.objects.get(username='YOUR_USERNAME'); u.role='admin'; u.save()"
```

The seeded keycap sets are **sample data**. Add real, verified sets in the Django admin
(`/admin/`) under *Keycap sets*.

## Branching
`main` (stable) <- `develop` (integration) <- `feature/*` (one branch per feature),
merged through pull requests.
