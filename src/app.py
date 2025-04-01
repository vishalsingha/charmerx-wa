import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form 
from fastapi.responses import Response
from pydantic import BaseModel
from mongo_utils import MongoDBStorage
from whatsapp_utils import WhatsappUtils
from conv_utils import ChatConversationManager
import uvicorn

source_code_location = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

app = FastAPI()
db_storage = MongoDBStorage()
wa_utils = WhatsappUtils()
chat_manager = ChatConversationManager()


@app.post('/whatsapp')
async def reply(request: Request):

    form_data = await request.form()
    form_dict = dict(form_data)
    print(form_dict)
    sender = form_dict.get('From') 
    sender_history = db_storage.get_user_history(sender)

    msg_response = chat_manager.handle_conversation(form_dict, sender_history)
    db_storage.store_message(form_dict, msg_response)

    cx_reply = wa_utils.respond(msg_response)
    return Response(content=cx_reply, media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5005)






