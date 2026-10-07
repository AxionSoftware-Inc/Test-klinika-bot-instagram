#!/bin/bash
set -e

/root/klinika_bot/venv/bin/pip install fastapi uvicorn httpx

cat << 'EOF' > /etc/systemd/system/instagram_webhook.service
[Unit]
Description=Instagram Meta Webhook Service for Clinic
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/klinika_bot
ExecStart=/root/klinika_bot/venv/bin/uvicorn instagram_webhook:app --host 127.0.0.1 --port 8050
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable instagram_webhook
systemctl restart instagram_webhook
sleep 2
systemctl status instagram_webhook --no-pager
