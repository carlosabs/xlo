import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger(__name__)


def enviar_email(novos, config):
    cfg = config.get("email", {})
    if not cfg.get("habilitado"):
        log.info("Email desabilitado")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "[OLX Santos] {} novo(s) apartamento(s)".format(len(novos))
    msg["From"] = cfg["remetente"]
    msg["To"] = ", ".join(cfg["destinatarios"])
    msg.attach(MIMEText(_montar_html(novos), "html", "utf-8"))

    with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_porta"]) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(cfg["usuario"], cfg["senha"])
        smtp.sendmail(cfg["remetente"], cfg["destinatarios"], msg.as_string())
    log.info("Email enviado para %s", cfg["destinatarios"])


def _montar_html(novos):
    cards_html = ""
    for a in novos:
        thumb = (
            '<img src="{}" style="width:100%;height:160px;object-fit:cover;">'.format(a["thumbnail"])
            if a.get("thumbnail") else
            '<div style="height:160px;background:#e5e7eb;display:flex;align-items:center;'
            'justify-content:center;font-size:32px;">🏠</div>'
        )

        # Endereço: logradouro tem prioridade, senão bairro
        endereco = a.get("logradouro") or a.get("bairro", "")

        detalhes = " &bull; ".join(filter(None, [
            "{} qts".format(a["quartos"]) if a.get("quartos") else "",
            a.get("area", ""),
            endereco,
            a.get("tipo", "").capitalize(),
        ]))

        cards_html += """
        <div style="border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;margin-bottom:20px;">
            {thumb}
            <div style="padding:14px 16px;">
                <p style="margin:0 0 4px;font-size:15px;font-weight:600;">{titulo}</p>
                <p style="margin:0 0 4px;font-size:20px;font-weight:700;color:#1d4ed8;">{preco}</p>
                <p style="margin:0 0 12px;font-size:13px;color:#6b7280;">{detalhes}</p>
                <a href="{url}" style="background:#1d4ed8;color:#fff;padding:8px 18px;border-radius:6px;text-decoration:none;">Ver &rarr;</a>
            </div>
        </div>""".format(
            thumb=thumb,
            titulo=a.get("titulo", ""),
            preco=a.get("preco", ""),
            detalhes=detalhes,
            url=a.get("url", "#"),
        )

    return """<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="background:#f3f4f6;font-family:Arial,sans-serif;padding:20px;max-width:560px;margin:0 auto;">
<h2 style="color:#1d4ed8;">{count} novo(s) apartamento(s) &mdash; {data}</h2>
{cards}
</body></html>""".format(
        count=len(novos),
        data=datetime.now().strftime("%d/%m/%Y %H:%M"),
        cards=cards_html,
    )