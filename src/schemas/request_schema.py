from pydantic import BaseModel


class CreateBotRequestSchema(BaseModel):
    campaign_id:str
    campaign_name : str
    description: str
    chatbot_name : str
    postman_collection : str
    whatsapp_mobile_number : str

class ConversationRequestSchema(BaseModel):
    whatsapp_mobile_number : str
    sender_whatsapp_mobile_number : str 
    

class MediaConversation(BaseModel):
    whatsapp_mobile_number : str 
    sender_whatsapp_mobile_number : str 
    