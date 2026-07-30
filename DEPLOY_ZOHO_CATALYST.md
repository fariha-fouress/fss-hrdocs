# Deploy on Zoho Catalyst (AppSail, custom Docker runtime)

Catalyst AppSail can run this app's Docker image directly. Since you already use
Zoho, billing/identity stay in one place. Free tier: ~25,000 GB-seconds + 100,000
API calls per month — ample for 4 internal users.

## Prerequisites
- A Zoho account (your existing one) and a Catalyst project.
- Node.js installed (for the Catalyst CLI), and Docker.
- A Docker Hub (or ECR/GCP Artifact Registry) account to hold the image.

## One-time code note (already done)
Catalyst assigns the HTTP port via the env var X_ZOHO_CATALYST_LISTEN_PORT.
The included Dockerfile already binds gunicorn to it (falling back to 5000
elsewhere), so no code change is needed.

## Steps
1. Console: sign in at https://console.catalyst.zoho.com and create a project,
   e.g. "FSS-HRDocs".
2. Build and push the image to a registry:
       docker build -t <dockerhub-user>/fss-hrdocs:1 .
       docker push <dockerhub-user>/fss-hrdocs:1
3. In the Catalyst console → AppSail → New App → choose **Custom Runtime** and
   connect the image `<dockerhub-user>/fss-hrdocs:1` from Docker Hub.
   (Alternatively use the Catalyst CLI: `npm i -g zcatalyst-cli`, `catalyst login`,
    then deploy the image per the "Custom Runtimes → Deploy from CLI" docs.)
4. Configuration (console → your app → Configurations):
   - Listen port: leave default (9000) — the app reads it automatically.
   - Memory: 512 MB is fine. Disk: default is fine.
   - Environment variables:
         SECRET_KEY        = <long random string>
         AUTH_MODE         = password
         AUTHORIZED_EMAILS = email1@…,email2@…,email3@…,email4@…
         LOCAL_PASSWORD    = <your shared password>
         EMAIL_ENABLED     = false
         PAGE_SIZE         = A4
         DB_PATH           = /tmp/hrdocs.db      # see persistence note below
5. Deploy to the **Production** environment. Catalyst gives you an app URL.
6. Put it on your subdomain: in Cloudflare DNS add a CNAME
   `admin.fouressynergy.com` → the Catalyst app URL (confirm custom-domain
   mapping in the Catalyst console). Then add an "Admin Login" menu link on the
   website pointing to https://admin.fouressynergy.com.

## IMPORTANT — audit-log persistence
AppSail instances are serverless: the local disk is **ephemeral**, so the SQLite
audit log (and generated-document records) can be lost on redeploy or when the
instance recycles. Two options:
  (a) Accept it — fine if you only need live generation and email notifications,
      not a permanent on-server history.
  (b) Keep durable records — switch the audit log + documents table from SQLite
      to **Catalyst Data Store** (a managed table). This is a focused code change
      to app/db.py; ask and it can be provided as a Catalyst-specific build.

If you need a permanent audit trail with zero code changes, a small always-on VM
(e.g. Oracle Always Free) keeps SQLite on disk — see DEPLOY_CLOUDFLARE.md.

## Enable the download-notification email (Zoho SMTP)
Add these environment variables (console → your app → Configurations), in
addition to the ones above:

    EMAIL_ENABLED     = true
    SMTP_HOST         = smtp.zoho.com     # use smtp.zoho.in / .eu / .com.au / .jp to match your Zoho data centre
    SMTP_PORT         = 465
    SMTP_USE_SSL      = true
    SMTP_USERNAME     = hr@fouressynergy.com          # a real Zoho mailbox to send FROM
    SMTP_PASSWORD     = <Zoho APP-SPECIFIC password>  # NOT the normal login password
    MAIL_FROM         = hr@fouressynergy.com
    MAIL_FROM_NAME    = HR Document Generator
    MANAGEMENT_EMAILS = manager1@fouressynergy.com,manager2@fouressynergy.com

### Get the Zoho app-specific password (one time)
Because Zoho accounts use 2FA, SMTP needs an app password, not your login one:
1. Sign in at https://accounts.zoho.com → Security → App Passwords.
2. "Generate New Password", name it e.g. "HR Doc Generator".
3. Copy the generated password into SMTP_PASSWORD above.

On every PDF download the app emails MANAGEMENT_EMAILS with the document type,
candidate, entity, who downloaded, and timestamp — a permanent record in that
mailbox, independent of the server's own storage.
