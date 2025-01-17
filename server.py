import asyncio
from flask import Flask, jsonify, request
from telethon import TelegramClient, events
import os

# Variáveis de ambiente para credenciais do Telegram
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Inicializar o cliente do Telethon
client = TelegramClient(None, api_id, api_hash).start(bot_token=bot_token)

# Armazenamento em memória para mensagens (para testes)
messages_store = []

# Configurar o listener de eventos para novas mensagens
@client.on(events.NewMessage(chats=-1002318920298))  # ID do grupo
async def handler(event):
    """Armazena novas mensagens do grupo."""
    message_data = {
        "id": event.message.id,
        "text": event.message.text or "Sem texto",
        "date": event.message.date.strftime("%Y-%m-%d %H:%M:%S"),
        "media": bool(event.message.media),
        "sender_id": event.sender_id,  # Adiciona o ID do remetente
    }
    messages_store.append(message_data)  # Adiciona a mensagem na memória
    print(f"Nova mensagem recebida: {message_data}")  # Log para ver no console

# Inicializar o servidor Flask
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "Servidor funcionando!", "message": "API de eventos ativa!"})

@app.route('/getMessages', methods=['GET'])
def get_messages():
    """Retorna mensagens armazenadas."""
    bot_id = client.get_me().id  # Obtém o ID do bot
    only_bot = request.args.get('only_bot', default=False, type=bool)

    if only_bot:
        # Filtra mensagens enviadas pelo bot
        bot_messages = [msg for msg in messages_store if msg["sender_id"] == bot_id]
        return jsonify(bot_messages)
    else:
        # Retorna todas as mensagens
        return jsonify(messages_store)

# Iniciar o cliente e o servidor Flask
def main():
    loop = asyncio.get_event_loop()

    # Rodar cliente Telethon no mesmo loop do Flask
    loop.create_task(client.run_until_disconnected())  # Telethon rodando
    app.run(host='0.0.0.0', port=5000)  # Servidor Flask rodando

if __name__ == '__main__':
    main()
