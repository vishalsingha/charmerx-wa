
from whatsapp_utils import WhatsappUtils
from llm_utils import ResponseSuggestor

wa_utils = WhatsappUtils()
response_suggestor = ResponseSuggestor()

class ChatConversationManager:
    def __init__(self):
        self.paid_contacts = ["918175847395"]
        self.unpaid_user_template = "BKL pase de pahle"
        self.invalid_img_template = "BKL chat/dating profile ya phir ladki i photo upload krr."

    def is_valid_contact(self, msg):
        sender = msg.get('From') 
        curr_number = sender.replace('whatsapp:+', '')
        if curr_number in self.paid_contacts:
            return True
        return False
    
    def validate_img_quality(self, base64img):
        if base64img is None:
            return True
        return True
    
    
    def handle_conversation(self, msg, history):
        if self.is_valid_contact(msg):
            sender = msg.get('From') 
            message_id = msg.get('SmsMessageSid')  
            media_url = msg.get('MediaUrl0') 
            whatsapp_number = sender.replace('whatsapp:+', '') 
            text_msg = msg.get('Body') 
            base64img = None
            valid_img_flag = self.validate_img_quality(base64img)

            if valid_img_flag==False:
                return self.invalid_img_template
            
            if media_url:
                base64img = wa_utils.save_media(msg)

            suggestions = response_suggestor.get_chat_suggestions(msg, history)

            # (base64img , text and history k base prr generate reply )
            
            return suggestions
        else:
            return self.unpaid_user_template
        

    



