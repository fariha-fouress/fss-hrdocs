# Deploy on a Fouress subdomain via Cloudflare Tunnel

Goal: the tool lives at **https://admin.fouressynergy.com**, reached from an
"Admin Login" tab on the website. Cloudflare provides the domain + HTTPS; the app
runs as a Docker container on any always-on machine (office PC, server, or a small
VPS). Cloudflare Pages/Workers cannot run this app itself.

## 1. Run the app (on the always-on machine, one time)
```
docker compose up -d --build        # starts the tool on http://localhost:5000
```
Set your 4 users + password in docker-compose.yml first (AUTHORIZED_EMAILS, LOCAL_PASSWORD).

## 2. Install cloudflared on that same machine
- Windows: `winget install --id Cloudflare.cloudflared`
- Linux: see https://pkg.cloudflare.com  (or `brew install cloudflared` on macOS)

## 3. Connect it to the Fouress Cloudflare account
```
cloudflared tunnel login                 # opens browser; pick the fouressynergy.com zone
cloudflared tunnel create hrdocs         # creates the tunnel + a credentials .json
cloudflared tunnel route dns hrdocs admin.fouressynergy.com   # auto-adds the DNS record
```

## 4. Point the tunnel at the app
Create `config.yml` next to the credentials file (path shown by step 3):
```
tunnel: <TUNNEL_ID_FROM_STEP_3>
credentials-file: <PATH_TO/<TUNNEL_ID>.json>
ingress:
  - hostname: admin.fouressynergy.com
    service: http://localhost:5000
  - service: http_status:404
```

## 5. Run the tunnel (and keep it running)
```
cloudflared tunnel run hrdocs
```
To run it permanently as a background service:
```
cloudflared service install            # runs on boot; survives restarts
```

## 6. Add the "Admin Login" tab on the website
In your Cloudflare-hosted site's navigation, add a menu item:
    Label: Admin Login
    Link:  https://admin.fouressynergy.com
No site rebuild needed — it's just an external link.

## Notes
- HTTPS is automatic (Cloudflare edge cert). No firewall ports are opened.
- The tool is already login-gated (your 4 emails + shared password).
- Optional extra layer: enable **Cloudflare Access** on admin.fouressynergy.com to
  require a Cloudflare login before the page even loads.
- To keep it out of search results it already isn't linked publicly; the login page
  can be left as-is.
