# AWS EC2 Deployment Guide — ScoreSentinel API (Mumbai `ap-south-1`)

**Project:** ScoreSentinel AML Transaction Risk Scoring Engine  
**Target Region:** AWS Asia Pacific (Mumbai) — `ap-south-1`  
**Regulatory Driver:** RBI Circular on Storage of Payment System Data (2018) & DPDP Act 2023 Data Localisation Compliance  

---

## Step 1: Launch EC2 `t2.micro` in `ap-south-1` Mumbai

1. Sign in to the **AWS Management Console** and switch the region in the top-right navigation bar to **Asia Pacific (Mumbai) `ap-south-1`**.
2. Navigate to **EC2** → **Instances** → **Launch instances**.
3. Configure the instance with the following settings:
   - **Name:** `scoresentinel-api-mumbai`
   - **Application and OS Images (AMI):** **Amazon Linux 2023 AMI** (64-bit x86, Free tier eligible)
   - **Instance type:** **`t2.micro`** (Free tier eligible — 1 vCPU, 1 GiB Memory)
   - **Key pair (login):**
     - Click **Create new key pair**
     - Key pair name: `scoresentinel-mumbai`
     - Key pair type: `RSA`
     - Private key file format: **`.pem`** (for OpenSSH)
     - Click **Create key pair** and save `scoresentinel-mumbai.pem` securely on your machine.
   - **Network settings (Security Group):**
     - Create a new security group named `scoresentinel-sg` with the following **Inbound Rules**:

| Type | Protocol | Port Range | Source | Purpose |
|---|---|---|---|---|
| **SSH** | TCP | `22` | My IP (or `0.0.0.0/0`) | SSH administrative access |
| **Custom TCP** | TCP | `5000` | `0.0.0.0/0` | ScoreSentinel Flask/Gunicorn API |
| **HTTPS** | TCP | `443` | `0.0.0.0/0` | HTTPS traffic (Reverse Proxy / TLS) |

4. Keep default storage (`8 GiB gp3` root volume) and click **Launch instance**.
5. Once the instance state is **Running**, copy its **Public IPv4 address** (e.g., `13.233.xx.xx`).

### Connect to the EC2 Instance via SSH

From your local terminal (PowerShell or Bash):

```bash
chmod 400 scoresentinel-mumbai.pem
ssh -i "scoresentinel-mumbai.pem" ec2-user@<EC2-PUBLIC-IP>
```

---

## Step 2: Install Docker on EC2

Run the following commands inside your EC2 SSH session to update packages, install Docker, start the Docker daemon, and grant `ec2-user` permissions:

```bash
sudo yum update -y
sudo yum install docker git -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

> **Note:** Log out and log back in (or run `newgrp docker`) so the `docker` group membership takes effect without requiring `sudo`.

```bash
newgrp docker
docker --version
```

---

## Step 3: Clone Repository

Clone the ScoreSentinel repository from GitHub and navigate into the `api` directory:

```bash
git clone https://github.com/atulkrishnan18-wq/transactionmonitoring.git
cd transactionmonitoring/api
```

Stage the shared engine modules (`engine/`, `feeds/`, `rules/`, `scoring_engine.py`, `requirements.txt`) into the `api/` Docker build context so the container includes all scoring and sanctions modules:

```bash
cp -r ../engine ../feeds ../rules ../scoring_engine.py ../requirements.txt .
```

---

## Step 4: Set Environment Variables

Create the production `.env` file in `transactionmonitoring/api/` by copying the `.env.production` template and filling in your live values:

```bash
cp .env.production .env
nano .env
```

Populate `.env` with your production credentials:

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
DEMO_API_KEY=SCORESENTINEL_DEMO_2027
READ_API_KEY=SCORESENTINEL_READ_2027
FLASK_DEBUG=false
FLASK_RUN_HOST=0.0.0.0
ALLOWED_ORIGINS=https://transactionmonitoring.vercel.app
EC2_PUBLIC_IP=<EC2-PUBLIC-IP>
REPORTING_ENTITY_NAME=ScoreSentinel Financial Services Pvt Ltd
REPORTING_ENTITY_TYPE=NBFC
PRINCIPAL_OFFICER_NAME=Atul Krishnan, CAMS
PRINCIPAL_OFFICER_DESIGNATION=Principal Officer & Head of AML Compliance
REPORTING_ENTITY_ADDRESS=Mumbai, Maharashtra, India
REPORTING_ENTITY_FIU_REG_NO=FIUIND-NBFC-2026-001
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## Step 5: Build and Run Docker Container

Build the production Docker image and launch the container in detached mode on port `5000`:

```bash
docker build -t scoresentinel-api .
docker run -d -p 5000:5000 \
  --env-file .env \
  --name scoresentinel \
  scoresentinel-api
```

Check that the container is running:

```bash
docker ps
```

---

## Step 6: Verify Deployment

Test the local health endpoint on the EC2 instance:

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{"engine":"1.0","status":"ok"}
```

Also verify external reachability from your local machine using the EC2 Public IP:

```bash
curl http://<EC2-PUBLIC-IP>:5000/api/health
```

---

## Step 7: Set Up Auto-Restart on Reboot

Configure Docker to automatically restart the `scoresentinel` container if the process crashes or the EC2 instance reboots, and enable the Docker systemd service on boot:

```bash
docker update --restart unless-stopped scoresentinel
sudo systemctl enable docker
```

---

## Step 8: Update Vercel Environment Variable

Point the React dashboard hosted on Vercel to the new AWS Mumbai EC2 endpoint:

1. Open the **[Vercel Dashboard](https://vercel.com/dashboard)** and select the **`transactionmonitoring`** project.
2. Navigate to **Settings** → **Environment Variables**.
3. Locate `REACT_APP_API_URL` and update its value to your new EC2 endpoint:
   ```text
   http://<EC2-PUBLIC-IP>:5000
   ```
   *(Or `https://<your-custom-domain>` if fronted by an HTTPS load balancer / CloudFront / Nginx TLS termination).*
4. Navigate to the **Deployments** tab, click the **`...`** menu on the latest deployment, and select **Redeploy** so the updated environment variable is baked into the production React bundle.

---

## Future Automated Updates (`deploy_aws.sh`)

Whenever new commits are pushed to GitHub, you can redeploy in one command using [`scripts/deploy_aws.sh`](file:///C:/Users/Roots%20and%20Arrow/transactionmonitoring/scripts/deploy_aws.sh):

```bash
# Run from your local machine:
EC2_HOST="<EC2-PUBLIC-IP>" PEM_KEY="./scoresentinel-mumbai.pem" bash scripts/deploy_aws.sh

# Or run directly inside the EC2 instance:
bash ~/transactionmonitoring/scripts/deploy_aws.sh --on-server
```
