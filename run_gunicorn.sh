#!/bin/bash
# Skrypt do uruchomienia aplikacji Flask z gunicorn

set -e

echo "Uruchamianie aplikacji Flask z gunicorn..."

# Sprawdź czy katalog logs istnieje
mkdir -p logs

# Sprawdź czy venv istnieje, jeśli nie - utwórz
if [ ! -d "venv" ]; then
    echo "Tworzenie virtual environment..."
    python3 -m venv venv
fi

# Aktywuj venv i zainstaluj zależności
source venv/bin/activate
pip install -q -r requirements.txt

# Uruchom gunicorn
echo "Aplikacja dostępna na:"
echo "  - https://localhost (tylko z tego komputera)"
echo "  - https://192.168.0.220 (z sieci lokalnej)"
echo ""
echo "Aby zatrzymać: Ctrl+C"
echo ""

gunicorn -c gunicorn_config.py app:app
