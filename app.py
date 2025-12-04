#!/usr/bin/env python3
"""
Aplikacja Flask demonstrująca:
- Odczyt prawdziwego adresu IP klienta z nagłówków proxy
- Wyświetlanie uprawnień pod jakimi działa aplikacja
"""

import os
import pwd
import grp
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_process_info():
    """Zwraca informacje o uprawnieniach procesu"""
    uid = os.getuid()
    gid = os.getgid()
    
    try:
        user_info = pwd.getpwuid(uid)
        username = user_info.pw_name
    except KeyError:
        username = f"UID:{uid}"
    
    try:
        group_info = grp.getgrgid(gid)
        groupname = group_info.gr_name
    except KeyError:
        groupname = f"GID:{gid}"
    
    return {
        'uid': uid,
        'gid': gid,
        'username': username,
        'groupname': groupname,
        'pid': os.getpid(),
        'ppid': os.getppid()
    }


def get_real_ip():
    """
    Odczytuje prawdziwy adres IP klienta.
    Sprawdza nagłówki ustawiane przez nginx (X-Real-IP, X-Forwarded-For)
    """
    # Nginx ustawia X-Real-IP
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    
    # Alternatywnie sprawdza X-Forwarded-For
    if request.headers.get('X-Forwarded-For'):
        # Bierze pierwszy IP z listy (oryginalny klient)
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    # Fallback na bezpośrednie połączenie
    return request.remote_addr


@app.route('/')
def index():
    """Główny endpoint pokazujący wszystkie informacje"""
    process_info = get_process_info()
    real_ip = get_real_ip()
    
    return jsonify({
        'message': 'Flask Application - Secure NGINX Proxy',
        'process_info': {
            'user': process_info['username'],
            'group': process_info['groupname'],
            'uid': process_info['uid'],
            'gid': process_info['gid'],
            'pid': process_info['pid'],
            'parent_pid': process_info['ppid']
        },
        'client_info': {
            'real_ip': real_ip,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'protocol': request.headers.get('X-Forwarded-Proto', 'unknown')
        },
        'headers': dict(request.headers)
    })


@app.route('/health')
def health():
    """Endpoint healthcheck"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/permissions')
def permissions():
    """Endpoint pokazujący tylko uprawnienia procesu"""
    process_info = get_process_info()
    return jsonify({
        'process_permissions': process_info
    })


@app.route('/ip')
def ip_info():
    """Endpoint pokazujący tylko informacje o IP klienta"""
    return jsonify({
        'client_ip': get_real_ip(),
        'remote_addr': request.remote_addr,
        'x_real_ip': request.headers.get('X-Real-IP'),
        'x_forwarded_for': request.headers.get('X-Forwarded-For'),
        'x_forwarded_proto': request.headers.get('X-Forwarded-Proto')
    })


if __name__ == '__main__':
    # Ten blok nie będzie używany - aplikacja będzie uruchamiana przez gunicorn/uwsgi
    # Pozostawiony tylko dla celów testowych
    print("UWAGA: To jest serwer deweloperski. Użyj gunicorn lub uwsgi w produkcji!")
    app.run(host='127.0.0.1', port=5000, debug=True)
