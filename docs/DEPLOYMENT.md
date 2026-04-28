# 🚀 Deployment Guide

Production deployment guide for PremiumHubBot.

---

## Server Requirements

### Minimum

- CPU: 1 core
- RAM: 512 MB
- Storage: 5 GB
- OS: Ubuntu 20.04+

### Recommended

- CPU: 2 cores
- RAM: 2 GB
- Storage: 20 GB
- OS: Ubuntu 22.04 LTS

---

## Quick Deploy

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3.11 python3.11-venv git

# 3. Clone repo
git clone https://github.com/yourusername/PremiumHubBot.git
cd PremiumHubBot

# 4. Setup venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure .env
cp .env.example .env
nano .env

# 6. Run
python -m bot.main
```

---

## Systemd Service

Create `/etc/systemd/system/premiumhubbot.service`:

```ini
[Unit]
Description=PremiumHubBot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/PremiumHubBot
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable premiumhubbot
sudo systemctl start premiumhubbot

# Check status
sudo systemctl status premiumhubbot
```

---

## Monitoring

```bash
# Logs
journalctl -u premiumhubbot -f

# Status
sudo systemctl status premiumhubbot

# Restart
sudo systemctl restart premiumhubbot
```

---

## Backup

```bash
# Manual backup
cp bot/database.db backups/backup_$(date +%Y%m%d).db

# Auto backup
# Already configured in jobs/auto_backup.py
```

---

## Security

```bash
# Firewall
sudo ufw allow ssh
sudo ufw enable

# Update .env permissions
chmod 600 .env
```

---

<div align="center">
  <b>🚀 Production Ready</b>
</div>
