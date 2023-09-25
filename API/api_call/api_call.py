import requests


def fetch_data_from_api(api, token:str):
    try:
        header = {
            "Authorization" : f"Bearer {token}"
        }
        response = requests.get(api, headers=header)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.RequestException as e:
        return e


def fetch_data_from_api_post(api, token:str):
    try:
        header = {
            "Authorization" : f"Bearer {token}"
        }
        response = requests.post(api, headers=header)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.RequestException as e:
        return e


# Extract my_following
def my_following(api_url, token):
    try:
        header = {
            "Authorization" : f"Bearer {token}"
        }
        response = requests.get(api_url, headers=header)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.RequestException as e:
        print(f"Error : {e}")
        return {'Error : 401 Client Error: Unauthorized for url:'+api_url}



def my_following_to(api_url, token):
    try:
        header = {
            "Authorization" : f"Bearer {token}"
        }
        response = requests.get(api_url, headers=header)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.RequestException as e:
        # print(f"Error : {e}")
        return e

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
