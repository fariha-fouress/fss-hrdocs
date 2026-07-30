# Deploy on a managed host (closest to "upload and it runs")

Cloudflare cannot run this app (it is not a static site). The simplest hosts that
run the included Dockerfile are **Render** or **Railway**. Steps for Render:

1. Put this folder in a Git repo (GitHub/GitLab). On github.com: New repo →
   upload these files → commit.
2. Render.com → New → **Web Service** → connect the repo.
   Render auto-detects the Dockerfile — no build settings needed.
3. Add environment variables (Render dashboard → Environment):
       SECRET_KEY         = <long random string>
       AUTH_MODE          = password
       AUTHORIZED_EMAILS  = email1@…,email2@…,email3@…,email4@…
       LOCAL_PASSWORD     = <your shared password>
       EMAIL_ENABLED      = false
4. Add a **Disk** (Render → the service → Disks) mounted at `/srv/data` so the
   audit log survives restarts. Set DB_PATH = /srv/data/hrdocs.db.
5. Deploy. Render gives you a URL like https://fss-hrdocs.onrender.com.

## Put it on admin.fouressynergy.com (via Cloudflare)
- In Render: Settings → Custom Domain → add `admin.fouressynergy.com`.
- In Cloudflare DNS: add the CNAME Render shows you (set it **DNS only /
  grey-cloud** first; you can enable the orange proxy after it verifies).
- Render issues HTTPS automatically.

## Add the tab on the website
Add a navigation menu item: **Admin Login → https://admin.fouressynergy.com**

Notes: use a paid instance/disk for a real internal tool (free tiers sleep and may
lose the database). Railway and Fly.io work the same way from the Dockerfile.
