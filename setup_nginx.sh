#!/bin/bash
# Skrypt do konfiguracji i uruchomienia nginx

set -e

echo "Konfiguracja nginx..."

# Skopiuj konfigurację
sudo cp nginx.conf /etc/nginx/sites-available/flask-app

# Utwórz symlink
sudo ln -sf /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/flask-app

# Usuń domyślną konfigurację
sudo rm -f /etc/nginx/sites-enabled/default

# Sprawdź konfigurację
echo "Testowanie konfiguracji nginx..."
sudo nginx -t

# Uruchom/przeładuj nginx
echo "Uruchamianie nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "✓ Nginx skonfigurowany i uruchomiony!"
echo "Status: sudo systemctl status nginx"
