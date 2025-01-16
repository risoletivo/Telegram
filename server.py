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

# Garantir que o cliente esteja conectado ao iniciar o script
asyncio.run(client.start(bot_token=bot_token))

# Inicializar o Flask
app = Flask(__name__)

@app.route('/getMessages', methods=['GET'])
def get_messages():
    """Endpoint para buscar mensagens do Telegram"""
    try:
        chat_id = request.args.get('chat_id', type=int)
        limit = request.args.get('limit', default=10, type=int)

        if not chat_id:
            return jsonify({"error": "chat_id é obrigatório!"}), 400

        # Log para depuração
        print(f"Recebendo requisição para chat_id: {chat_id} com limite: {limit}")

        # Executar a função assíncrona usando asyncio.run
        messages = asyncio.run(fetch_messages(chat_id, limit))
        return jsonify(messages)
    except Exception as e:
        # Log detalhado do erro
        print(f"Erro ao processar requisição: {e}")
        return jsonify({"error": str(e)}), 500

async def fetch_messages(chat_id, limit):
    """Função assíncrona para buscar mensagens de um grupo"""
    try:
        async with client:
            history = await client(GetHistoryRequest(
                peer=chat_id,
                offset_id=0,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))

            messages = []
            for message in history.messages:
                messages.append({
                    "id": message.id,
                    "text": message.message or "Sem texto",
                    "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "media": bool(message.media)
                })

            return messages
    except Exception as e:
        print(f"Erro ao buscar mensagens do Telegram: {e}")
        raise e

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
