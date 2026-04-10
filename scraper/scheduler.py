"""
Agendador de execucao diaria do scraper.

Uso:
    python3 scheduler.py             # roda continuamente agendado
    python3 scheduler.py --agora     # executa imediatamente e sai

Para rodar em background no servidor:
    nohup python3 scheduler.py > /var/log/olx_scheduler.log 2>&1 &

Ou como servico systemd (recomendado):
    sudo cp olx_santos.service /etc/systemd/system/
    sudo systemctl enable olx_santos
    sudo systemctl start olx_santos
"""
import sys
import logging
import time

try:
    import schedule
except ImportError:
    print("Instale o pacote schedule: pip3 install schedule")
    sys.exit(1)

from config import CONFIG
from main import rodar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def job():
    log.info("=== Iniciando execucao agendada ===")
    try:
        novos = rodar()
        log.info("=== Concluido — %d novos anuncios ===", len(novos))
    except Exception as e:
        log.error("Erro na execucao: %s", e)


if __name__ == "__main__":
    if "--agora" in sys.argv:
        log.info("Execucao imediata solicitada")
        job()
        sys.exit(0)

    horario = CONFIG.get("horario_execucao", "08:00")
    schedule.every().day.at(horario).do(job)
    log.info("Agendado para rodar todos os dias as %s", horario)
    log.info("Use Ctrl+C para parar ou python3 scheduler.py --agora para rodar agora")

    while True:
        schedule.run_pending()
        time.sleep(30)
