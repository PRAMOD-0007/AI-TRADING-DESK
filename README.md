# AI Trading Desk

Flask COT analytics application with a public landing page, Supabase members authentication, and a protected dashboard/API.

## Local setup

1. Create a Supabase project.
2. In Supabase Authentication settings, disable public sign-ups if access is invitation-only.
3. Invite members from Supabase Dashboard → Authentication → Users.
4. Configure Site URL and Redirect URLs for local and production URLs.
5. Copy the Project URL and publishable/anon key from Supabase API settings.
6. Set environment variables (see `.env.example`):

```bash
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY
```

7. Install and run:

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. Members sign in at `/login`; authenticated members access `/dashboard`.

## Render deployment

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn app:app
```

Set `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in Render environment variables. Configure Supabase URL settings with the deployed app URL.

## Security

- Supabase handles password storage and authentication.
- Protected Flask API endpoints validate bearer tokens with Supabase Auth.
- The publishable/anon key is intended for browser use. Never expose a service-role key.
- Public signup is not included. Invite/create users through Supabase Auth unless a registration flow is intentionally added.
- Keep `.env` out of Git.
