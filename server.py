import asyncio
from flask import Flask, jsonify, request, Response
from telethon import TelegramClient, events
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import os

# Variáveis de ambiente para credenciais do Telegram
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Inicializar o cliente do Telethon com sessão de usuário
client = TelegramClient("user_session", api_id, api_hash)

# Armazenamento em memória para mensagens recentes
messages_store = []

# Configurar o listener de eventos para novas mensagens no grupo
@client.on(events.NewMessage(chats=-1002318920298))  # Substitua pelo ID do grupo
async def handler(event):
    """Captura novas mensagens no grupo."""
    message_data = {
        "id": event.message.id,
        "text": event.message.text or "Sem texto",
        "date": event.message.date.strftime("%Y-%m-%d %H:%M:%S"),
        "media": bool(event.message.media),
        "sender_id": event.sender_id,  # ID do remetente
    }
    messages_store.append(message_data)

    # Mantém apenas as últimas 50 mensagens (para evitar uso excessivo de memória)
    if len(messages_store) > 50:
        messages_store.pop(0)

    print(f"Nova mensagem recebida: {message_data}")  # Log para depuração

# Inicializar o servidor Flask
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "Servidor funcionando!", "message": "API de eventos ativa!"})

@app.route('/getMessages', methods=['GET'])
def get_messages():
    """Retorna mensagens armazenadas."""
    only_bot = request.args.get('only_bot', default=False, type=bool)
    if only_bot:
        return jsonify([msg for msg in messages_store if msg["sender_id"] == client.get_me().id])
    return jsonify(messages_store)

@app.route('/rssFeed', methods=['GET'])
def rss_feed():
    """Gera um RSS feed com mensagens."""
    rss = Element('rss', version="2.0")
    channel = SubElement(rss, 'channel')

    title = SubElement(channel, 'title')
    title.text = "Feed de Mensagens do Grupo"

    link = SubElement(channel, 'link')
    link.text = f"https://telegram-server.onrender.com/rssFeed"

    description = SubElement(channel, 'description')
    description.text = "Mensagens mais recentes do grupo Telegram."

    for msg in messages_store:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = f"Mensagem ID {msg['id']}"
        SubElement(item, 'description').text = msg['text']
        SubElement(item, 'pubDate').text = datetime.strptime(
            msg['date'], "%Y-%m-%d %H:%M:%S"
        ).strftime("%a, %d %b %Y %H:%M:%S GMT")

    return Response(tostring(rss, encoding="utf-8"), mimetype="application/rss+xml")

# Iniciar o cliente e o servidor Flask
def main():
    loop = asyncio.get_event_loop()
    loop.create_task(client.start())  # Inicia o cliente
    loop.create_task(client.run_until_disconnected())  # Mantenha o cliente ativo
    app.run(host='0.0.0.0', port=5000)  # Inicia o servidor Flask

if __name__ == '__main__':
    main()
