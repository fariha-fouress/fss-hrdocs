# Deploy on Railway (from the Dockerfile)

Railway builds this Dockerfile directly and gives you an HTTPS URL. Note: Railway
has no permanent free tier — a trial with $5 credit, then Hobby ~$5/month.

The container already binds to Railway's $PORT automatically (no change needed).

## Option A — from GitHub (recommended; auto-redeploys on push)
1. Put this folder in a GitHub repo:
       git init && git add . && git commit -m "HR doc generator"
       git branch -M main
       git remote add origin https://github.com/<you>/fss-hrdocs.git
       git push -u origin main
   (The included .gitignore keeps .env and the local database out of the repo.)
2. Railway.app → New Project → **Deploy from GitHub repo** → pick the repo.
   Railway detects the Dockerfile and builds it — no build settings needed.
3. Open the service → **Variables** tab → add (this is where secrets live on
   Railway; the docker-compose.yml file is NOT used by Railway):
       SECRET_KEY         = <long random string>
       AUTH_MODE          = password
       AUTHORIZED_EMAILS  = email1@…,email2@…,email3@…,email4@…
       LOCAL_PASSWORD     = <shared password>
       EMAIL_ENABLED      = true
       SMTP_HOST          = smtp.zoho.com        # .in/.eu/.com.au/.jp to match your Zoho DC
       SMTP_PORT          = 465
       SMTP_USE_SSL       = true
       SMTP_USERNAME      = hr@fouressynergy.com
       SMTP_PASSWORD      = <Zoho app-specific password>
       MAIL_FROM          = hr@fouressynergy.com
       MANAGEMENT_EMAILS  = manager1@fouressynergy.com,manager2@fouressynergy.com
       PAGE_SIZE          = A4
4. Settings → Networking → **Generate Domain** → gives https://<name>.up.railway.app.
   Log in there with an AUTHORIZED_EMAILS address + LOCAL_PASSWORD.

## Option B — from your computer via the Railway CLI (no GitHub)
    npm i -g @railway/cli
    railway login
    railway init            # creates a project
    railway up              # uploads this folder, builds the Dockerfile
Then set the Variables (step 3 above) in the dashboard, and Generate Domain.

## Put it on admin.fouressynergy.com (via Cloudflare)
- Railway → service → Settings → Networking → **Custom Domain** →
  enter `admin.fouressynergy.com`. Railway shows a CNAME target.
- In Cloudflare DNS: add that CNAME (start as DNS-only / grey cloud; you can
  enable the orange proxy after it validates). HTTPS is issued automatically.
- Add an "Admin Login" menu link on the website → https://admin.fouressynergy.com

## Persistent storage — REQUIRED for the Locations feature
The app keeps everything that users add or change — **Locations** (letterheads,
handbooks, legal rules), added authorised users, saved custom roles, and the
in-app Audit log — in a SQLite database plus an uploads folder. Railway's normal
filesystem is wiped on every redeploy, so without a Volume those additions would
disappear on the next deploy.

Attach a Volume once:
1. Railway → your service → **Variables** → make sure this is **removed/empty** if
   present: `DB_PATH` (leave it unset — the app derives it from DATA_DIR).
2. Railway → your service → **Settings → Volumes → New Volume**.
   - **Mount path:** `/data`
   - Save. Railway redeploys with the volume attached.
3. The Docker image already sets `DATA_DIR=/data`, so the database lands at
   `/data/hrdocs.db` and uploaded letterheads at `/data/uploads`. If you ever
   change the mount path, add a matching `DATA_DIR` variable.

That's it — added locations, letterhead uploads and edits now survive every
redeploy. (The 6 built-in locations are seeded automatically on first run.)
