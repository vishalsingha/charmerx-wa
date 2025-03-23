import os
from dotenv import load_dotenv
from flask import Flask, request
from mongo_utils import MongoDBStorage
from whatsapp_utils import WhatsappUtils
from conv_utils import ChatConversationManager

source_code_location = os.path.dirname(os.path.abspath(__file__))


load_dotenv()


app = Flask(__name__)
db_storage = MongoDBStorage()
wa_utils = WhatsappUtils()
chat_manager = ChatConversationManager()


@app.route('/whatsapp', methods=['POST'])
def reply():

    print(request.form.to_dict())

    sender = request.form.get('From') 
    sender_history = db_storage.get_user_history(sender)

    
    msg_response = chat_manager.handle_conversation(request, sender_history)
    db_storage.store_message(request, msg_response)
    return wa_utils.respond(msg_response)



if __name__ == "__main__":
    app.run(port=5000, debug=True)



