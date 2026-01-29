from fastapi import APIRouter
from src.schemas.request_schema import CreateBotRequestSchema
from src.utils.utilities import MainUtils,MongoUtils
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from src.prompt import static_prompt_v1
from dotenv import load_dotenv
import os 

load_dotenv()

## SETTING ENV VARIABLES

DB_CHATBOT_COLLECTION = os.getenv("DB_CHATBOT_COLLECTION")

## LOAD UTILITIES 

utils = MainUtils()
mongo_db_utils = MongoUtils()

## ROUTER 

router = APIRouter(tags=["Chatbot Creation"])

## ENDPOINTS 

@router.post("/create_chatbot")
async def create_chatbot(data:CreateBotRequestSchema):
    postman_collection_json = await utils.get_postman_collection(data.postman_collection)
    postman_collection = await utils.get_formatted_collection__(postman_collection_json)
    static_prompt_template = await utils.create_prompt_template(static_prompt_v1(),["campaign","context","postman_collection"])
    static_prompt = await static_prompt_template.ainvoke({
        "campaign":data.campaign_name,
        "context":data.description,
        "postman_collection":postman_collection
    })
    if not await mongo_db_utils.collection_exists(DB_CHATBOT_COLLECTION):
        collection = await mongo_db_utils.create_collection(DB_CHATBOT_COLLECTION,index_field="mobile")
    else : 
        collection = await mongo_db_utils.get_collection(DB_CHATBOT_COLLECTION)
    try:
        if await mongo_db_utils.insert_data(collection,{
            "campaign_id":data.campaign_id,
            "mobile":data.whatsapp_mobile_number,
            "campaign_name":data.campaign_name,
            "campaign_description":data.description,
            "static_prompt":static_prompt.text
        }):
            return JSONResponse(status_code=200,content={"success":True,"message":"chatbot created successfully"})
    except Exception as e: 
        return JSONResponse(status_code=409,content={"success":True,"message":f"{data.whatsapp_mobile_number} Already linked with chatbot name {data.campaign_name}"})
    
    else:
        HTTPException(status_code=500,detail="Some Internal Error Occured !")

        

    