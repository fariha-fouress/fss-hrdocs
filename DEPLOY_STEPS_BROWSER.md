# Push to GitHub, then deploy on Railway — browser runbook

Prep (do once, on your computer):
- Unzip `hr-docgen-deploy.zip`. You'll get a `hr-docgen` folder with `app/`,
  `Dockerfile`, `requirements.txt`, etc. (No `.env` — good, secrets stay out.)
- Have a GitHub account and a Railway account ready (sign in first).

Paste the block below to the Claude browser extension. Steps marked YOU are
manual (unzip, drag files, type secrets); the agent does the rest.

================= PASTE TO CLAUDE BROWSER EXTENSION =================
Help me deploy a web app to GitHub then Railway. Do the navigation and clicking;
pause and tell me clearly when a step needs me. Go one step at a time.

PART 1 — GitHub
1. Navigate to https://github.com/new
2. In "Repository name" type: fss-hrdocs
3. Select the "Private" radio option.
4. Leave everything else default. Click the "Create repository" button.
5. On the new repo page, click the link "uploading an existing file"
   (or navigate to https://github.com/<my-username>/fss-hrdocs/upload/main ).
6. PAUSE — tell me to drag the CONTENTS of my unzipped hr-docgen folder
   (the app folder, Dockerfile, requirements.txt, and all other files) into the
   upload drop area. Wait for me to confirm the files are listed.
7. Scroll to "Commit changes" and click the green "Commit changes" button.
8. Confirm the repo now shows the app/ folder and Dockerfile.

PART 2 — Railway
9. Navigate to https://railway.com/new  (sign in if asked).
10. Click "Deploy from GitHub repo".
11. If Railway asks to connect/authorize GitHub, click "Configure GitHub App",
    grant access to the fss-hrdocs repo, then come back.
12. Select the fss-hrdocs repository. Railway detects the Dockerfile and starts
    building. Wait for the service card to appear.
13. Click the service card, then open the "Variables" tab.
14. Click "Raw Editor". PAUSE — tell me to paste my environment variables
    (I have them ready). Wait for me, then click "Save"/"Update Variables".
15. Open the "Settings" tab → scroll to "Networking" → under "Public Networking"
    click "Generate Domain". If it asks for a port, enter 8080.
16. Copy the generated https://<name>.up.railway.app URL and give it to me.
17. PAUSE — I will open that URL and log in to confirm it works.
==================================================================

Environment variables to paste in Railway's Raw Editor (step 14).
YOU fill the <...> values; keep the rest as-is:

SECRET_KEY=<paste a long random string>
AUTH_MODE=password
AUTHORIZED_EMAILS=user1@fouressynergy.com,user2@fouressynergy.com,user3@fouressynergy.com,user4@fouressynergy.com
LOCAL_PASSWORD=<your shared login password>
EMAIL_ENABLED=true
SMTP_HOST=smtp.zoho.com
SMTP_PORT=465
SMTP_USE_SSL=true
[email protected]
SMTP_PASSWORD=<Zoho app-specific password>
[email protected]
MAIL_FROM_NAME=HR Document Generator
[email protected]
PAGE_SIZE=A4

Notes:
- Railway is not free: $5 trial credit, then ~$5/month.
- SMTP_HOST: use smtp.zoho.in / .eu / .com.au / .jp if your Zoho is on that DC.
- Later, to use admin.fouressynergy.com: Railway → Settings → Networking →
  Custom Domain → enter it → add the CNAME it shows in Cloudflare DNS.
