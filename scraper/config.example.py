"""
Configuracao do robo OLX Imoveis - Santos/SP
remoear para config.py e preencher
"""

CONFIG = {
    # ── Buscas ────────────────────────────────────────────────────────────────
    # Parametros da URL:
    #   ps/pe       preco minimo/maximo
    #   ss          area minima em m²
    #   gsp         vagas de garagem
    #   ros=1&ros=2 1 ou 2 quartos
    #   ret=1020    apartamento
    #   sf=1        mais recentes primeiro  ← obrigatorio para o corte por data
    #   sp=1        menor preco / sp=15 maior preco
    "buscas": {
        "Gonzaga - Venda": (
            "https://www.olx.com.br/imoveis/venda/estado-sp/"
            "baixada-santista-e-litoral-sul/santos/gonzaga"
            "?ps=350000&pe=560000&ss=48&gsp=1&ros=1&ros=2&ret=1020&sf=1"
        ),
        "Campo Grande - Venda": (
            "https://www.olx.com.br/imoveis/venda/estado-sp/"
            "baixada-santista-e-litoral-sul/santos/campo-grande"
            "?ps=350000&pe=560000&ss=48&gsp=1&ros=1&ros=2&ret=1020&sf=1"
        ),
        "Pompeia - Venda": (
            "https://www.olx.com.br/imoveis/venda/estado-sp/"
            "baixada-santista-e-litoral-sul/santos/pompeia"
            "?ps=350000&pe=560000&ss=48&gsp=1&ros=1&ros=2&ret=1020&sf=1"
        ),

        # Aluguel (descomente se quiser)
        "Gonzaga - Aluguel": (
            "https://www.olx.com.br/imoveis/aluguel/estado-sp/"
            "baixada-santista-e-litoral-sul/santos/gonzaga"
            "?ps=1800&pe=3800&ss=48&gsp=1&ros=1&ros=2&ret=1020&sf=1"
        ),
        "Pompeia - Aluguel": (
            "https://www.olx.com.br/imoveis/aluguel/estado-sp/"
            "baixada-santista-e-litoral-sul/santos/pompeia"
            "?ps=1800&pe=3800&ss=48&gsp=1&ros=1&ros=2&ret=1020&sf=1"
        ),
        "Campo grande - Aluguel": (
            "https://www.olx.com.br/imoveis/aluguel/estado-sp/"
            "baixada-santista-e-litoral-sul/santos/campo-grande"
            "?ps=1800&pe=3800&ss=48&gsp=1&ros=1&ros=2&ret=1020&sf=1"
        ),
    },

    # ── Filtro de idade ───────────────────────────────────────────────────────
    # Para quando encontrar anuncio mais antigo que X dias
    # Funciona pois as buscas sao ordenadas por sf=1 (mais recentes primeiro)
    "max_dias_anuncio": 20,

    # ── Agendamento ───────────────────────────────────────────────────────────
    "horarios_execucao": ["08:00", "14:00", "20:00"],  # quantos quiser   # formato HH:MM

    # ── Email ─────────────────────────────────────────────────────────────────
    "email": {
        "habilitado": True,
        # Gmail: gere senha de app em myaccount.google.com/apppasswords
        # Brevo:  smtp-relay.brevo.com porta 587 (free tier generoso)
        "smtp_host":  "smtp.gmail.com",
        "smtp_porta": 587,
        "usuario":    "@gmail.com",
        "senha":      "",
        "remetente":     "@gmail.com",
        "destinatarios": ["@gmail.com"],
    },

    # ── Sync com o droplet ──────────────────────────────────────────────────
    "sync": {
        "habilitado": True,
        "host":           "",
        "usuario":        "olx",
        "porta":          22,
        "caminho_remoto": "/opt/olx_santos/data/imoveis.db",
    },

    # ── Comportamento ─────────────────────────────────────────────────────────
    "delay_entre_buscas": (3, 7),   # segundos aleatorios entre cada busca
}