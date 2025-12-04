# Aplikacja Flask z NGINX Reverse Proxy (HTTPS)

Projekt demonstracyjny pokazujący:
- ✅ Certyfikat SSL samo-podpisany
- ✅ NGINX skonfigurowany do obsługi **tylko** połączeń HTTPS
- ✅ NGINX jako reverse proxy dla Flask
- ✅ Aplikacja Flask uruchomiona na gunicorn lub uWSGI (NIE serwer deweloperski)
- ✅ Wyświetlanie uprawnień użytkownika/grupy pod którymi działa aplikacja
- ✅ Odczyt prawdziwego adresu IP klienta z nagłówków proxy

## 📁 Struktura projektu

```
szyfry_server/
├── app.py                  # Aplikacja Flask
├── requirements.txt        # Zależności Python
├── gunicorn_config.py      # Konfiguracja gunicorn
├── uwsgi.ini              # Konfiguracja uWSGI (opcjonalnie)
├── nginx.conf             # Konfiguracja nginx
├── generate_cert.sh       # Skrypt do generowania certyfikatu SSL
├── run_gunicorn.sh        # Skrypt uruchamiający z gunicorn
├── run_uwsgi.sh          # Skrypt uruchamiający z uWSGI (opcjonalnie)
└── README.md             # Ten plik
```

## 🚀 Instalacja i uruchomienie

### Krok 1: Generowanie certyfikatu SSL

```bash
chmod +x generate_cert.sh
./generate_cert.sh
```

To utworzy katalog `certs/` z certyfikatem samo-podpisanym ważnym przez 365 dni.

### Krok 2: Instalacja i konfiguracja NGINX

```bash
# Zainstaluj nginx (jeśli nie masz)
sudo apt install nginx  # Ubuntu/Debian
# lub
sudo dnf install nginx  # Fedora

# Skopiuj konfigurację
sudo cp nginx.conf /etc/nginx/sites-available/flask-app

# Utwórz symlink
sudo ln -s /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/

# Usuń domyślną konfigurację (opcjonalnie)
sudo rm /etc/nginx/sites-enabled/default

# Przetestuj konfigurację
sudo nginx -t

# Uruchom/przeładuj nginx
sudo systemctl restart nginx
```

### Krok 3: Uruchomienie aplikacji Flask

**Opcja A: Gunicorn (zalecane)**

```bash
chmod +x run_gunicorn.sh
./run_gunicorn.sh
```

**Opcja B: uWSGI**

Najpierw odkomentuj sekcję uWSGI w `nginx.conf` i zakomentuj sekcję gunicorn, następnie:

```bash
sudo nginx -t && sudo systemctl reload nginx
chmod +x run_uwsgi.sh
./run_uwsgi.sh
```

## 🔍 Testowanie

### Dostęp do aplikacji

Aplikacja jest dostępna **tylko** przez HTTPS:

```bash
# Główny endpoint - pokazuje wszystkie informacje
curl -k https://localhost/

# Tylko uprawnienia procesu
curl -k https://localhost/permissions

# Tylko informacje o IP klienta
curl -k https://localhost/ip

# Healthcheck
curl -k https://localhost/health
```

**Uwaga:** Flaga `-k` (lub `--insecure`) jest potrzebna dla certyfikatu samo-podpisanego.

### W przeglądarce

Otwórz: https://localhost

Przeglądarka pokaże ostrzeżenie o niezaufanym certyfikacie - to normalne dla certyfikatów samo-podpisanych. Kliknij "Zaawansowane" i "Kontynuuj mimo ryzyka".

### Sprawdzenie przekierowania HTTP → HTTPS

```bash
# To powinno przekierować na HTTPS
curl -L http://localhost/
```

## 📊 Co pokazuje aplikacja?

### 1. **Uprawnienia procesu** (`/permissions`)

```json
{
  "process_permissions": {
    "username": "malinop4",
    "groupname": "malinop4", 
    "uid": 1000,
    "gid": 1000,
    "pid": 13639,
    "ppid": 13635
  }
}
```

### 2. **Prawdziwy adres IP klienta** (`/ip`)

```json
{
  "client_ip": "192.168.0.50",
  "remote_addr": "127.0.0.1",
  "x_real_ip": "192.168.0.50",
  "x_forwarded_for": "192.168.0.50",
  "x_forwarded_proto": "https"
}
```

**Jak to działa:**
- NGINX ustawia nagłówki `X-Real-IP` i `X-Forwarded-For`
- Aplikacja Flask odczytuje te nagłówki w funkcji `get_real_ip()`
- `remote_addr` pokazuje 127.0.0.1 (połączenie od nginx)
- `x_real_ip` pokazuje prawdziwy IP klienta

## 🔐 Bezpieczeństwo SSL/TLS

