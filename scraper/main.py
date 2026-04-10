"""
Ponto de entrada do scraper.
Orquestra busca, parse, deduplicacao, notificacao e sync com o droplet.

Uso:
    python main.py                 # execucao normal
    python main.py --testar-email  # envia email com os ultimos 5 anuncios do banco
"""
import logging
import random
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from config import CONFIG
from db import DB_PATH, init_db, ja_visto, salvar
from fetcher import buscar_pagina
from notifier import enviar_email
from parser import extrair_anuncios

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).resolve().parent / "scraper.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def testar_email():
    """Envia email com os ultimos 5 anuncios do banco para testar as credenciais."""
    if not DB_PATH.exists():
        log.error("Banco nao encontrado — rode o scraper primeiro")
        return

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT * FROM anuncios ORDER BY visto_em DESC LIMIT 5"
    ).fetchall()
    con.close()

    if not rows:
        log.error("Nenhum anuncio no banco ainda")
        return

    anuncios = [dict(r) for r in rows]
    log.info("Enviando email de teste com %d anuncios...", len(anuncios))
    enviar_email(anuncios)
    log.info("Pronto — verifique sua caixa de entrada")


def sincronizar():
    cfg = CONFIG.get("sync", {})
    if not cfg.get("habilitado"):
        return

    destino = "{}@{}:{}".format(cfg["usuario"], cfg["host"], cfg["caminho_remoto"])
    cmd = [
        "rsync", "-az", "--timeout=30",
        "-e", "ssh -p {} -o StrictHostKeyChecking=no".format(cfg.get("porta", 22)),
        str(DB_PATH),
        destino,
    ]

    log.info("Sincronizando banco com o droplet...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            log.info("Sync concluido com sucesso")
        else:
            log.error("Erro no sync: %s", result.stderr)
    except Exception as e:
        log.error("Falha no sync: %s", e)


def rodar():
    init_db()
    todos_novos = []
    max_dias = CONFIG.get("max_dias_anuncio", 20)

    for nome_busca, url in CONFIG["buscas"].items():
        if "/venda/" in url:
            tipo = "venda"
        elif "/aluguel/" in url:
            tipo = "aluguel"
        else:
            tipo = ""

        log.info("Buscando: %s", nome_busca)
        html = buscar_pagina(url)
        if not html:
            continue

        anuncios = extrair_anuncios(html, tipo=tipo)
        log.info("  -> %d anuncio(s) encontrado(s)", len(anuncios))

        for a in anuncios:
            if a.get("data_anuncio"):
                try:
                    dt = datetime.fromisoformat(a["data_anuncio"])
                    dias = (datetime.now() - dt).days
                    if dias > max_dias:
                        log.info("  Parando — anuncio com %d dias: %s", dias, a["titulo"][:50])
                        break
                except Exception:
                    pass

            if not ja_visto(a["id"]):
                salvar(a)
                todos_novos.append(a)
                log.info("  NOVO: %s | %s | %s | %s", a["titulo"][:55], a["preco"], a["bairro"], tipo)

        time.sleep(random.uniform(*CONFIG.get("delay_entre_buscas", (3, 7))))

    log.info("Total de novos anuncios: %d", len(todos_novos))

    if todos_novos:
        enviar_email(todos_novos)

    sincronizar()

    return todos_novos


if __name__ == "__main__":
    if "--testar-email" in sys.argv:
        testar_email()
    else:
        rodar()