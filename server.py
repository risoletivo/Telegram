from flask import Flask, jsonify, request
from telethon.sync import TelegramClient
from telethon.errors import BotMethodInvalidError, ChatAdminRequiredError
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
    return jsonify({"status": "Servidor funcionando!", "message": "Bem-vindo ao Telegram Bot API."})

@app.route('/getMessages', methods=['GET'])
def get_messages():
    """Obtém mensagens de um grupo."""
    try:
        chat_id = request.args.get('chat_id', type=int)
        limit = request.args.get('limit', default=10, type=int)
        if not chat_id:
            return jsonify({"error": "chat_id é obrigatório!"}), 400

        with client:
            messages = []
            for message in client.iter_messages(chat_id, limit=limit):
                if message:
                    messages.append({
                        "id": message.id,
                        "text": message.text or "Sem texto",
                        "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "media": bool(message.media),
                    })
            return jsonify(messages)

    except BotMethodInvalidError:
        return jsonify({"error": "Método restrito para bots. Verifique as permissões do bot ou o tipo de método usado."}), 403
    except ChatAdminRequiredError:
        return jsonify({"error": "O bot precisa ser administrador para acessar mensagens neste chat."}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
