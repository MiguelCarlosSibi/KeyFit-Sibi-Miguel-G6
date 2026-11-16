# KeyFit: Know Before You Buy

A Django web app that checks whether a keycap set or switch fits a keyboard before purchase.
This phase covers the **Account Feature**.

## Stack
Django (templates), PostgreSQL via Supabase

## Features
- Registration with validation (required fields, email format, unique username/email, password confirmation) and hashed passwords
- Login / logout, with `@login_required` protection
- Role-based dashboards: **member** and **admin** (a user cannot open the other role's dashboard)
- User profile: view and edit your own details

## Setup
```bash
git clone https://github.com/MiguelCarlosSibi/KeyFit-Sibi-Miguel-G6.git
cd KeyFit-Sibi-Miguel-G6
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and fill in the Supabase database values and a secret key, then:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
New accounts are members. To make an admin, set the user's `role` to `admin`:
```bash
python manage.py shell -c "from accounts.models import User; u=User.objects.get(username='YOUR_USERNAME'); u.role='admin'; u.save()"
```