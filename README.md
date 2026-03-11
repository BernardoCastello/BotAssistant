# Chatbot Pessoal

Bot FastAPI + Docker para Telegram

## Pré-requisitos

- Docker + Docker Compose
- Conta no Telegram e um bot criado via [@BotFather](https://t.me/botfather)
- URL pública com HTTPS

---

## 🚀 Setup passo a passo

### Criar o bot no BotFather

```
/newbot
→ escolha um nome
→ escolha um username (termina em "bot")
→ copie o token
```

### Configurar variáveis de ambiente

```bash
cp .env.example .env
```

### URL pública para desenvolvimento local

Use [ngrok](https://ngrok.com) para expor sua porta local:

```bash
ngrok http 8000
# Copie a URL https://xxxx.ngrok.io para WEBHOOK_BASE_URL no .env
```

### Subir o container local para dev

```bash
docker compose -f docker-compose.dev.yml up
```


### Registrar o webhook no Telegram

```bash
docker compose exec bot python scripts/setup_webhook.py set
```

Saída esperada:
```json
{"ok": true, "result": true, "description": "Webhook was set"}
```

---

## Comandos úteis

```bash
# Ver logs em tempo real
docker compose logs -f bot

# Remover webhook (para testes com polling)
docker compose exec bot python scripts/setup_webhook.py delete

# Checar saúde da aplicação
curl http://localhost:8000/health

# Derruba tudo 
docker compose down -v
```



