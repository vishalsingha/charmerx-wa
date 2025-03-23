import os
from openai import OpenAI
from pydantic import BaseModel, Field
from system import system_prompt, system_prompt1


# Set your OpenAI API key here
API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key = API_KEY)

class ChatSuggestions(BaseModel):
    suggestion1 : str
    suggestion2 : str
    suggestion3 : str


class ResponseSuggestor:
    def __init__(self):
        self.system = system_prompt1

    def prepare_single_message(self, msg_dict):
        content = []
        if msg_dict.get('Body'):
            content.append({"type" : "text", "text" : msg_dict.get('Body')})
        if msg_dict.get('MediaUrl0'):
            content.append({"type": "image_url", "image_url": {"url": msg_dict.get('MediaUrl0'), "detail": "auto"}})

        message = [{"role" : "user", "content" : content}]

        if msg_dict.get('cx_reply'):
            message.append({"role" : "assistant", "content" : msg_dict.get('cx_reply')})

        return message

    def prepare_llm_message(self, msg, history):

        message = []

        for h in history:
            message+=self.prepare_single_message(h)

        message+=self.prepare_single_message(msg.form.to_dict())
        return message



    def get_chat_suggestions(self, msg, history):
        """
        Get the chat suggestions from the GPT-4 model.
        """

        messages = self.prepare_llm_message(msg, history)

        print(messages)

        response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500, 
                response_format = ChatSuggestions
            )
        response = response.choices[0].message.parsed
        
        return response.suggestion1




