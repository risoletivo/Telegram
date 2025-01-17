import asyncio
from flask import Flask, jsonify, request, Response
from telethon import TelegramClient, events
import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

# Variáveis de ambiente para credenciais do Telegram
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Inicializar o cliente do Telethon
client = TelegramClient(None, api_id, api_hash).start(bot_token=bot_token)

# Armazenamento em memória para mensagens recentes (para testes)
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
    
    # Mantém apenas as últimas 50 mensagens (opcional, para evitar uso excessivo de memória)
    if len(messages_store) > 50:
        messages_store.pop(0)

    print(f"Nova mensagem recebida: {message_data}")  # Log para teste

# Inicializar o servidor Flask
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "Servidor funcionando!", "message": "API de eventos ativa!"})

@app.route('/getMessages', methods=['GET'])
def get_messages():
    """Retorna mensagens armazenadas."""
    loop = asyncio.get_event_loop()

    # Obtém o ID do bot para filtrar as mensagens enviadas por ele
    bot = loop.run_until_complete(client.get_me())
    bot_id = bot.id

    # Verifica se o filtro 'only_bot' foi solicitado
    only_bot = request.args.get('only_bot', default=False, type=bool)

    if only_bot:
        # Filtra mensagens enviadas pelo bot
        bot_messages = [msg for msg in messages_store if msg["sender_id"] == bot_id]
        return jsonify(bot_messages)
    else:
        # Retorna todas as mensagens do grupo
        return jsonify(messages_store)

@app.route('/rssFeed', methods=['GET'])
def rss_feed():
    """Gera um RSS feed com as mensagens mais recentes."""
    # Cria a estrutura principal do RSS
    rss = Element('rss', version="2.0")
    channel = SubElement(rss, 'channel')
    
    # Informações básicas do canal RSS
    title = SubElement(channel, 'title')
    title.text = "Feed de Mensagens do Grupo"
    
    link = SubElement(channel, 'link')
    link.text = "https://telegram-server-7mur.onrender.com/rssFeed"
    
    description = SubElement(channel, 'description')
    description.text = "As mensagens mais recentes do grupo do Telegram."
    
    # Adiciona cada mensagem como item do RSS
    for msg in messages_store:
        item = SubElement(channel, 'item')
        
        item_title = SubElement(item, 'title')
        item_title.text = f"Mensagem ID {msg['id']}"
        
        item_description = SubElement(item, 'description')
        item_description.text = msg['text']
        
        item_pubDate = SubElement(item, 'pubDate')
        item_pubDate.text = datetime.strptime(msg['date'], "%Y-%m-%d %H:%M:%S").strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        item_guid = SubElement(item, 'guid')
        item_guid.text = f"https://telegram-server-7mur.onrender.com/rssFeed#{msg['id']}"
    
    # Gera o XML em texto
    rss_feed_xml = tostring(rss, encoding="utf-8", method="xml")
    
    # Retorna o RSS com cabeçalho correto
    return Response(rss_feed_xml, mimetype="application/rss+xml")

# Iniciar o cliente e o servidor Flask
def main():
    loop = asyncio.get_event_loop()

    # Rodar cliente Telethon no mesmo loop do Flask
    loop.create_task(client.run_until_disconnected())  # Telethon rodando
    app.run(host='0.0.0.0', port=5000)  # Servidor Flask rodando

if __name__ == '__main__':
    main()
