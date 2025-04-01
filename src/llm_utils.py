import os
from openai import OpenAI
from pydantic import BaseModel, Field
from system import system_prompt, system_prompt1, grok_system_prompt
from mistralai import Mistral


# Set your OpenAI API key here
API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key = API_KEY)



mistral_api_key = "1c6iZ4qIFYRcu0AgMicJdyKlCEG1ydgT"
mistral_client = Mistral(api_key=mistral_api_key)

# class ChatSuggestions(BaseModel):
#     suggestion1: str = Field(..., description="Short and natural response related which can be one of playful, funny, witty, flirty, spicy, teasing, clever.")
#     suggestion2: str = Field(..., description="Short and natural response related to continuation, agreement disagreement. Possble tones can be : playful, flirty spicy, teasing, clever, punch line, pickup lines.")
#     suggestion3: str = Field(..., description="Short and natural response smoothly transitioning the conversation towards asking the person out or shifting to a new, meaningful topic. Craft attractive charming and clever reply.")


suggestion2_prompt = '''
**Spicy:** Craft an attractive, charming, and concise reply that smoothly transitions the conversation towards a date or an engaging new topic. Use a mix of humor, intrigue, or confident charm to make the shift feel effortless and exciting.  

- If the moment feels right, seamlessly incorporate a flirty yet natural ask-out.  
- If not, initiate a fresh topic with a playful or intriguing hook that keeps the conversation flowing.  
- Keep it short, clever, and engaging—avoid forced or overly generic transitions.
'''



suggestion3_prompt = '''
**Spicy:** Craft an attractive, charming, and concise reply that smoothly transitions the conversation towards a date or an engaging new topic. Use a mix of humor, intrigue, or confident charm to make the shift feel effortless and exciting.  

- If the moment feels right, seamlessly incorporate a flirty yet natural ask-out.  
- If not, initiate a fresh topic with a playful or intriguing hook that keeps the conversation flowing.  
- Keep it short, clever, and engaging—avoid forced or overly generic transitions.
'''


class ChatSuggestions(BaseModel):
    suggestion1: str = Field(..., description="Sweet : Craft a short, witty, and engaging response that directly references details from the screenshot/text. Use a mix of playfulness, humour, sarcasm, teasing, or cleverness to make it feel personal and engaging.")
    suggestion2: str = Field(..., description="Cool : Continue the interaction with a short response that builds on the previous statement naturally. Possible tones: playful, teasing, flirty, clever. Incorporate elements of curiosity, surprise, or challenge.")
    suggestion3: str = Field(..., description=suggestion3_prompt)


# class ChatSuggestions(BaseModel):
#     suggestion1: str = Field(..., description="A kind, empathetic reply that ends with a hook or follow-up question.")
#     suggestion2: str = Field(..., description="A witty, humorous response that may include mild playful sarcasm if it enhances confidence and coolness. Not flirty or suggestive.")
#     suggestion3: str = Field(..., description="A subtle, playful flirty reply if appropriate. If flirting or asking out isn't suitable, pivot to an engaging topic change.")
#     suggestion4: str = Field(..., description="The best option or a smart combination of the above, tailored to the situation.")




# 1. Sweet: A kind, empathetic reply that ends with a hook or follow-up question.
# 2. Cool: A witty, humorous response that may include mild playful sarcasm if it enhances confidence and coolness. Not flirty or suggestive.
# 3. Spicy: A subtle, playful flirty reply if appropriate. If flirting or asking out isn't suitable, pivot to an engaging topic change.
# 4. CharmerX Special: The best option or a smart combination of the above, tailored to the situation.


# class ChatSuggestions(BaseModel):
#     suggestion1: str = Field(..., description="Generate witty, playful, and slightly flirty responses with an Indian twist. Incorporate light humor, cultural references, or relatable situations that show confidence and charm. Responses should feel natural, not overbearing — something that makes the other person smile or chuckle. Add subtle compliments or teasing to build intrigue.")
#     suggestion2: str = Field(..., description="Create engaging and thoughtful responses that either continue the conversation or lightly challenge the other person's viewpoint. Keep it playful but substantial, mixing humor with curiosity. Use pop culture, Bollywood, cricket, or Indian food references to keep it relatable. If disagreeing, be charmingly witty rather than confrontational.")
#     suggestion3: str = Field(..., description="Generate smooth, charming, and confident transitions to either ask the person out or change the topic seamlessly. Make it feel casual and warm, with a flirty undertone. References to Indian festivals, food, or pop culture can add familiarity. Avoid sounding rehearsed; it should feel spontaneous.")






class ResponseSuggestor:
    def __init__(self):
        self.system = system_prompt1

    def prepare_single_message(self, msg):
        content = []
        if msg.get('Body'):
            content.append({"type" : "text", "text" : msg.get('Body')})
        if msg.get('MediaUrl0'):
            content.append({"type": "image_url", "image_url": {"url": msg.get('MediaUrl0'), "detail": "high"}})

        if msg.get('transcript'):
            content.append({"type" : "text", "text" : f"Here is the transcript for the image : {msg.get('transcript')}"})

        message = [{"role" : "user", "content" : content}]

        if msg.get('cx_reply'):
            message.append({"role" : "assistant", "content" : msg.get('cx_reply')})

        return message

    def prepare_llm_message(self, msg, history):

        message = [{"role" : "system", "content" : grok_system_prompt}]

        for h in history:
            message+=self.prepare_single_message(h)

        message+=self.prepare_single_message(msg)
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
                response_format = ChatSuggestions,
                temperature=0.9,           # Controls randomness (0 to 1)
                top_p=0.9,  
            )
        response = response.choices[0].message.parsed
        
        return '- '+response.suggestion1 + '\n\n- ' + response.suggestion2 + '\n\n- ' + response.suggestion3  


class TranscribeChat:
    def __init__(self):
        pass 

    def get_transcript(self, base64img):

        # Define the messages for the chat
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": '''
### **Task:**  
Extract the transcript from a given chat screenshot image and return it as a structured list of dictionaries.  

### **Expected Output Format:**  
A list of dictionaries, where each dictionary represents a message with two keys:  
- **`type`**: Indicates whether the message is aligned to the left or right edge of the image.  
- **`content`**: Contains the text of the message.  

```python
[
    {'type': 'left' | 'right', 'content': 'text message here'},
    ...
]
```

### **Guidelines for Determining `type`:**  
- **Messages attached to the left edge of the image →** Assign `'left'`.  
- **Messages attached to the right edge of the image →** Assign `'right'`.  

### **Special Case:**  
- If a message has a **tagged mention (e.g., "@username")**, then **swap** its default alignment:  
  - Left-aligned messages should be marked as `'right'`.  
  - Right-aligned messages should be marked as `'left'`.  

Ensure the transcript accurately reflects the order and structure of the conversation.
                        '''
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64img}" 
                    }
                ]
            }
        ]

        model = "pixtral-12b-2409"

        # Get the chat response
        chat_response = mistral_client.chat.complete(
            model=model,
            messages=messages
        )

        # Print the content of the response
        return chat_response.choices[0].message.content
