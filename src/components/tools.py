from langchain.tools import tool
import requests

class Tools :     
    @tool
    def call_api(BASE_URL: str,endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
        """
        Generic API caller For all postman API you have 
        
        Args:
            BASE_URL (str) : BASE URL FOR API ENDPOINT Extracted from postman sample requests
            endpoint (str): API endpoint (e.g., '/specialities', '/appointments', '/book-appointment').
            method (str): HTTP method ("GET" or "POST").
            params (dict, optional): Query parameters for GET requests.
            data (dict, optional): JSON body for POST requests.
        
        Returns:
            dict: JSON response from the API
        """
        url = f"{BASE_URL}{endpoint}"
        print("MAKING AN API CALL : ",url)
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
                
            else:
                return {"error": f"Unsupported method {method}"}

            if response.status_code == 200:
                return {"success":True,"fatal":False,"tool_response":response.json()}
            else:
                return {
                        "success": False,
                        "fatal": True,
                        "message": "Sorry, our restaurant service is temporarily unavailable."
                    }
        except Exception as e:
            return {"error": str(e)}
        

