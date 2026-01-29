from fastapi import APIRouter
from src.schemas.request_schema import ConversationRequestSchema
router = APIRouter(tags=["Chatbot Conversation"])

@router.post("/conversation")
def do_conversation(data:ConversationRequestSchema):
    ## Genereate response on user query 
    
    ## stor the conversation chain 
    
    ## send the message on whatsapp 
    pass



