from flask import Flask, jsonify, request
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio

# Configuração do Telegram API
api_id = 28838959
api_hash = '0689fb8fce69e6d9db522f12f94cc8cb'
bot_token = '7859518986:AAEfD43-ctyHb1DIZat7Rv_oZtYbn-OAIIs'

# Inicializar o cliente do Telegram
client = TelegramClient('bot_session', api_id, api_hash)

# Inicializar o Flask
app = Flask(__name__)

@app.before_first_request
def start_client():
    # Garantir que o cliente Telethon seja iniciado antes da primeira requisição
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start(bot_token=bot_token))

@app.route('/getMessages', methods=['GET'])
def get_messages():
    try:
        chat_id = request.args.get('chat_id', 


