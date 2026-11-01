#!/usr/bin/env bash
# ==============================================================================
# ScoreSentinel — AWS EC2 Mumbai (ap-south-1) Deployment Script (Docker Compose)
# ==============================================================================
# Usage:
#   1. Run from local machine (SSH into EC2 and deploy):
#      EC2_HOST=ec2-xx-xx-xx-xx.ap-south-1.compute.amazonaws.com \
#      SSH_KEY=~/.ssh/scoresentinel-mumbai.pem \
#      API_DOMAIN=api.chainsutra.in \
#      ./scripts/deploy_aws.sh
#
#   2. Run directly on the EC2 instance:
#      ./scripts/deploy_aws.sh --on-server
# ==============================================================================

set -euo pipefail

EC2_USER="${EC2_USER:-ec2-user}"
EC2_HOST="${EC2_HOST:-}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/scoresentinel-mumbai.pem}"
REMOTE_REPO_DIR="${REMOTE_REPO_DIR:-$HOME/transactionmonitoring}"
GIT_BRANCH="${GIT_BRANCH:-aws-hardening}"
API_DOMAIN="${API_DOMAIN:-api.chainsutra.in}"

deploy_on_server() {
    echo "==> [1/4] Navigating to repository at ${REMOTE_REPO_DIR}..."
    cd "${REMOTE_REPO_DIR}"

    if [ ! -f ".env" ]; then
        echo "ERROR: .env file not found in ${REMOTE_REPO_DIR}."
        echo "Copy .env.production to .env and populate production secrets first."
        exit 1
    fi

    # Load API_DOMAIN from .env if present
    ENV_DOMAIN="$(grep -E '^API_DOMAIN=' .env | tail -n 1 | cut -d'=' -f2- | tr -d '\r"'\''' || true)"
    if [ -n "${ENV_DOMAIN}" ]; then
        API_DOMAIN="${ENV_DOMAIN}"
    fi

    echo "==> [2/4] Pulling latest code from GitHub (branch: ${GIT_BRANCH})..."
    git fetch origin
    git checkout "${GIT_BRANCH}"
    git pull origin "${GIT_BRANCH}"

    echo "==> [3/4] Building and starting services via docker-compose.prod.yml..."
    docker compose -f docker-compose.prod.yml build
    docker compose -f docker-compose.prod.yml up -d

    echo "==> [4/4] Verifying HTTPS health endpoint at https://${API_DOMAIN}/api/health ..."
    sleep 5
    HEALTH_RESPONSE="$(curl -fsS --max-time 15 "https://${API_DOMAIN}/api/health" || true)"
    if echo "${HEALTH_RESPONSE}" | grep -q '"status"'; then
        echo "Health response: ${HEALTH_RESPONSE}"
        echo "PASS"
    else
        echo "Health check failed or returned unexpected payload: ${HEALTH_RESPONSE}"
        docker compose -f docker-compose.prod.yml logs --tail 40
        echo "FAIL"
        exit 1
    fi
}

if [[ "${1:-}" == "--on-server" ]]; then
    deploy_on_server
else
    if [[ -z "${EC2_HOST}" ]]; then
        echo "Usage: EC2_HOST=<ec2-ip-or-dns> SSH_KEY=<path-to-pem> ./scripts/deploy_aws.sh"
        echo "   or: ./scripts/deploy_aws.sh --on-server  (when already SSH'd into EC2)"
        exit 1
    fi

    echo "==> Connecting to ${EC2_USER}@${EC2_HOST} (ap-south-1 Mumbai)..."
    ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=accept-new "${EC2_USER}@${EC2_HOST}" \
        "GIT_BRANCH='${GIT_BRANCH}' API_DOMAIN='${API_DOMAIN}' bash -s" << 'EOF'
set -euo pipefail
REPO_DIR="$HOME/transactionmonitoring"
if [ ! -d "$REPO_DIR" ]; then
    git clone https://github.com/atulkrishnan18-wq/transactionmonitoring.git "$REPO_DIR"
fi
cd "$REPO_DIR"
git fetch origin
git checkout "${GIT_BRANCH:-aws-hardening}"
git pull origin "${GIT_BRANCH:-aws-hardening}"
bash scripts/deploy_aws.sh --on-server
EOF
fi
