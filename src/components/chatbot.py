from src.exception import CustomException 
from src.schemas.graph_state import ChatState
from langgraph.graph import StateGraph,START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage,ToolMessage,HumanMessage,AIMessage
from langgraph.prebuilt import ToolNode,tools_condition
from src.components.tools import Tools
from openai import RateLimitError
from src.utils.utilities import MainUtils
from langchain_core.runnables import RunnableLambda
import os
import sys
import datetime
import time
import json

from dotenv import load_dotenv
load_dotenv()

llm_name = os.getenv("LLM_NAME")

class ChatGraph:
    def __init__(self,mobile_number,retriever):
        self.retriever = retriever
        self.mobile_number = mobile_number
        self.date = datetime.datetime.now()
        self.utils = MainUtils()
        self.tool_obj = Tools()
        self.tools = [self.tool_obj.call_api]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.chain = self.chat_prompt | RunnableLambda(self.get_llm_response)
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()


    def _build_graph(self):
        """Setup the state graph with nodes & edges."""
        graph = StateGraph(ChatState)
        graph.add_node("chat_node", self.chatnode)
        graph.add_node("tools", ToolNode(self.tools))
        graph.add_node("get_user_details",self.get_detail)
        graph.add_edge(START, "chat_node")
        graph.add_edge("chat_node","get_user_details")
        graph.add_edge("tools", "chat_node")
        graph.add_conditional_edges("chat_node", tools_condition)
        return graph

    async def cut_messages_len(self,messages: list[BaseMessage]) -> list[BaseMessage]:
        try:
            conversation=[]
            for m in messages:
                if isinstance(m,ToolMessage):
                    conversation.append(m)

                elif isinstance(m,AIMessage):
                    conversation.append(AIMessage(content=m.content))
                else:
                    conversation.append(HumanMessage(content=m.content))
            return conversation
        except Exception as e:
            raise CustomException(e,sys)
        
    async def get_user_details(self,user_detail,conversation):
        prompt = f"You will be providing the current user detail we have and the last 4 conversation your task is to add new detail from the last conversation to the current detail , Current User Detail: {user_detail}, Last 4 conversation : {conversation}. ## NOTE : Include all important user details and do not provide any preamble or postamble. \n"
        response = self.utils.groq_llm.invoke(prompt)
        return response.content

    async def get_detail(self,state:ChatState) -> ChatState:
        messages = state['messages']
        current_user_detail = state.get("user_details", "")
        if len(messages)%4==0 and len(messages)!=0:
            updated_user_detail = await self.get_user_details(current_user_detail,messages[-4:])
            return {"user_details":updated_user_detail}
        return {"user_details":""}

    async def chatnode(self,state: ChatState) -> ChatState:
        try:
            messages = state["messages"]
            user_details = state.get("user_details", "")
            last_user_message = messages[-1]
            if isinstance(messages[-1],ToolMessage):
                payload = json.loads(last_user_message.content)
                if not payload['success']:
                    return {"messages": [AIMessage(content=payload['message'])]}
            query = await self.utils.reframe_query(last_user_message,messages[-5:])
            query_text = query.content if hasattr(query, "content") else str(query)
            pdf_context = self.retriever.invoke(query_text)
            print("USER_STMT",last_user_message)
            start_time = time.perf_counter()
            response = await self.chain.ainvoke({
                'campaign':self.campaign_name,
                'context':self.campaign_description,
                'formatted_collection':self.formatted_collection,
                'user_details':user_details,
                'conversation':messages[-20:],
                'pdf_context':pdf_context,
                'mobile_number':self.mobile_number,
                'date_time':self.date,
            })
            if isinstance(response,AIMessage):
                if len(response.tool_calls)==0:
                    response = AIMessage(content = response.content[0]['text'])
            print("RESPONSE : ",response)
            end_time = time.perf_counter()
            print(f"Latency: {end_time - start_time:.3f} sec")
            return {"messages": [response]}
        except RateLimitError:
            raise Exception("Failed to call OpenAI API due to rate limit.")
        except Exception as e:
            raise CustomException(e,sys) 
        
    def chatbot(self):
        """Compile and return chatbot graph."""
        return self.graph.compile(checkpointer=self.checkpointer)
