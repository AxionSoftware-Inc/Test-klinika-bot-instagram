#!/bin/bash
set -e

mkdir -p /root/klinika_bot
mv /root/config.py /root/handlers.py /root/keyboards.py /root/main.py /root/requirements.txt /root/.env /root/klinika_bot/ 2>/dev/null || true
cd /root/klinika_bot

if [ ! -d "venv" ]; then
    apt-get update -y
    apt-get install -y python3-venv python3-pip
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
fi

./venv/bin/pip install -r requirements.txt

# Systemd servisini yaratish
cat << 'EOF' > /etc/systemd/system/klinika_bot.service
[Unit]
Description=Klinika Telegram Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/klinika_bot
ExecStart=/root/klinika_bot/venv/bin/python3 /root/klinika_bot/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable klinika_bot
systemctl restart klinika_bot
sleep 2
systemctl status klinika_bot --no-pager
