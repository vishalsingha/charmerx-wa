

import re
import os
import requests
import base64
from twilio.twiml.messaging_response import MessagingResponse


source_code_location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_location = f"{source_code_location}/data"



class WhatsappUtils:
    def __init__(self):
        pass

    def parse_twilio_media_url(self, media_url):
        # Using regex to extract the required IDs
        pattern = r"Accounts/(?P<account_id>AC[a-zA-Z0-9]+)/Messages/(?P<message_id>MM[a-zA-Z0-9]+)/Media/(?P<media_id>ME[a-zA-Z0-9]+)"
        
        match = re.search(pattern, media_url)
        if match:
            return match.group("account_id"), match.group("message_id"), match.group("media_id")
        else:
            return None, None, None
        
    def save_media(self, msg):

        whatsapp_number = msg.get('From').replace('whatsapp:+', '') 
        message_id = msg.get('SmsMessageSid')  # Unique message ID
        media_url = msg.get('MediaUrl0')  # Media URL
    
        content_type = msg.get('MediaContentType0')  # Media type
        ext = content_type.split('/')[1]  # Extract file extension

        _, _, media_id = self.parse_twilio_media_url(media_url)
        r = msg.get(media_url)
        
        

        # Ensure user directory exists
        user_dir = f'{data_location}/uploads/{whatsapp_number}'
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # Create filenames
        filename = f'{user_dir}/{whatsapp_number}_{message_id}_{media_id}.{ext}'

        image_data = r.content
        base64img = base64.b64encode(image_data).decode('utf-8')

        with open(filename, 'wb') as f:
            f.write(image_data)

        return base64img
    
    def respond(self, message):
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    