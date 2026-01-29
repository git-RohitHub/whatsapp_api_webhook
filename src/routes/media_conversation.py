from fastapi import APIRouter
from src.schemas.request_schema import MediaConversation

router = APIRouter(tags=["Media Conversation"])


@router.post("/media_conversation")
def handle_voice_note(data:MediaConversation):

    pass

