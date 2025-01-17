import asyncio
from flask import Flask, jsonify, request
from telethon import TelegramClient
import os

# Variáveis de ambiente para credenciais do Telegram
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Inicializar o cliente do Telethon
client = TelegramClient(None, api_id, api_hash).start(bot_token=bot_token)

# Inicializar o servidor Flask
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "Servidor funcionando!", "message": "API para buscar mensagens antigas."})

@app.route('/scanMessages', methods=['GET'])
def scan_messages():
    """Busca mensagens antigas do grupo."""
    chat_id = request.args.get('chat_id', type=int)
    limit = request.args.get('limit', default=100, type=int)
    offset_id = request.args.get('offset_id', default=0, type=int)  # ID inicial para busca
    max_messages = request.args.get('max_messages', default=500, type=int)  # Máximo de mensagens

    if not chat_id:
        return jsonify({"error": "Parâmetro 'chat_id' é obrigatório!"}), 400

    loop = asyncio.get_event_loop()

    async def fetch_messages():
        messages = []
        async for message in client.iter_messages(chat_id, limit=limit, offset_id=offset_id):
            messages.append({
                "id": message.id,
                "text": message.text or "Sem texto",
                "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                "media": bool(message.media),
                "sender_id": message.sender_id,
            })
            if len(messages) >= max_messages:  # Interrompe se atingir o máximo
                break
        return messages

    try:
        result = loop.run_until_complete(fetch_messages())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Iniciar o cliente e o servidor Flask
def main():
    loop = asyncio.get_event_loop()

    # Rodar cliente Telethon no mesmo loop do Flask
    loop.create_task(client.run_until_disconnected())  # Telethon rodando
    app.run(host='0.0.0.0', port=5000)  # Servidor Flask rodando

if __name__ == '__main__':
    main()
