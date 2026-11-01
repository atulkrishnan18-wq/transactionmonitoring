# ScoreSentinel — AWS EC2 Mumbai (`ap-south-1`) Hardened Deployment Guide

**Purpose:** India-hosted deployment to support clients' own data-residency requirements.
**Target Region:** AWS Asia Pacific (Mumbai) — `ap-south-1`
**API Domain:** `https://api.chainsutra.in` (TLS terminated by Caddy 2 reverse proxy)
**Frontend Origin:** `https://transactionmonitoring.vercel.app`

---

> [!WARNING]
> **Database Location & Data-Residency Disclosure**
> Hosting the Flask API on AWS EC2 Mumbai (`ap-south-1`) places only the **compute layer** in India. True end-to-end India data residency requires your PostgreSQL database (`DATABASE_URL`) to **also** reside in `ap-south-1` (Mumbai).
>
> Run the included region inspector before claiming India data residency:
> ```bash
> python3 scripts/check_db_region.py
> ```
> - If your `DATABASE_URL` hostname contains `ap-northeast-1` (Tokyo) or `ap-southeast-1` (Singapore), the script prints `NOT India-hosted: detected <region>`.
> - Until the database itself is migrated to `ap-south-1` (either a new Supabase project created in **Mumbai `ap-south-1`** or **AWS RDS for PostgreSQL in `ap-south-1`**), always describe the deployment externally as: **"API hosted in Mumbai; database migration in progress."**

---

## Step 1: Launch EC2 Instance in `ap-south-1` (Mumbai)

