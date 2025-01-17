import asyncio
from flask import Flask, jsonify, request
from telethon import TelegramClient, events
import os

# Credenciais do Telegram
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Inicializar o cliente Telethon (UserBot)
client = TelegramClient('session_name', api_id, api_hash)

# Armazenamento de mensagens
messages_store = []

# Listener para mensagens no grupo
@client.on(events.NewMessage(chats=-1002318920298))  # Substitua pelo ID do grupo
async def handler(event):
    """Captura novas mensagens no grupo."""
    message_data = {
        "id": event.message.id,
        "text": event.message.text or "Sem texto",
        "date": event.message.date.strftime("%Y-%m-%d %H:%M:%S"),
        "media": bool(event.message.media),
        "sender_id": event.sender_id,
    }
    messages_store.append(message_data)
    
    # Mantém apenas as últimas 50 mensagens
    if len(messages_store) > 50:
        messages_store.pop(0)

    print(f"Nova mensagem recebida: {message_data}")

# Inicializar o Flask
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "Servidor funcionando!", "message": "API de mensagens ativa."})

@app.route('/getMessages', methods=['GET'])
def get_messages():
    """Retorna mensagens armazenadas."""
    return jsonify(messages_store)

@app.route('/diagnostic', methods=['GET'])
def diagnostic():
    """Exibe o conteúdo do armazenamento de mensagens."""
    return jsonify({
        "messages_store": messages_store,
        "total_messages": len(messages_store)
    })

# Iniciar o cliente Telethon e o servidor Flask
def main():
    loop = asyncio.get_event_loop()

    # Autenticação manual no Render (se necessário)
    client.start()

    # Rodar o cliente e o servidor
    loop.create_task(client.run_until_disconnected())
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
