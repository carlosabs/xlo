"""
Envio de email com os novos anuncios.
"""
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import CONFIG

log = logging.getLogger(__name__)


def enviar_email(novos):
    cfg = CONFIG["email"]
    if not cfg.get("habilitado"):
        log.info("Email desabilitado no config.py")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "[OLX Santos] {} novo(s) apartamento(s)".format(len(novos))
    msg["From"]    = cfg["remetente"]
    msg["To"]      = ", ".join(cfg["destinatarios"])
    msg.attach(MIMEText(_montar_html(novos), "html", "utf-8"))

    try:
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_porta"]) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(cfg["usuario"], cfg["senha"])
            smtp.sendmail(cfg["remetente"], cfg["destinatarios"], msg.as_string())
        log.info("Email enviado para %s", cfg["destinatarios"])
    except Exception as e:
        log.error("Erro ao enviar email: %s", e)


def _montar_html(novos):
    cards_html = ""
    for a in novos:
        thumb = (
            '<img src="{}" style="width:100%;height:160px;object-fit:cover;border-radius:8px 8px 0 0;display:block;">'.format(a["thumbnail"])
            if a.get("thumbnail") else
            '<div style="width:100%;height:160px;background:#e5e7eb;border-radius:8px 8px 0 0;display:flex;align-items:center;justify-content:center;font-size:32px;">🏠</div>'
        )
        detalhes = " &bull; ".join(filter(None, [
            "{} qts".format(a["quartos"]) if a.get("quartos") else "",
            a.get("area", ""),
            a.get("bairro", ""),
            a.get("tipo", "").capitalize(),
        ]))
        cards_html += """
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;margin-bottom:20px;">
            {thumb}
            <div style="padding:14px 16px;">
                <p style="margin:0 0 6px;font-size:15px;font-weight:600;color:#111827;">{titulo}</p>
                <p style="margin:0 0 6px;font-size:20px;font-weight:700;color:#1d4ed8;">{preco}</p>
                <p style="margin:0 0 12px;font-size:13px;color:#6b7280;">{detalhes}</p>
                <a href="{url}" style="display:inline-block;background:#1d4ed8;color:#fff;padding:8px 18px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:500;">Ver anuncio &rarr;</a>
            </div>
        </div>""".format(
            thumb=thumb,
            titulo=a.get("titulo", "Sem titulo"),
            preco=a.get("preco", "Sob consulta"),
            detalhes=detalhes,
            url=a.get("url", "#"),
        )

    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;">
<div style="max-width:560px;margin:30px auto;padding:0 16px;">
    <div style="background:#1d4ed8;padding:24px;border-radius:10px 10px 0 0;text-align:center;">
        <h1 style="margin:0;color:#fff;font-size:20px;">🏠 {count} novo(s) apartamento(s) em Santos</h1>
        <p style="margin:8px 0 0;color:#bfdbfe;font-size:13px;">{data} &bull; Pompeia | Campo Grande | Gonzaga</p>
    </div>
    <div style="background:#f9fafb;padding:20px;border:1px solid #e5e7eb;border-top:none;border-radius:0 0 10px 10px;">
        {cards}
        <p style="text-align:center;font-size:11px;color:#9ca3af;margin-top:24px;">Robo OLX Imoveis &bull; Santos/SP</p>
    </div>
</div>
</body></html>""".format(
        count=len(novos),
        data=datetime.now().strftime("%d/%m/%Y %H:%M"),
        cards=cards_html,
    )