1. Sign in to the [AWS Management Console](https://ap-south-1.console.aws.amazon.com/ec2/home?region=ap-south-1) and confirm the top-right region selector is **Asia Pacific (Mumbai) `ap-south-1`**.
2. Click **Launch instance** and configure:
   - **Name:** `scoresentinel-api-mumbai`
   - **AMI:** **Amazon Linux 2023 AMI** (choose `x86_64` for `t3.small`, or `arm64` if launching Graviton `t4g.small`).
   - **Instance Type (2 GiB RAM required):**
     - **`t3.small`** (2 vCPU, 2 GiB RAM — **x86_64** AMI), **or**
     - **`t4g.small`** (2 vCPU, 2 GiB RAM — **ARM64 / Graviton** AMI, lower cost).
     - *Note: Do not use `t2.micro` (1 GiB RAM) in production; Gunicorn workers + sanctions XML parsing + ReportLab PDF generation + Caddy can trigger Linux OOM kills on 1 GiB instances.*
   - **Key Pair (login):**
     - Create a new RSA `.pem` key pair named `scoresentinel-mumbai` and save `scoresentinel-mumbai.pem` locally.
   - **Network Settings (Security Group — `scoresentinel-sg`):**
     Configure **only** the following three inbound rules (do **not** open port `5000` to the internet; `api` is only reachable internally by `caddy` over the Docker bridge network):

     | Type | Protocol | Port Range | Source | Purpose |
     |---|---|---|---|---|
     | **SSH** | TCP | `22` | **My IP** (`<your-ip>/32`) | Restricted administrative SSH access |
     | **HTTP** | TCP | `80` | **Anywhere-IPv4** (`0.0.0.0/0`) | Let's Encrypt HTTP-01 challenge & HTTP->HTTPS redirect |
     | **HTTPS** | TCP | `443` | **Anywhere-IPv4** (`0.0.0.0/0`) | Public HTTPS API traffic via Caddy |

   - **Configure Storage (Root Volume):**
     - Set root EBS volume to **`30 GiB` `gp3`** (absorbs Docker build layer cache, container logs, sanctions feed snapshots, and generated STR PDFs).
3. Click **Launch instance**.

---

## Step 2: Allocate an Elastic IP & Configure DNS (`api.chainsutra.in`)

### 2.1 Allocate and Associate an Elastic IP
Without an Elastic IP, stopping and starting the EC2 instance changes its public IPv4 address and breaks DNS.
1. In the EC2 Console left sidebar, go to **Network & Security -> Elastic IPs**.
2. Click **Allocate Elastic IP address** -> **Allocate**.
3. Select the newly allocated Elastic IP -> **Actions -> Associate Elastic IP address**.
4. Choose **Instance**, select `scoresentinel-api-mumbai`, and click **Associate**.

### 2.2 Create the DNS `A` Record
1. Open your DNS provider for `chainsutra.in`.
2. Create (or update) an **`A` record**:
   - **Host / Name:** `api` (resolving to `api.chainsutra.in`)
   - **Type:** `A`
   - **Value / Target:** `<Your-Elastic-IP>`
   - **TTL:** `300` (5 minutes)
   - *If using Cloudflare DNS, set Proxy status to **DNS only (grey cloud)** so Caddy can complete Let's Encrypt TLS issuance directly.*
3. **Wait for DNS resolution before starting Docker Compose** (otherwise Let's Encrypt certificate issuance will fail):
   ```bash
   nslookup api.chainsutra.in
   ```
   Confirm it returns your EC2 Elastic IP before proceeding to Step 6.

---

## Step 3: Set Key Permissions & SSH into EC2

Lock down permissions on `scoresentinel-mumbai.pem` before connecting:

- **Windows (PowerShell):**
  ```powershell
  icacls .\scoresentinel-mumbai.pem /inheritance:r
  icacls .\scoresentinel-mumbai.pem /grant:r "$($env:USERNAME):(R)"
  ssh -i .\scoresentinel-mumbai.pem ec2-user@<YOUR_ELASTIC_IP>
  ```

- **macOS / Linux:**
  ```bash
  chmod 400 ~/Downloads/scoresentinel-mumbai.pem
  ssh -i ~/Downloads/scoresentinel-mumbai.pem ec2-user@<YOUR_ELASTIC_IP>
  ```

---

## Step 4: Install Docker, Docker Compose Plugin & Git on Amazon Linux 2023

Run the following on the EC2 instance:

```bash
sudo dnf update -y
sudo dnf install -y docker git cronie
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# Install Docker Compose v2 CLI plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins
ARCH="$(uname -m)"
sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-${ARCH}" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Re-login so docker group membership takes effect
exit
```

Reconnect via SSH and verify:
```bash
docker --version
docker compose version
```

---

## Step 5: Clone Repository & Configure `.env`

1. Clone the repository and switch to the deployment branch:
   ```bash
   git clone https://github.com/atulkrishnan18-wq/transactionmonitoring.git
   cd ~/transactionmonitoring
   git checkout aws-hardening
   ```

2. Generate two distinct, cryptographically random API keys (at least 24 characters each; 32-byte URL-safe tokens are 43 characters):
   ```bash
   python3 -c "import secrets; print('DEMO_API_KEY=' + secrets.token_urlsafe(32)); print('READ_API_KEY=' + secrets.token_urlsafe(32))"
   ```
   > [!IMPORTANT]
   > `api/app.py` validates `DEMO_API_KEY` and `READ_API_KEY` at startup and **refuses to start** if either key is missing, shorter than 24 characters, identical to the other key, or set to any placeholder/retired default (`CHANGE_ME...`).

3. Copy the root `.env.production` template to `.env` and populate your real values:
   ```bash
   cp .env.production .env
   chmod 600 .env
   nano .env
   ```

   Your `.env` file in `/home/ec2-user/transactionmonitoring/.env` should follow this structure:
   ```env
   DATABASE_URL=CHANGE_ME
   # Generate keys with: python -c "import secrets; print(secrets.token_urlsafe(32))"
   DEMO_API_KEY=CHANGE_ME_GENERATE_NEW_KEY
   READ_API_KEY=CHANGE_ME_GENERATE_NEW_KEY
   FLASK_DEBUG=false
   FLASK_RUN_HOST=0.0.0.0
   API_DOMAIN=api.chainsutra.in
   ALLOWED_ORIGINS=https://transactionmonitoring.vercel.app
   REPORTING_ENTITY_NAME=DEMO ENTITY - NOT A REGISTERED REPORTING ENTITY
   REPORTING_ENTITY_TYPE=DEMO
   PRINCIPAL_OFFICER_NAME=Demo Principal Officer
   PRINCIPAL_OFFICER_DESIGNATION=Demo
   REPORTING_ENTITY_ADDRESS=Demo address
   REPORTING_ENTITY_FIU_REG_NO=DEMO-ONLY
   ```

4. Check the database region reported by your `DATABASE_URL`:
   ```bash
   python3 scripts/check_db_region.py
   ```

---

## Step 6: Build and Start Services with Docker Compose

`docker-compose.prod.yml` builds the API image directly from the repository root using `api/Dockerfile.aws` (no manual `cp -r` steps needed), keeps port `5000` internal (`expose: ["5000"]`), mounts `./feeds:/app/feeds` for daily sanctions feed persistence, and runs **Caddy 2** on ports `80` and `443` for automatic HTTPS.

```bash
cd ~/transactionmonitoring
docker compose -f docker-compose.prod.yml up -d --build
```

Verify both containers are running and healthy:
```bash
docker compose -f docker-compose.prod.yml ps
curl -i https://api.chainsutra.in/api/health
```
Expected response:
```json
{"engine":"1.0","status":"ok"}
```

---

## Step 7: Install Daily Sanctions Feed Cron Job (`02:00` Daily)

Install the automated daily sanctions feed updater (`feeds/run_daily_feeds.py`) on the EC2 host:

```bash
cd ~/transactionmonitoring
bash scripts/install_cron.sh
```

This script ensures `cronie` (`crond`) is enabled and idempotently adds:
```cron
0 2 * * * cd /home/ec2-user/transactionmonitoring && docker compose -f docker-compose.prod.yml exec -T api python feeds/run_daily_feeds.py >> /home/ec2-user/feeds.log 2>&1
```
Because `./feeds:/app/feeds` is mounted in `docker-compose.prod.yml`, `ofac_previous.json`, `un_previous.json`, `ofac_delta_log.txt`, and `un_delta_log.txt` persist on the host across container rebuilds.

---

## Step 8: Update Vercel Frontend Environment Variables

> [!IMPORTANT]
> **Why HTTPS (`https://api.chainsutra.in`) is Mandatory for Vercel**
> Your React dashboard is served over **HTTPS** (`https://transactionmonitoring.vercel.app`). Modern browsers strictly enforce **Mixed Content blocking**: an HTTPS webpage is forbidden from making `fetch`/`XHR` requests to an insecure `http://<EC2_IP>:5000` endpoint. Always set `REACT_APP_API_URL` to **`https://api.chainsutra.in`** — never `http://IP:5000`.

1. Open the [Vercel Dashboard](https://vercel.com/dashboard) -> select your **transactionmonitoring** project -> **Settings -> Environment Variables**.
2. Update the following variables for **Production, Preview, and Development**:
   - `REACT_APP_API_URL` = `https://api.chainsutra.in`
   - `REACT_APP_READ_API_KEY` = `<your new READ_API_KEY from .env>`
   - `REACT_APP_DEMO_API_KEY` = `<your new DEMO_API_KEY from .env>`
3. Go to **Deployments** -> click **Redeploy** on the latest deployment so the React build embeds the updated environment variables.

---

## First-Time Verification Checklist

- [ ] **New Keys Generated:** `DEMO_API_KEY` and `READ_API_KEY` were freshly generated via `secrets.token_urlsafe(32)`, are distinct, and match between EC2 `.env` and Vercel Environment Variables.
- [ ] **No Secrets Committed:** `git status` and `git diff` confirm `.env` is untracked and no real credentials exist in tracked files.
- [ ] **HTTPS Health Check Passes:** `curl -fsS https://api.chainsutra.in/api/health` returns `{"engine":"1.0","status":"ok"}` with a valid Let's Encrypt certificate.
- [ ] **Port 5000 Closed Externally:** `curl --connect-timeout 5 http://api.chainsutra.in:5000/api/health` times out / is refused.
- [ ] **Dashboard Loads Alerts:** Opening `https://transactionmonitoring.vercel.app` loads the alert queue over HTTPS with no browser console CORS or Mixed Content errors.
- [ ] **STR PDF Shows Demo Header:** Generating an STR PDF while `REPORTING_ENTITY_FIU_REG_NO=DEMO-ONLY` prints `DEMONSTRATION DOCUMENT - NOT A REGISTERED FIU-IND FILING` at the top of every page.

---

## Troubleshooting

### 1. TLS Certificate Not Issued by Caddy (`SSL_ERROR_INTERNAL_ERROR_ALERT` / Timeout)
- **Cause:** DNS `A` record for `api.chainsutra.in` does not yet resolve to the EC2 Elastic IP, or Security Group ports `80`/`443` are blocked.
- **Fix:**
  1. Check `nslookup api.chainsutra.in` returns your Elastic IP.
  2. Confirm AWS Security Group inbound rules allow TCP `80` and `443` from `0.0.0.0/0`.
  3. Inspect Caddy logs: `docker compose -f docker-compose.prod.yml logs caddy`.

### 2. CORS Error in Browser Console
- **Cause:** `ALLOWED_ORIGINS` in EC2 `.env` does not match the exact frontend origin (no trailing slash).
- **Fix:** Ensure `ALLOWED_ORIGINS=https://transactionmonitoring.vercel.app` in `.env`, then restart:
  ```bash
  docker compose -f docker-compose.prod.yml up -d
  ```

### 3. Out-of-Memory (OOM) / Instance Freezes During Build or Feed Run
- **Cause:** Running on a 1 GiB instance (`t2.micro` / `t3.micro`) without swap.
- **Fix:** Upgrade instance type to `t3.small` or `t4g.small` (2 GiB RAM), or add a 2 GiB swap file on Amazon Linux 2023:
  ```bash
  sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
  sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
  ```

### 4. `scoresentinel-api` Container Keep Restarting (`Restarting (1)`)
- **Cause:** Startup key validation failed in `api/app.py` (missing key, `< 24` chars, duplicate keys, or `CHANGE_ME` placeholder still present in `.env`).
- **Fix:** Check the exact `RuntimeError` message with:
  ```bash
  docker compose -f docker-compose.prod.yml logs api
  ```
  Update `DEMO_API_KEY` and `READ_API_KEY` in `.env` with freshly generated 32-byte tokens and run `docker compose -f docker-compose.prod.yml up -d`.
