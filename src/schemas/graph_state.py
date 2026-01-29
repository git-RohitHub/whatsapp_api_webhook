from typing import TypedDict,Annotated,Optional
from langchain_core.messages import BaseMessage
import operator

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]  
    user_details: str                                      
    last_user_query: Optional[BaseMessage]

