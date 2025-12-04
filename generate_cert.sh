#!/bin/bash
# Skrypt do generowania certyfikatu samo-podpisanego dla nginx

set -e

# Katalog na certyfikaty
CERT_DIR="./certs"
mkdir -p "$CERT_DIR"

# Nazwa plików certyfikatu
KEY_FILE="$CERT_DIR/server.key"
CERT_FILE="$CERT_DIR/server.crt"

echo "Generowanie certyfikatu samo-podpisanego SSL..."

# Generowanie klucza prywatnego i certyfikatu
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/C=PL/ST=Poland/L=Warsaw/O=Development/OU=IT/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:192.168.0.220"

# Ustawienie odpowiednich uprawnień
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo ""
echo "  Klucz prywatny: $KEY_FILE"
echo "  Certyfikat: $CERT_FILE"
echo ""
