from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.server_api import ServerApi
from src.exception import CustomException
from typing import TypedDict
from langchain_core.prompts import PromptTemplate
import requests
import os 
import sys

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
DB_CHATBOT_COLLECTION = os.getenv("DB_CHATBOT_COLLECTION")
DB_CONVERSATION_COLLECTION = os.getenv("DB_CONVERSATION_COLLECTION")

class MainUtils:
    def __init__(self):
        pass 

    async def get_postman_collection(self,postman_collection_link):
        try:
            response = requests.get(postman_collection_link)
            return response.json()
        except Exception as e:
            raise CustomException(e,sys)
    
    async def get_formatted_collection__(self,postman_collection_data):
        output = []
        collection_name = postman_collection_data['collection']['info']['name']
        collection_description = postman_collection_data['collection']['info']['description']
        for item in postman_collection_data['collection']['item']:
            block = []
            item_name = item.get('name', '')
            req = item.get('request', {})
            desc = req.get('description', '').strip()
            method = req.get('method', '')
            url = req.get('url', {}).get('raw', '')
            block.append(f"name :  {item_name}")
            block.append(f"request description:  {desc}")
            block.append(f"request method:  {method}")
            block.append(f"request url:  {url}")
            if method == 'POST' and 'body' in req and 'raw' in req['body']:
                block.append("Example Request Body : ")
                block.append(req['body']['raw'])
            output.append("\n".join(block))
        return collection_name + "\n"+collection_description+"\n\n"+"\n\n".join(output)

    async def create_prompt_template(self,template,input_varaibles):
        try:
            return PromptTemplate(
                template=template,
                input_variables = input_varaibles
            )
        except Exception as e:
            raise CustomException(e,sys)



class MongoUtils:
    def __init__(self):
        self.mongo_client = AsyncMongoClient(MONGODB_URI,server_api=ServerApi('1'))
        self.db = self.mongo_client[DB_NAME]

    async def get_collection(self,collection_name:str):
        return self.db[collection_name]
    
    async def collection_exists(self,collection_name:str):
        try:
            if collection_name in await self.db.list_collection_names():
                return True 
            else:
                return False
        except Exception as e:
            raise(e)
    
    async def create_collection(self,collection_name:str,index_field:str):
        try:
            collection : AsyncCollection = await self.db.create_collection(collection_name)
            await collection.create_index([(index_field, 1)], unique=True)
            return True
        except Exception as e:
            raise(e)
        
    async def insert_data(self,collection,data:dict):
        try:
            response = await collection.insert_one(data)
            if response.acknowledged:
                return True
            else:
                False
        except Exception as e:
            raise(e)

    async def search_data(self,collection,data):
        try:
            result = await collection.find_one(data)
            return result
        
        except Exception as e:
            raise(e)
