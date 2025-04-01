
from whatsapp_utils import WhatsappUtils
from llm_utils import ResponseSuggestor, TranscribeChat


wa_utils = WhatsappUtils()
response_suggestor = ResponseSuggestor()
trancribe = TranscribeChat()

class ChatConversationManager:
    def __init__(self):
        self.paid_contacts = ["918175847395", "919507899149", "918290650000" "919754532490"]
        self.unpaid_user_template = "Hey there! CharmerX is all about helping you charm your way to epic dates, but our magic’s reserved for our awesome paid crew. Want to level up your dating game with killer lines? Pop over to charmerx.com to join the fun or learn more—we’d love to have you on board!"

    def is_valid_contact(self, msg):
        sender = msg.get('From') 
        curr_number = sender.replace('whatsapp:+', '')
        if curr_number in self.paid_contacts:
            return True
        return True
    
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
                transcript = trancribe.get_transcript(base64img)
                msg["transcript"] = transcript
            
            suggestions = response_suggestor.get_chat_suggestions(msg, history)

            # (base64img , text and history k base prr generate reply )
            
            return suggestions
        else:
            return self.unpaid_user_template
        

    



