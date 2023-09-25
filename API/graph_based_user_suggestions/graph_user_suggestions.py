import random
import requests

# Fetch my_following data using the provided URL
def my_following(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raises an exception for non-2xx responses
        # print(response.json())  # Assuming the response is in JSON format
        json_response = response.json()
        return json_response
    except requests.exceptions.RequestException as e:
        return e
        # print("An error occurred:", e)

def get_all_users(token:str):
    try:
        api = "https://apischema.freeschema.com/api/get-all-user-compositions"
        header = {
            "Authorization" : f"Bearer {token}"
        }
        response = requests.get(api, headers=header)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.RequestException as e:
        return e

# Main Recommend Users function
def recommend_users(graph, user, page=10, inpage=1, replace_concept_id=None):
    try:
        following = set(graph.successors(user))
        # print("Following:", following)

        recommended = set()
        for u in following:
            recommended.update(graph.successors(u))

        recommended.difference_update(following)
        recommended.discard(user)
        # print("Recommended:", recommended)

        if not recommended:
            all_users = set(graph.nodes())
            recommended = all_users - following
            recommended.discard(user)

        # print("Number of recommended users:", len(recommended))
        # print("Recommended Users:", recommended)

        start_idx = (page - 1) * inpage
        end_idx = start_idx + inpage
        recommended_users = list(recommended)[start_idx:end_idx]

        if replace_concept_id is None:
            print("Returning from regular")
            return recommended_users
        else:
            try:
                index = list(recommended).index(replace_concept_id)
                # print("Index:", index)
                # print("Replacement Concept ID:", replace_concept_id)

                friends = set(graph.successors(replace_concept_id))
                # print("Friends of Friend:", friends)

                if friends:
                    unfollowed_friends = [friend for friend in friends if friend not in following]

                    if unfollowed_friends:
                        recommended.discard(replace_concept_id)
                        list_recommended = list(recommended)
                        list_recommended.remove(unfollowed_friends[0])
                        list_recommended.insert(index, unfollowed_friends[0])
                        # print("From friends friend list :", list_recommended)
                        
                        recommended_users = list_recommended[start_idx:end_idx]
                        # print("From friends friend final :", recommended_users)

                        replaced_user_suggestion = {
                            "replace_concept_Id": unfollowed_friends[0],
                            "recommended_user": recommended_users,
                            "Remaining Users": len(list_recommended),
                            "Deleted User": replace_concept_id
                        }
                        return replaced_user_suggestion
                else:
                    try:
                        extract_user_index = page * inpage
                        replaced_with_value = list(recommended)[extract_user_index]
                        print("Replacement Value : ", replaced_with_value)
                        
                        list_recommended = list(recommended)
                        # print("Recommended Users List before replacement : ", list_recommended)
                        list_recommended[index] = replaced_with_value
                        # print("Recommended Users List after replacement : ", list_recommended)
                        list_recommended.pop(extract_user_index)  # Replace from the extracted index
                        # print("Recommended Users List after pop :", list_recommended)

                        recommended_users = list_recommended[start_idx:end_idx]

                        replaced_user_suggestion = {
                            "replace_concept_Id": replaced_with_value,
                            "recommended_user": recommended_users,
                            "Remaining Users": len(list_recommended),
                            "Deleted User": replace_concept_id
                        }
                        return replaced_user_suggestion
                    except IndexError:
                        return "No more index to return"
            except ValueError:
                # print("User not found in the list of recommended users")
                return recommended_users
    except Exception as e:
        # print("Error:", e)
        return ["<Info> User concept Id not available </Info>"]
