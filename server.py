from flask import Flask, jsonify, request
from telethon.sync import TelegramClient

# Credenciais do Telegram
api_id = 28838959
api_hash = '0689fb8fce69e6d9db522f12f94cc8cb'
bot_token = '7859518986:AAEfD43-ctyHb1DIZat7Rv_oZtYbn-OAIIs'

# Inicializar o cliente do Telethon
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# Inicializar o servidor Flask
app = Flask(__name__)

@app.route('/getMessages', methods=['GET'])
def get_messages():
    try:
        chat_id = request.args.get('chat_id', type=int)
        limit = request.args.get('limit', default=10, type=int)
        if not chat_id:
            return jsonify({"error": "chat_id é obrigatório!"}), 400

        with client:
            messages = []
            for message in client.iter_messages(chat_id, limit=limit):
                messages.append({
                    "id": message.id,
                    "text": message.text or "Sem texto",
                    "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "media": bool(message.media)
                })

            return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
