#!/usr/bin/env bash
# ==============================================================================
# ScoreSentinel — AWS EC2 (ap-south-1 Mumbai) Automated Deployment Script
# ==============================================================================
# Usage (from local machine via SSH):
#   EC2_HOST="ec2-13-233-xx-xx.ap-south-1.compute.amazonaws.com" \
#   PEM_KEY="~/.ssh/scoresentinel-mumbai.pem" \
#   ./scripts/deploy_aws.sh
#
# Or run directly on the EC2 instance:
#   ./scripts/deploy_aws.sh --on-server
# ==============================================================================

set -euo pipefail

EC2_USER="${EC2_USER:-ec2-user}"
EC2_HOST="${EC2_HOST:-}"
PEM_KEY="${PEM_KEY:-~/.ssh/scoresentinel-mumbai.pem}"
APP_DIR="${APP_DIR:-~/transactionmonitoring}"
CONTAINER_NAME="scoresentinel"
IMAGE_NAME="scoresentinel-api"

REMOTE_COMMANDS=$(cat << 'EOF'
set -euo pipefail

echo "============================================================"
echo " ScoreSentinel AWS EC2 (ap-south-1 Mumbai) Deployment"
echo "============================================================"

# 1. Pull latest code from GitHub
if [ ! -d "$HOME/transactionmonitoring" ]; then
    echo "[1/5] Cloning repository..."
    git clone https://github.com/atulkrishnan18-wq/transactionmonitoring.git "$HOME/transactionmonitoring"
fi

cd "$HOME/transactionmonitoring"
echo "[1/5] Pulling latest changes from GitHub (main)..."
git fetch origin main
git reset --hard origin/main

# 2. Stage engine modules into api/ build context
echo "[2/5] Preparing Docker build context in api/..."
cp -r engine feeds rules scoring_engine.py requirements.txt api/

cd "$HOME/transactionmonitoring/api"

if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found in api/. Copying template from .env.production..."
    cp .env.production .env
    echo "Please populate api/.env with production secrets before traffic cutover."
fi

# 3. Rebuild Docker image
echo "[3/5] Building Docker image: scoresentinel-api..."
sudo docker build -t scoresentinel-api .

# 4. Restart the Docker container service
echo "[4/5] Restarting container: scoresentinel..."
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^scoresentinel$"; then
    sudo docker stop scoresentinel || true
    sudo docker rm scoresentinel || true
fi

sudo docker run -d \
    -p 5000:5000 \
    --env-file .env \
    --restart unless-stopped \
    --name scoresentinel \
    scoresentinel-api

# 5. Verify health endpoint
echo "[5/5] Waiting for Gunicorn workers to initialise..."
sleep 4
echo "Checking health endpoint: http://localhost:5000/api/health"
HEALTH_RESP=$(curl -sS http://localhost:5000/api/health)
echo "Health response: $HEALTH_RESP"

if echo "$HEALTH_RESP" | grep -q '"status":"ok"'; then
    echo "✅ Deployment successful! ScoreSentinel API is live on port 5000."
else
    echo "❌ Health check did not return expected status. Container logs:"
    sudo docker logs --tail 50 scoresentinel
    exit 1
fi
EOF
)

if [[ "${1:-}" == "--on-server" ]] || [[ -z "$EC2_HOST" ]]; then
    if [[ -z "$EC2_HOST" ]] && [[ "${1:-}" != "--on-server" ]]; then
        echo "Connecting to EC2 instance..."
        echo "Note: Set EC2_HOST and PEM_KEY environment variables to run over SSH,"
        echo "or pass --on-server when executing directly inside the EC2 instance."
        exit 1
    fi
    bash -c "$REMOTE_COMMANDS"
else
    echo "Connecting to ${EC2_USER}@${EC2_HOST} (ap-south-1 Mumbai)..."
    ssh -i "$PEM_KEY" -o StrictHostKeyChecking=accept-new "${EC2_USER}@${EC2_HOST}" "$REMOTE_COMMANDS"
fi
