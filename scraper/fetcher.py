"""
Requisicoes HTTP ao OLX.
"""
import logging
import requests

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.olx.com.br/",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def buscar_pagina(url):
    try:
        resp = SESSION.get(url, timeout=20)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        log.error("Erro ao buscar %s: %s", url, e)
        return None
