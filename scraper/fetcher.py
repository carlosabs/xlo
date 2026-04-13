import logging
import time
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


def buscar_pagina(url, tentativas=3):
    for i in range(1, tentativas + 1):
        try:
            resp = SESSION.get(url, timeout=20)
            if resp.status_code == 200:
                return resp.text
            log.warning("Tentativa %d/%d — HTTP %d: %s", i, tentativas, resp.status_code, url)
        except Exception as e:
            log.warning("Tentativa %d/%d — erro: %s", i, tentativas, e)

        if i < tentativas:
            time.sleep(2 * i)

    log.error("Falhou após %d tentativas: %s", tentativas, url)
    return None
