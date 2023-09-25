import requests


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


def get_friends_friends_with_mutual_count(BASE_URL, my_concept_id, jwt_token:str):
    friends_friend_api = f"{BASE_URL}/Connection/get-link-secondary?compositionId={my_concept_id}&linker=follow_s&secondaryLinker=follow_s"
    my_friends = authentication_apischema_post(friends_friend_api, token=jwt_token)

    # loop through secondary linker
    friends_set = set()  # For own friend
    friends_friends = {}
    friends_friends_following = []

    for output in my_friends['output']:
        friend_id = output['id']
        friends_set.add(friend_id)
        follow_s = output['follow_s']
        friends_friends_following.extend(follow_s)  # Add all follow_s in list
        friend_friends_id = {val['id'] for val in follow_s}  # Insert friend friends into set
        for d in friend_friends_id:
            if d not in friends_friends:
                friends_friends[d] = set()
            friends_friends[d].add(friend_id)


    sorted_friends_friends = dict(sorted(friends_friends.items(), key= lambda x: len(x[1]), reverse=True))
        
#     print("My Friends : ", friends_set)
#     print(sorted_friends_friends)    

#     for friend, mutual in sorted_friends_friends.items():
#         print(f"friend {friend} has mutual friends {mutual}")
    
    sorted_friends_friends_without_own_follow = [friend for friend, mutual in sorted_friends_friends.items() if friend not in friends_set]
    # print("sorted_friends_friends_without_own_follow : ", sorted_friends_friends_without_own_follow)
    
    # print(friends_friends_following)
    sorted_friends_friends_without_own_follow_and_data = [ data for data in friends_friends_following if data['id'] in sorted_friends_friends_without_own_follow ]
    
    return sorted_friends_friends_without_own_follow, sorted_friends_friends_without_own_follow_and_data
