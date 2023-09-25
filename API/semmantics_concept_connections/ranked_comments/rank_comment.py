import requests 
from os import environ as env
import jwt
from datetime import datetime
from api_call.api_call import fetch_data_from_api

def authentication_apischema_post(api, type_param:str=None, page:int=1, inpage:int=10, token:str=None):
    try:
        header = {
            "Authorization":f"Bearer {token}"
        }
        parameters = {
            "type" : type_param,
            "page" : page,
            "inpage" : inpage
        }
        
        response = requests.post(api, headers=header, params=parameters)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return e


def decodeJWT(token: str):
    try:
        decoded_token = jwt.decode(token, env['SECRET_KEY'], algorithms = env['JWT_ALGORITHM'])
        exp_timestamp = decoded_token.get("exp", 0)
        current_timestamp = datetime.timestamp(datetime.utcnow())
        return decoded_token if exp_timestamp >= current_timestamp else None
    except jwt.ExpiredSignatureError:
        return {"Expired Signature"}
    except jwt.DecodeError:
        return {"error"}


def get_user_id(token: str):
    decoded_jwt = jwt.decode(token, env['SECRET_KEY'], algorithms=env['JWT_ALGORITHM'])
    user_id = decoded_jwt.get("unique_name")
    # print("User ID Type : ", type(user_id))
    return user_id


def get_all_users(BASE_URL, token:str):
    try:
        api = f"{BASE_URL}/get-all-user-compositions"
        header = {
            "Authorization" : f"Bearer {token}"
        }
        response = requests.get(api, headers=header)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.RequestException as e:
        return e
    


# def web_url_comments(api_url, token:str=None):
    
#     try:
#         header = {
#             "Authorization" : f"Bearer {token}"
#         }
#         response = requests.get(api_url, headers=header)
#         response.raise_for_status()
#         json_response = response.json()
#         return json_response
#     except requests.exceptions.RequestException as e:
#         print(f"Error : {e}")
#         return e
    

def get_user_concept_id(user_id, user_concepts):
    return next(key for key, value in user_concepts.items() if value == int(user_id))

def fetch_comments(api_url, jwt_token):
    url_commented_data = fetch_data_from_api(api_url, token=jwt_token)
    return url_commented_data['data']['data']

def friends_comments(BASE_URL, user_concept_id, token:str):
    get_secondary_link_api = f"{BASE_URL}/Connection/get-link-secondary?compositionId={user_concept_id}&linker=follow_s&secondaryLinker=url_comment_s"
    result = authentication_apischema_post(get_secondary_link_api, token=token)
    return result

