"""
Operacoes com o banco de dados SQLite.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "imoveis.db"


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS anuncios (
            id            TEXT PRIMARY KEY,
            titulo        TEXT,
            preco         TEXT,
            bairro        TEXT,
            url           TEXT,
            thumbnail     TEXT,
            quartos       TEXT,
            area          TEXT,
            tipo          TEXT,
            data_anuncio  TEXT,
            visto_em      TEXT
        )
    """)
    # Migração: adiciona colunas novas se o banco ja existia sem elas
    cur = con.execute("PRAGMA table_info(anuncios)")
    colunas = [row[1] for row in cur.fetchall()]
    if "tipo" not in colunas:
        con.execute("ALTER TABLE anuncios ADD COLUMN tipo TEXT DEFAULT ''")
    if "data_anuncio" not in colunas:
        con.execute("ALTER TABLE anuncios ADD COLUMN data_anuncio TEXT DEFAULT ''")
    con.commit()
    con.close()


def ja_visto(anuncio_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.execute("SELECT 1 FROM anuncios WHERE id = ?", (anuncio_id,))
    found = cur.fetchone() is not None
    con.close()
    return found


def salvar(anuncio):
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        INSERT OR IGNORE INTO anuncios
            (id, titulo, preco, bairro, url, thumbnail, quartos, area, tipo, data_anuncio, visto_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        anuncio["id"],
        anuncio.get("titulo", ""),
        anuncio.get("preco", ""),
        anuncio.get("bairro", ""),
        anuncio.get("url", ""),
        anuncio.get("thumbnail", ""),
        anuncio.get("quartos", ""),
        anuncio.get("area", ""),
        anuncio.get("tipo", ""),
        anuncio.get("data_anuncio", ""),
        datetime.now().isoformat(),
    ))
    con.commit()
    con.close()
