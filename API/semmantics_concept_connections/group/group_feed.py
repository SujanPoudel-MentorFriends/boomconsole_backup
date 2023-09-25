import requests
from api_call.api_call import fetch_data_from_api, fetch_data_from_api_post, my_following_to, get_all_users



def count_group(BASE_URL, token, user_cid):
    # print("User concept Id : ", user_cid)
    enrolled_group = f"{BASE_URL}/Connection/get-link?compositionId={user_cid}&linker=group_members_by&inpage=10&page=1"
    # print("Enrolled Graph : ", enrolled_group)
    group = fetch_data_from_api(enrolled_group, token)
    # print("Group : ", group)
    total = group['count']
    return int(total)


def get_link_linker_data(BASE_URL, token, composition_id, linker, page:int=1, inpage:int=10):
    
    try:
        
        api = f"{BASE_URL}/Connection/get-link?compositionId={composition_id}&linker={linker}&inpage={inpage}&page={page}"

        headers = {
            "Authorization" : f"Bearer {token}"
        }

        response = requests.get(api, headers= headers)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    
    except requests.exceptions.RequestException as e:
        return e



def process_group(BASE_URL, group, jwt_token):
    group_id = group['id']
    boom_shared_boomgpt_linker = f"{BASE_URL}/Connection/get-link?compositionId={group_id}&linker=group_shared_boomgpt_s&inpage=10&page=1"
    shared_gpt = fetch_data_from_api(boom_shared_boomgpt_linker, jwt_token)

    if shared_gpt['count'] != 0:
        data = {
            "group_data": group,
            "group_data_total_count": shared_gpt['count']
        }
        return data
    else:
        return None

    

def process_group_post(BASE_URL, group_post, jwt_token):
    group_id = int(group_post['group_data']['id'])
    total_group_post = group_post['group_data_total_count']
    
    # Function to fetch linker data with linker name "group_shared_boomgpt_s" from group id
    group_shared_gpt_data = get_link_linker_data(BASE_URL, token=jwt_token, composition_id=group_id, linker='group_shared_boomgpt_s', page=1, inpage=total_group_post)

    group_shared_data = []

    for group_post_data in group_shared_gpt_data['output']:
        post_id = int(group_post_data['id'])
        # Function to fetch linker data with linker name "group_shared_boomgpt_data_s" from shared_post_id
        group_post_shared_data = get_link_linker_data(BASE_URL, token=jwt_token, composition_id=post_id, linker='group_shared_boomgpt_data_s', page=1, inpage=total_group_post)

        combined_data = {
            'group_post_shared_by': group_post['group_data'],
            'group_post_shared': group_post_data,
            'group_shared_post_data': group_post_shared_data
        }
        group_shared_data.append(combined_data)

    return group_shared_data
