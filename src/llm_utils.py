import os
from openai import OpenAI
from pydantic import BaseModel, Field
from system import grok_system_prompt


# Set your OpenAI API key here
API_KEY = os.environ.get("OPENAI_API_KEY")   # this is anthropic  currently
client = OpenAI(api_key = API_KEY, base_url="https://api.anthropic.com/v1/")


response_type = '''
Output Format : 
<think>thinkng here . Keep thnkng short and to the point<think>
- (Sweet) : Craft a short, witty, and engaging response that directly references details from the screenshot/text. Use a mix of playfulness, humour, sarcasm, teasing, or cleverness to make it feel personal and engaging.
- (Cool) : Continue the interaction with a short response that builds on the previous statement naturally. Possible tones: playful, teasing, flirty, clever. Incorporate elements of curiosity, surprise, or challenge.
- (Spicy) : Craft an attractive, charming, and concise reply that smoothly transitions the conversation towards a date or an engaging new topic. Use a mix of humor, intrigue, or confident charm to make the shift feel effortless and exciting.  \n\n- If the moment feels right, seamlessly incorporate a flirty yet natural ask-out.  \n- If not, initiate a fresh topic with a playful or intriguing hook that keeps the conversation flowing.  \n- Keep it short, clever, and engaging—avoid forced or overly generic transitions.
- (CharmerX) Craft a short and best reply possibles combining all the above responses. 

Don't output anything other than this.
'''



import requests
from PIL import Image
from io import BytesIO
import base64

def process_image_from_url(url):
    # Step 1: Get image from URL
    response = requests.get(url)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))

    # Step 2: Resize to half dimensions (changing aspect ratio)
    new_size = (img.width // 2, img.height // 2)
    img_resized = img.resize(new_size)

    # Step 3: Convert to base64 using original format
    format = img.format if img.format else 'JPEG'  # Default to JPEG if format not detected
    buffered = BytesIO()
    img_resized.save(buffered, format=format)
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_base64



class ResponseSuggestor:
    def __init__(self):
        self.system = grok_system_prompt

    def prepare_single_message(self, msg):
        content = []
        if msg.get('Body'):
            content.append({"type" : "text", "text" : msg.get('Body')})
        if msg.get('MediaUrl0'):
            content.append({"type": "image_url", "image_url": {"url": msg.get('MediaUrl0'), "detail": "low"}})

        message = [{"role" : "user", "content" : content}]

        if msg.get('cx_reply'):
            message.append({"role" : "assistant", "content" : msg.get('cx_reply')})

        return message

    def prepare_llm_message(self, msg, history):

        message = [{"role" : "system", "content" : self.system + f'\n\n{response_type}'}]


        if msg.get("MediaUrl0"):
            message+=self.prepare_single_message(msg)
        else:
            for h in history:
                message+=self.prepare_single_message(h)
            message+=self.prepare_single_message(msg)
        return message



    def get_chat_suggestions(self, msg, history):
        """
        Get the chat suggestions from the GPT-4 model.
        """

        messages = self.prepare_llm_message(msg, history)


        response = client.beta.chat.completions.parse(
                model="claude-3-7-sonnet-20250219",
                messages=messages,
                max_tokens=500, 
                temperature=0.9,           # Controls randomness (0 to 1)
                top_p=0.9,  
            )
        print(response)
        return response.choices[0].message.content

