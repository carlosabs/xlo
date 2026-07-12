import logging
import time
import requests
from curl_cffi import requests as curl_requests

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.olx.com.br/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def buscar_pagina(url, tentativas=3):
    for i in range(1, tentativas + 1):
        try:
            resp = curl_requests.get(url, impersonate="chrome124", timeout=20)
            if resp.status_code == 200:
                return resp.text
            log.warning("Tentativa %d/%d — HTTP %d", i, tentativas, resp.status_code)
        except Exception as e:
            log.warning("Tentativa %d/%d — erro: %s", i, tentativas, e)
        if i < tentativas:
            time.sleep(2 * i)
    return None


def buscar_endereco(cep):
    """Consulta a ViaCEP e retorna logradouro, bairro, localidade, uf.
    Retorna dict vazio se o CEP for inválido ou não encontrado.
    """
    cep_limpo = cep.replace("-", "").replace(" ", "").strip()
    if len(cep_limpo) != 8 or not cep_limpo.isdigit():
        return {}
    try:
        resp = SESSION.get(
            "https://viacep.com.br/ws/{}/json/".format(cep_limpo),
            timeout=10,
        )
        data = resp.json()
        if "erro" not in data:
            return data  # logradouro, bairro, localidade, uf, etc.
        log.debug("ViaCEP: CEP não encontrado: %s", cep_limpo)
    except Exception as e:
        log.warning("ViaCEP falhou para %s: %s", cep_limpo, e)
    return {}