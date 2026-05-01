import sqlite3
from datetime import datetime
from pathlib import Path

_DB_PATH = None


def set_db_path(data_dir):
    global _DB_PATH
    _DB_PATH = Path(data_dir) / "imoveis.db"


def _path():
    if _DB_PATH is None:
        raise RuntimeError("DB path not set — call set_db_path() first")
    return str(_DB_PATH)


def init_db():
    Path(_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(_path())
    con.execute("""
        CREATE TABLE IF NOT EXISTS anuncios (
            id            TEXT PRIMARY KEY,
            titulo        TEXT,
            preco         TEXT,
            bairro        TEXT,
            cep           TEXT,
            logradouro    TEXT,
            url           TEXT,
            thumbnail     TEXT,
            quartos       TEXT,
            area          TEXT,
            tipo          TEXT,
            data_anuncio  TEXT,
            visto_em      TEXT,
            ignorado      INTEGER DEFAULT 0,
            favorito      INTEGER DEFAULT 0
        )
    """)
    # Migração: adiciona colunas novas se o banco já existia sem elas
    cur = con.execute("PRAGMA table_info(anuncios)")
    colunas = [row[1] for row in cur.fetchall()]
    for col, definition in [
        ("tipo",        "TEXT DEFAULT ''"),
        ("data_anuncio","TEXT DEFAULT ''"),
        ("ignorado",    "INTEGER DEFAULT 0"),
        ("favorito",    "INTEGER DEFAULT 0"),
        ("cep",         "TEXT DEFAULT ''"),
        ("logradouro",  "TEXT DEFAULT ''"),
    ]:
        if col not in colunas:
            con.execute("ALTER TABLE anuncios ADD COLUMN {} {}".format(col, definition))
    con.commit()
    con.close()


def ja_visto(anuncio_id):
    con = sqlite3.connect(_path())
    cur = con.execute("SELECT 1 FROM anuncios WHERE id = ?", (anuncio_id,))
    found = cur.fetchone() is not None
    con.close()
    return found


def salvar(anuncio):
    con = sqlite3.connect(_path())
    con.execute("""
        INSERT OR IGNORE INTO anuncios
            (id, titulo, preco, bairro, cep, logradouro,
             url, thumbnail, quartos, area, tipo, data_anuncio, visto_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        anuncio["id"],
        anuncio.get("titulo", ""),
        anuncio.get("preco", ""),
        anuncio.get("bairro", ""),
        anuncio.get("cep", ""),
        anuncio.get("logradouro", ""),
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


def salvar_logradouro(anuncio_id, logradouro):
    """Atualiza só o logradouro de um anúncio já salvo."""
    con = sqlite3.connect(_path())
    con.execute(
        "UPDATE anuncios SET logradouro = ? WHERE id = ?",
        (logradouro, anuncio_id),
    )
    con.commit()
    con.close()


def listar(tipo="", bairro="", quartos="", favorito=False, ordem="recentes"):
    con = sqlite3.connect(_path())
    con.row_factory = sqlite3.Row
    query = "SELECT * FROM anuncios WHERE ignorado IS NOT 1"
    params = []
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    if bairro:
        query += " AND LOWER(bairro) LIKE ?"
        params.append("%" + bairro.lower() + "%")
    if quartos:
        query += " AND quartos = ?"
        params.append(quartos)
    if favorito:
        query += " AND favorito = 1"
    if ordem == "preco_asc":
        query += " ORDER BY CAST(REPLACE(REPLACE(REPLACE(preco,'R$ ',''),'.',''),',','.') AS REAL) ASC"
    elif ordem == "preco_desc":
        query += " ORDER BY CAST(REPLACE(REPLACE(REPLACE(preco,'R$ ',''),'.',''),',','.') AS REAL) DESC"
    else:
        query += " ORDER BY COALESCE(data_anuncio, visto_em) DESC"
    rows = con.execute(query, params).fetchall()
    con.close()
    return [dict(r) for r in rows]


def toggle_favorito(anuncio_id):
    con = sqlite3.connect(_path())
    row = con.execute("SELECT favorito FROM anuncios WHERE id = ?", (anuncio_id,)).fetchone()
    if row:
        novo = 0 if row[0] else 1
        con.execute("UPDATE anuncios SET favorito = ? WHERE id = ?", (novo, anuncio_id))
        con.commit()
    con.close()


def ignorar(anuncio_id):
    con = sqlite3.connect(_path())
    con.execute("UPDATE anuncios SET ignorado = 1 WHERE id = ?", (anuncio_id,))
    con.commit()
    con.close()


def stats():
    con = sqlite3.connect(_path())
    total = con.execute(
        "SELECT COUNT(*) FROM anuncios WHERE ignorado IS NOT 1"
    ).fetchone()[0]
    hoje = con.execute(
        "SELECT COUNT(*) FROM anuncios WHERE DATE(visto_em) = DATE('now') AND ignorado IS NOT 1"
    ).fetchone()[0]
    favoritos = con.execute(
        "SELECT COUNT(*) FROM anuncios WHERE favorito = 1 AND ignorado IS NOT 1"
    ).fetchone()[0]
    bairros = con.execute(
        "SELECT bairro, COUNT(*) as n FROM anuncios WHERE ignorado IS NOT 1 "
        "GROUP BY bairro ORDER BY n DESC"
    ).fetchall()
    con.close()
    return {
        "total": total,
        "hoje": hoje,
        "favoritos": favoritos,
        "bairros": [(r[0] or "Outros", r[1]) for r in bairros],
    }