Konfiguracja NGINX używa:
- ✅ TLS 1.2 i TLS 1.3
- ✅ Silne szyfry (HIGH)
- ✅ HSTS (Strict-Transport-Security)
- ✅ Przekierowanie HTTP → HTTPS
- ✅ Dodatkowe nagłówki bezpieczeństwa (X-Frame-Options, X-Content-Type-Options, etc.)

### Architektura SSL Termination:
```
Klient → [HTTPS/SSL] → NGINX (port 443)
                          ↓ [HTTP]
                       Gunicorn (127.0.0.1:8000)
                          ↓
                       Flask App
```

- **NGINX** obsługuje szyfrowanie/deszyfrowanie SSL (SSL termination)
- **Gunicorn** używa HTTP na localhost - bezpieczne, bo tylko lokalne połączenie
- Separacja obowiązków: NGINX = SSL/proxy, Gunicorn = aplikacja

## ⚙️ Konfiguracja produkcyjna

### Uruchamianie jako usługa systemd (gunicorn)

Utwórz `/etc/systemd/system/flask-app.service`:

```ini
[Unit]
Description=Flask Application with Gunicorn
After=network.target

[Service]
User=malinop4
Group=malinop4
WorkingDirectory=/home/malinop4/Dokumenty/szyfry_server
Environment="PATH=/home/malinop4/Dokumenty/szyfry_server/venv/bin"
ExecStart=/home/malinop4/Dokumenty/szyfry_server/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Uruchom:

```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl start flask-app
sudo systemctl status flask-app
```

### Zmiana użytkownika/grupy

Aby uruchomić aplikację jako inny użytkownik (np. `www-data`):

1. **W gunicorn_config.py** odkomentuj:
   ```python
   user = "www-data"
   group = "www-data"
   ```

2. **Lub w systemd service** zmień:
   ```ini
   User=www-data
   Group=www-data
   ```

3. Nadaj odpowiednie uprawnienia:
   ```bash
   sudo chown -R www-data:www-data /home/malinop4/Dokumenty/szyfry_server
   ```

## 🧪 Weryfikacja wymagań

### ✅ Certyfikat samo-podpisany
```bash
openssl x509 -in certs/server.crt -text -noout
```

### ✅ NGINX obsługuje tylko HTTPS
```bash
# HTTP przekierowuje na HTTPS
curl -I http://localhost/
# HTTP/1.1 301 Moved Permanently
# Location: https://localhost/
```

### ✅ NGINX jako reverse proxy
```bash
# Nginx przekazuje do gunicorn/uwsgi
sudo netstat -tulpn | grep nginx
sudo netstat -tulpn | grep gunicorn
```

### ✅ Uprawnienia aplikacji
```bash
curl -k https://localhost/permissions
```

### ✅ Prawdziwy adres IP
```bash
curl -k https://localhost/ip
```

## 🛑 Zatrzymywanie aplikacji

### Gunicorn
```bash
kill $(cat gunicorn.pid)
# lub Ctrl+C w terminalu
```

### uWSGI
```bash
kill $(cat uwsgi.pid)
# lub Ctrl+C w terminalu
```

### NGINX
```bash
sudo systemctl stop nginx
```

## 📝 Logi

- **NGINX**: `/var/log/nginx/flask-app-access.log` i `flask-app-error.log`
- **Gunicorn**: `./logs/gunicorn_access.log` i `gunicorn_error.log`
- **uWSGI**: `./logs/uwsgi.log`

## 🔧 Rozwiązywanie problemów

### Problem: NGINX nie może połączyć się z aplikacją

```bash
# Sprawdź czy gunicorn/uwsgi działa
ps aux | grep gunicorn
ps aux | grep uwsgi

# Sprawdź czy port 8000/8001 nasłuchuje
sudo netstat -tulpn | grep 8000
```

### Problem: Błąd uprawnień do certyfikatu

```bash
# Certyfikat musi być czytelny dla nginx
sudo chmod 644 certs/server.crt
sudo chmod 600 certs/server.key
sudo chown root:root certs/server.*
```

### Problem: SELinux blokuje połączenie

```bash
# Na systemach z SELinux
sudo setsebool -P httpd_can_network_connect 1
```

## 📚 Dodatkowe informacje

### Endpointy aplikacji:
- `/` - Pełne informacje (uprawnienia + IP + nagłówki)
- `/permissions` - Tylko uprawnienia procesu
- `/ip` - Tylko informacje o adresie IP
- `/health` - Healthcheck

### Porty:
- **443** - NGINX HTTPS (jedyne publiczne)
- **80** - NGINX HTTP (przekierowanie → 443)
- **8000** - Gunicorn (localhost only)
- **8001** - uWSGI (localhost only, opcjonalnie)
- **9191** - uWSGI stats (localhost only, opcjonalnie)

---

**Autor:** GitHub Copilot  
**Data:** 4 grudnia 2025
