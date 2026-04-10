# olx_santos

Robô de busca de apartamentos no OLX + visualizador web.

```
olx_santos/
├── scraper/
│   ├── config.py       configuracoes (bairros, email, agendamento)
│   ├── db.py           banco de dados SQLite
│   ├── fetcher.py      requisicoes HTTP
│   ├── parser.py       extracao do JSON do OLX
│   ├── notifier.py     envio de email
│   ├── main.py         orquestrador — rode este para executar
│   ├── scheduler.py    agendador diario
│   └── data/           imoveis.db (criado automaticamente)
├── web/
│   ├── app.py          servidor Flask
│   └── templates/
│       └── index.html  interface web
├── data/               pasta reservada (db fica em scraper/data/)
└── olx_santos.service  arquivo de servico systemd
```

## Instalacao

```bash
pip3 install requests beautifulsoup4 lxml flask schedule
```

## Rodar o scraper uma vez

```bash
cd scraper
python3 main.py
```

## Rodar agendado (todos os dias no horario configurado)

```bash
cd scraper
python3 scheduler.py

# ou em background:
nohup python3 scheduler.py > /var/log/olx_scheduler.log 2>&1 &
```

## Rodar o visualizador web

```bash
cd web
python3 app.py
# acesse http://localhost:5000
```

## Instalar como servico systemd (servidor)

```bash
sudo cp olx_santos.service /etc/systemd/system/
# edite o caminho em ExecStart e WorkingDirectory se necessario
sudo systemctl daemon-reload
sudo systemctl enable olx_santos
sudo systemctl start olx_santos

# ver status / logs:
sudo systemctl status olx_santos
journalctl -u olx_santos -f
```

## Banco existente (migracao)

Se ja tem um `imoveis.db` de versao anterior, o `db.py` adiciona
automaticamente as colunas `tipo` e `data_anuncio` se nao existirem.
Nao precisa apagar o banco.
