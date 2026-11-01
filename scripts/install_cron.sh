#!/usr/bin/env bash
# ==============================================================================
# ScoreSentinel — Daily Sanctions Feed Cron Installer (Amazon Linux 2023 EC2)
# ==============================================================================
# Installs cronie if missing, enables/starts crond, and idempotently registers
# a daily 02:00 cron job to run feeds/run_daily_feeds.py inside the API container.
# ==============================================================================

set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/transactionmonitoring}"
LOG_FILE="${LOG_FILE:-$HOME/feeds.log}"
CRON_CMD="0 2 * * * cd ${REPO_DIR} && docker compose -f docker-compose.prod.yml exec -T api python feeds/run_daily_feeds.py >> ${LOG_FILE} 2>&1"
CRON_MARKER="feeds/run_daily_feeds.py"

echo "==> [1/3] Checking cronie installation..."
if ! command -v crontab >/dev/null 2>&1; then
    echo "Installing cronie..."
    if command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y cronie
    else
        sudo yum install -y cronie
    fi
fi

echo "==> [2/3] Enabling and starting crond service..."
sudo systemctl enable crond
sudo systemctl start crond

echo "==> [3/3] Registering daily 02:00 sanctions feed cron job (idempotent)..."
EXISTING_CRON="$(crontab -l 2>/dev/null || true)"
FILTERED_CRON="$(printf '%s\n' "${EXISTING_CRON}" | grep -v "${CRON_MARKER}" || true)"

if [ -n "${FILTERED_CRON}" ]; then
    printf '%s\n%s\n' "${FILTERED_CRON}" "${CRON_CMD}" | crontab -
else
    printf '%s\n' "${CRON_CMD}" | crontab -
fi

echo "==> Cron job installed successfully. Current crontab:"
crontab -l
