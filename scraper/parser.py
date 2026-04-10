"""
Extracao de anuncios do HTML/JSON do OLX.
"""
import json
import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def extrair_anuncios(html, tipo=""):
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", {"id": "__NEXT_DATA__"})

    if not script:
        log.warning("__NEXT_DATA__ nao encontrado, tentando fallback")
        return _fallback(soup, tipo)

    try:
        data = json.loads(script.string)
    except (json.JSONDecodeError, TypeError) as e:
        log.error("Erro ao decodificar JSON: %s", e)
        return []

    try:
        props = data["props"]["pageProps"]
        listings_raw = (
            props.get("ads")
            or props.get("listings")
            or props.get("searchState", {}).get("listings", [])
            or _deep_find(data, "ads")
            or []
        )
    except (KeyError, TypeError):
        listings_raw = []

    return [a for a in (_parse_item(item, tipo) for item in listings_raw) if a]


def _parse_item(item, tipo=""):
    try:
        anuncio_id = str(item.get("listId") or "")
        if not anuncio_id:
            return None

        titulo = item.get("subject") or item.get("title") or ""
        preco  = item.get("price") or item.get("priceValue") or "Sob consulta"
        url    = item.get("friendlyUrl") or item.get("url") or ""
        if url and not url.startswith("http"):
            url = "https://www.olx.com.br" + url

        # Imagem
        thumbnail = ""
        images = item.get("images") or []
        if isinstance(images, list) and images:
            first = images[0]
            thumbnail = first.get("original", "") if isinstance(first, dict) else first

        # Bairro
        bairro = ""
        loc = item.get("location") or {}
        if isinstance(loc, dict):
            bairro = loc.get("neighbourhood") or loc.get("municipio") or ""
        if not bairro:
            loc2 = item.get("locationDetails") or {}
            if isinstance(loc2, dict):
                bairro = loc2.get("neighbourhood") or loc2.get("zone") or ""

        # Quartos e area
        quartos = area = ""
        for prop in (item.get("properties") or []):
            name  = str(prop.get("name") or "").lower()
            value = str(prop.get("value") or "")
            if name == "rooms":
                quartos = value
            elif name == "size":
                area = value

        # Data do anuncio
        data_anuncio = ""
        raw_date = item.get("date") or item.get("listTime") or item.get("origListTime")
        if raw_date:
            try:
                ts = int(raw_date)
                if ts > 1e10:
                    ts = ts / 1000
                data_anuncio = datetime.fromtimestamp(ts).isoformat()
            except Exception:
                pass

        return {
            "id":           anuncio_id,
            "titulo":       titulo,
            "preco":        preco,
            "bairro":       bairro,
            "url":          url,
            "thumbnail":    thumbnail,
            "quartos":      quartos,
            "area":         area,
            "tipo":         tipo,
            "data_anuncio": data_anuncio,
        }
    except Exception as e:
        log.debug("Erro ao parsear item: %s", e)
        return None


def _deep_find(obj, key, depth=0):
    if depth > 8:
        return None
    if isinstance(obj, dict):
        if key in obj and isinstance(obj[key], list) and obj[key]:
            return obj[key]
        for v in obj.values():
            result = _deep_find(v, key, depth + 1)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _deep_find(item, key, depth + 1)
            if result:
                return result
    return None


def _fallback(soup, tipo=""):
    anuncios = []
    cards = soup.select("[data-lurker-detail='main_ad']") or soup.select(".AdCard_adCard__RJd2b")
    for card in cards:
        try:
            link  = card.find("a", href=True)
            url   = link["href"] if link else ""
            titulo = card.get_text(strip=True)[:80]
            preco_el = card.select_one("[class*='price']") or card.select_one("[class*='Price']")
            preco = preco_el.get_text(strip=True) if preco_el else ""
            match = re.search(r"/(\d+)$", url)
            anuncio_id = match.group(1) if match else url[-20:]
            if anuncio_id:
                anuncios.append({
                    "id": anuncio_id, "titulo": titulo, "preco": preco,
                    "bairro": "", "url": url, "thumbnail": "",
                    "quartos": "", "area": "", "tipo": tipo, "data_anuncio": "",
                })
        except Exception:
            pass
    return anuncios
