#!/usr/bin/env python3
"""
Web viewer para os imoveis scrapeados do OLX.
Rode: python3 app.py
Acesse: http://localhost:5000
"""
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, jsonify, render_template, request
except ImportError:
    print("Flask nao instalado. Rode: pip3 install flask")
    exit(1)

app = Flask(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "imoveis.db"


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/imoveis")
def api_imoveis():
    bairro   = request.args.get("bairro", "")
    quartos  = request.args.get("quartos", "")
    tipo     = request.args.get("tipo", "")
    favorito = request.args.get("favorito", "")
    ordem    = request.args.get("ordem", "recentes")
    busca    = request.args.get("busca", "")

    query  = "SELECT * FROM anuncios WHERE 1=1"
    params = []

    if bairro:
        query += " AND LOWER(bairro) LIKE ?"
        params.append("%" + bairro.lower() + "%")

    if quartos:
        query += " AND quartos = ?"
        params.append(quartos)

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)

    if favorito == "1":
        query += " AND favorito = 1"

    if busca:
        query += " AND (LOWER(titulo) LIKE ? OR LOWER(bairro) LIKE ?)"
        params += ["%" + busca.lower() + "%", "%" + busca.lower() + "%"]

    if ordem == "preco_asc":
        query += " ORDER BY CAST(REPLACE(REPLACE(REPLACE(preco,'R$ ',''),'.',''),',','.') AS REAL) ASC"
    elif ordem == "preco_desc":
        query += " ORDER BY CAST(REPLACE(REPLACE(REPLACE(preco,'R$ ',''),'.',''),',','.') AS REAL) DESC"
    else:
        query += " ORDER BY COALESCE(data_anuncio, visto_em) DESC"

    rows    = get_db().execute(query, params).fetchall()
    imoveis = [dict(r) for r in rows]

    agora = datetime.now()
    for im in imoveis:
        data_ref = im.get("data_anuncio") or im.get("visto_em") or ""
        try:
            dt   = datetime.fromisoformat(data_ref)
            diff = agora - dt
            if diff.days == 0:
                im["visto_label"] = "hoje"
            elif diff.days == 1:
                im["visto_label"] = "ontem"
            else:
                im["visto_label"] = "há {} dias".format(diff.days)
        except Exception:
            im["visto_label"] = ""

    return jsonify(imoveis)


@app.route("/api/imoveis/<anuncio_id>/favorito", methods=["PATCH"])
def toggle_favorito(anuncio_id):
    con = get_db()
    row = con.execute("SELECT favorito FROM anuncios WHERE id = ?", (anuncio_id,)).fetchone()
    if not row:
        return jsonify({"erro": "nao encontrado"}), 404
    novo_valor = 0 if row["favorito"] else 1
    con.execute("UPDATE anuncios SET favorito = ? WHERE id = ?", (novo_valor, anuncio_id))
    con.commit()
    return jsonify({"favorito": novo_valor})


@app.route("/api/imoveis/<anuncio_id>", methods=["DELETE"])
def deletar(anuncio_id):
    con = get_db()
    con.execute("DELETE FROM anuncios WHERE id = ?", (anuncio_id,))
    con.commit()
    return jsonify({"ok": True})


@app.route("/api/stats")
def api_stats():
    con     = get_db()
    total      = con.execute("SELECT COUNT(*) FROM anuncios").fetchone()[0]
    hoje       = con.execute("SELECT COUNT(*) FROM anuncios WHERE DATE(visto_em) = DATE('now')").fetchone()[0]
    favoritos  = con.execute("SELECT COUNT(*) FROM anuncios WHERE favorito = 1").fetchone()[0]
    bairros    = con.execute("SELECT bairro, COUNT(*) as n FROM anuncios GROUP BY bairro ORDER BY n DESC").fetchall()
    tipos      = con.execute("SELECT tipo, COUNT(*) as n FROM anuncios GROUP BY tipo ORDER BY n DESC").fetchall()
    return jsonify({
        "total":     total,
        "hoje":      hoje,
        "favoritos": favoritos,
        "bairros":   [{"bairro": r[0] or "Desconhecido", "n": r[1]} for r in bairros],
        "tipos":     [{"tipo": r[0] or "outro", "n": r[1]} for r in tipos],
    })


if __name__ == "__main__":
    if not DB_PATH.exists():
        print("Banco nao encontrado em:", DB_PATH.resolve())
        print("Rode o scraper/main.py primeiro.")
        exit(1)
    print("Usando banco:", DB_PATH.resolve())
    print("Servidor em http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)