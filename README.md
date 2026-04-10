# olx_santos

Robô que monitora apartamentos no OLX em Santos/SP e exibe os resultados em um frontend web.

## Arquitetura

```
Celular Android (Termux)         VPS Digital Ocean
────────────────────────         ─────────────────
cron 2x por dia                  web/app.py (Flask)
  └─ scraper/main.py     rsync►  data/imoveis.db
       ├─ fetcher.py
       ├─ parser.py
       ├─ db.py
       ├─ notifier.py
       └─ scheduler.py
```

O scraper roda no celular (IP residencial evita bloqueio do OLX).
Após cada execução sincroniza o banco via rsync para o VPS.
O frontend Flask no VPS serve os dados na porta 5000.

## Estrutura

```
olx_santos/
├── scraper/
│   ├── config.py         configuracoes (use config.example.py como base)
│   ├── config.example.py exemplo de configuracao
│   ├── db.py             banco de dados SQLite
│   ├── fetcher.py        requisicoes HTTP
│   ├── parser.py         extracao do JSON do OLX
│   ├── notifier.py       envio de email
│   ├── main.py           orquestrador
│   └── scheduler.py      agendador (usado no Termux)
├── web/
│   ├── app.py            servidor Flask
│   └── templates/
│       └── index.html    interface web
├── data/                 imoveis.db (gerado automaticamente, no .gitignore)
├── requirements.txt      dependencias Python
├── olx_web.service       servico systemd para o frontend
└── olx_scraper.service   servico systemd (opcional, se rodar no servidor)
```

## Instalacao

### Dependencias

```bash
pip install -r requirements.txt
```

### Configuracao

```bash
cp scraper/config.example.py scraper/config.py
# edite o config.py com suas configuracoes
```

### Rodando o scraper (Termux / Linux)

```bash
cd scraper
python main.py                  # execucao unica
python main.py --agora          # alias para execucao unica
python main.py --testar-email   # testa email com ultimos 5 anuncios do banco
python scheduler.py             # agendador continuo (usa horarios do config.py)
```

### Rodando o frontend (VPS)

```bash
cd web
python app.py
# acesse http://SEU_IP:5000
```

### Instalando como servico systemd (VPS)

```bash
sudo cp olx_web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now olx_web

# logs
tail -f /var/log/olx_web.log
```

### Configurando no Termux (Android)

```bash
# Instalar dependencias
pkg install python python-pip rsync openssh cronie -y
pkg install libxml2 libxslt -y
pip install -r requirements.txt

# Configurar cron (ex: 8h e 20h)
crontab -e
# adicionar:
# 0 8,20 * * * cd ~/olx_santos/scraper && python main.py >> ~/olx_santos/scraper/scraper.log 2>&1

# Iniciar cron
crond

# Manter rodando em background
termux-wake-lock

# Auto-iniciar no boot (requer Termux:Boot instalado pelo F-Droid)
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start.sh << 'BOOT'
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
crond
BOOT
chmod +x ~/.termux/boot/start.sh
```

### Sincronizando banco com o VPS via SSH

```bash
# Gerar chave SSH no celular
ssh-keygen -t ed25519 -C "termux-olx"

# Copiar chave para o VPS
# No VPS:
echo "SUA_CHAVE_PUBLICA" >> ~/.ssh/authorized_keys

# Testar
ssh usuario@IP_DO_VPS
```

## Parametros da URL do OLX

| Parametro | Descricao |
|-----------|-----------|
| `ps` / `pe` | preco minimo / maximo |
| `ss` | area minima em m² |
| `gsp` | vagas de garagem |
| `ros=1&ros=2` | 1 ou 2 quartos |
| `ret=1020` | tipo apartamento |
| `sf=1` | ordenar por mais recentes |
| `sp=1` | ordenar por menor preco |
| `sp=15` | ordenar por maior preco |

## Funcionalidades

- Busca em multiplos bairros e categorias (venda/aluguel)
- Filtro por preco, area minima, garagem e quartos
- Corte automatico por idade do anuncio (configavel, padrao 20 dias)
- Deduplicacao — nao notifica o mesmo anuncio duas vezes
- Notificacao por email com cards dos novos anuncios
- Email de erro em caso de falha critica
- Sincronizacao automatica do banco com o VPS via rsync
- Frontend web com filtros, busca, ordenacao e tabs venda/aluguel
- Favoritar anuncios com destaque visual
- Excluir anuncios fisicamente do banco

## Observacoes

- O scraper **nao pode rodar no VPS** — IPs de datacenter sao bloqueados pelo OLX
- Rodar no celular via Termux resolve o problema (IP residencial)
- O banco SQLite nao deve ser commitado (dados pessoais / LGPD)
- A senha do Gmail deve ser uma **senha de app** gerada em myaccount.google.com/apppasswords