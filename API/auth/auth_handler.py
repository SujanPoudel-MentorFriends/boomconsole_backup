from os import environ as env
import jwt
from datetime import datetime, timedelta

# Create JWT Token
def create_token(SECRET_KEY, JWT_ALGORITHM):
    # Get the current time and calculate expiration and issued-at times
    current_time = datetime.utcnow()
    expiration_time = current_time + timedelta(hours=24)
    issued_at_time = current_time

    # Create a JWT token
    payload = {
        'unique_name': '10401',
        'email': 'learningsujan@gmail.com',
        'upn': '100274126',
        'nbf': int(issued_at_time.timestamp()),
        'exp': int(expiration_time.timestamp()),
        'iat': int(issued_at_time.timestamp())
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return token
 


def decodeJWT(token: str):
    decoded_token = jwt.decode(token, env['SECRET_KEY'], algorithms = env['JWT_ALGORITHM'])
    # print(decoded_token)
    try:
        decoded_token = jwt.decode(token, env['SECRET_KEY'], algorithms = env['JWT_ALGORITHM'])
        exp_timestamp = decoded_token.get("exp", 0)
        current_timestamp = datetime.timestamp(datetime.utcnow())
        return decoded_token if exp_timestamp >= current_timestamp else None
    except jwt.ExpiredSignatureError:
        return {"Expired Signature"}
    except jwt.DecodeError:
        return {"error on token"}


def get_user_id(token: str):
    decoded_jwt = decodeJWT(token) # Call function to decode jwt
    try:
        print(decoded_jwt)
        user_id = decoded_jwt.get("unique_name")
        return user_id
    except:
        decoded_jwt

def get_user_concept_id(token:str):
    decoded_jwt = decodeJWT(token) # Call function to decode jwt
    try:
        user_concept_id = decoded_jwt.get("upn")
        # print("User Concept Id : ", user_concept_id)
        return user_concept_id
    except:
        decoded_jwt
