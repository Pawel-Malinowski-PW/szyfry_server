# Konfiguracja gunicorn dla aplikacji Flask

# Adres i port na którym nasłuchuje gunicorn
bind = "127.0.0.1:8000"

# Liczba procesów worker
workers = 4

# Typ workera
worker_class = "sync"

# Timeout
timeout = 30

# Nazwa procesu
proc_name = "flask_app"

# Logi
accesslog = "./logs/gunicorn_access.log"
errorlog = "./logs/gunicorn_error.log"
loglevel = "info"

# Daemon mode - ustawione na False, żeby widzieć logi
daemon = False

# PID file
pidfile = "./gunicorn.pid"

# Użytkownik i grupa (opcjonalne - zostaw zakomentowane jeśli uruchamiasz jako zwykły użytkownik)
# user = "www-data"
# group = "www-data"
