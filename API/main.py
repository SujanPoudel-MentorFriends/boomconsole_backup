from os import environ as env
import sqlalchemy
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
import requests
from cachetools import cached, TTLCache
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from fastapi.middleware.cors import CORSMiddleware
import jwt
import time
from threading import Thread

from auth.auth_bearer import JWTBearer
from auth.auth_handler import create_token, decodeJWT, get_user_id, get_user_concept_id
from api_call.api_call import fetch_data_from_api, fetch_data_from_api_post, my_following_to, get_all_users

from graph_based_user_suggestions import graph_user_suggestions
from comment_ranking import rank_comments
from shared_post_recommendation import shared_post

from semmantics_concept_connections.ranked_comments import rank_comment
from semmantics_concept_connections.user_suggestions.user_recommend import get_friends_friends_with_mutual_count
from semmantics_concept_connections.group import group_feed

app = FastAPI()

PROD_BASE_API_URL = env['PROD_BASE_API_URL']
DEV_BASE_API_URL = env['DEV_BASE_API_URL']

# Configure CORS settings
origins = [
    # PROD_BASE_API_URL,
    # DEV_BASE_API_URL
    "https://devboom.freeschema.com",
    "http://apischema.freeschema.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],  #  allowed headers 
)

# Create a cache with a TTL of 5 minutes (300 seconds)
cache = TTLCache(maxsize=100, ttl=300)

    
def preload_cache():
    # Preload the cache during server startup
    api = f"{PROD_BASE_API_URL}/concepts/list-with-total?type=the_user"
    print(api)
    token = create_token(env['SECRET_KEY'], env['JWT_ALGORITHM'])  # Create JWT_TOKEN
    data = fetch_data_from_api(api, token)

    # print("Daata : ", data)
    
    size = data['data']['total']

    print("Size : ", size)    
    api_total = f"{PROD_BASE_API_URL}/concepts/list-with-total?type=the_user&page={1}&inpage={size}"
    
    all_data = fetch_data_from_api(api_total, token)
    
    # Cache the preloaded data
    cache["all_users"] = all_data

# Function to periodically preload the cache
def preload_cache_periodically():
    while True:
        preload_cache()  # Preload the cache
        time.sleep(600)  # Wait for 10 minutes (600 seconds)

# Start the preload_cache_periodically function in a separate thread
preload_thread = Thread(target=preload_cache_periodically)
preload_thread.start()



@app.get("/")
def default_api():
    response = {
        "status" : "200",
        "message" : "API RUN Successfully"
    }
    return response


# FastAPI endpoint
@app.get("/api/get_url_comments", dependencies=[Depends(JWTBearer())], tags=["Web URL Comments"])
def suggested_url_comments(page: int = 1, inpage: int = 20, jwt_token: str = Depends(JWTBearer())):
    with ThreadPoolExecutor(max_workers=2) as executor:
        user_id = executor.submit(get_user_id, token=jwt_token).result()
        result_get_all_users = executor.submit(get_all_users, PROD_BASE_API_URL, token=jwt_token).result()
    
    print("Results Get all users : ", result_get_all_users)

    user_concepts = result_get_all_users['userConcepts']      # Get user concepts id
    my_concept_id = rank_comment.get_user_concept_id(user_id, user_concepts)  # Convert user id to concept id
        
    result = rank_comment.friends_comments(PROD_BASE_API_URL, my_concept_id, jwt_token)  # Fetch friends comments 
    print(result)
    friends_url_comment = []
    comments_id = set()
    
    # Go inside friends comment with linker 'follow_s'
    for output in result['output']:
        for url_comment_s in output['url_comment_s']:
            friends_url_comment.append(url_comment_s)
            comments_id.add(url_comment_s['id'])
    
    # Sort by date descending
    friend_ranked_comments = sorted(friends_url_comment, key=lambda x: x['data']['boomext_web_comments']['created_on'], reverse=True)
    
    # Calculate number of required comments
    required_comments = page * inpage
    # Calculate remainig comments other than friends comment to fulfill pagination
    remaining_comments_length = required_comments - len(friend_ranked_comments)
    
    print("Remaining Comments Length : ", remaining_comments_length)
    
    # Check for 
    if remaining_comments_length > 0:
        api_with_user_id = f"{PROD_BASE_API_URL}/concepts/list-with-total?type=boomext_web_comments&page=1&inpage={remaining_comments_length+len(friend_ranked_comments)}"
        random_comments = rank_comment.fetch_comments(api_with_user_id, jwt_token)
        random_comments = [comment for comment in random_comments if comment["id"] not in comments_id]
    
    all_ranked_comments = friend_ranked_comments + random_comments
    start_index = (page - 1) * inpage
    end_index = start_index + inpage
    ranked_comments_page = all_ranked_comments[start_index:end_index]
    
    return ranked_comments_page


@app.get("/devapi/get_url_comments", dependencies=[Depends(JWTBearer())], tags=["Web URL Comments"])
def suggested_url_comments(page: int = 1, inpage: int = 20, jwt_token: str = Depends(JWTBearer())):
    with ThreadPoolExecutor(max_workers=2) as executor:
        user_id = executor.submit(get_user_id, token=jwt_token).result()
        result_get_all_users = executor.submit(get_all_users, DEV_BASE_API_URL, token=jwt_token).result()
    
    print("Result Get All Users : ", result_get_all_users)
    user_concepts = result_get_all_users['userConcepts']      # Get user concepts id
    my_concept_id = rank_comment.get_user_concept_id(user_id, user_concepts)  # Convert user id to concept id
        
    result = rank_comment.friends_comments(DEV_BASE_API_URL, my_concept_id, jwt_token)  # Fetch friends comments 
    print("Result : ", result)
    friends_url_comment = []
    comments_id = set()
    
    # Go inside friends comment with linker 'follow_s'
    for output in result['output']:
        for url_comment_s in output['url_comment_s']:
            friends_url_comment.append(url_comment_s)
            comments_id.add(url_comment_s['id'])
    
    # Sort by date descending
    friend_ranked_comments = sorted(friends_url_comment, key=lambda x: x['data']['boomext_web_comments']['created_on'], reverse=True)
    
    # Calculate number of required comments
    required_comments = page * inpage
    # Calculate remainig comments other than friends comment to fulfill pagination
    remaining_comments_length = required_comments - len(friend_ranked_comments)
    
    print("Remaining Comments Length : ", remaining_comments_length)
    
    # Check for 
    if remaining_comments_length > 0:
        api_with_user_id = f"{DEV_BASE_API_URL}/concepts/list-with-total?type=boomext_web_comments&page=1&inpage={remaining_comments_length+len(friend_ranked_comments)}"
        random_comments = rank_comment.fetch_comments(api_with_user_id, jwt_token)
        random_comments = [comment for comment in random_comments if comment["id"] not in comments_id]
    
    all_ranked_comments = friend_ranked_comments + random_comments
    start_index = (page - 1) * inpage
    end_index = start_index + inpage
    ranked_comments_page = all_ranked_comments[start_index:end_index]
    
    return ranked_comments_page

@app.get("/api/get_user_suggestions", dependencies=[Depends(JWTBearer())])
async def user_suggestion(page:int=1, inpage:int=10, recent_follow:int=None, jwt_token: str = Depends(JWTBearer())):

    try:
        print("inside it..........")
        init_start = time.time()
        my_concept_id = get_user_concept_id(token=jwt_token)
        print("My concept Id : ", my_concept_id)
        init_end = time.time()
        print(f"Init part takes {init_end-init_start} sec ")

        second_start = time.time()

        with ThreadPoolExecutor(max_workers=2) as executor:
            in_time = time.time()
            result_get_all_users = await cache.get("all_users")
            print(" Result Get All Users : ", result_get_all_users)
            if result_get_all_users is None:
                return {"message": "Data not available"}
            # result_get_all_users = executor.submit(fetch_all_data_from_api, token=jwt_token).result()
            end_time  = time.time()
            print(f"Time inside : {end_time - in_time}")
            friend_suggestions, friend_suggestions_with_data = executor.submit(get_friends_friends_with_mutual_count, PROD_BASE_API_URL, my_concept_id=my_concept_id, jwt_token=jwt_token).result()

        second_end = time.time()
        print(f"Second part takes {second_end - second_start} sec ")


        # print("Mutual Friends : ", friend_suggestions)
        random_users = []

        third_start = time.time()    
        total_data_needed = page * inpage
        remaining_data = total_data_needed - len(friend_suggestions)

        if remaining_data > 0 :
            count = 0     
            # print(result_get_all_users)
            users_data = result_get_all_users["data"]["data"]
            for data in users_data:
                if isinstance(data['data']['the_user'], dict):
                    user_cid = int(data["id"])
                    if user_cid not in friend_suggestions and my_concept_id != int(user_cid):
                        if remaining_data == count:
                            break
                        else:
                            random_users.append(data)
                            count += 1


        # print(random_users)
        third_end = time.time()
        print(f"Third part takes {third_end-third_start} sec ")

        final_recommendation = friend_suggestions_with_data + list(random_users)

        # print("Final Recommendation : ", final_recommendation)
        start_index = (page-1) * inpage
        end_index = start_index + inpage
        
        print("-------------------")
        print("Final Recommendation : " , final_recommendation)
        

        return final_recommendation[start_index:end_index]

    except Exception as e:
        return e

@app.get("/devapi/get_user_suggestions", dependencies=[Depends(JWTBearer())])
async def user_suggestion(page:int=1, inpage:int=10, recent_follow:int=None, jwt_token: str = Depends(JWTBearer())):

    try:
        init_start = time.time()
        my_concept_id = get_user_concept_id(token=jwt_token)
        print("My concept Id : ", my_concept_id)
        init_end = time.time()
        print(f"Init part takes {init_end-init_start} sec ")

        second_start = time.time()

        with ThreadPoolExecutor(max_workers=2) as executor:
            in_time = time.time()
            result_get_all_users = await cache.get("all_users")
            if result_get_all_users is None:
                return {"message": "Data not available"}
            # result_get_all_users = executor.submit(fetch_all_data_from_api, token=jwt_token).result()
            end_time  = time.time()
            print(f"Time inside : {end_time - in_time}")
            friend_suggestions, friend_suggestions_with_data = executor.submit(get_friends_friends_with_mutual_count, DEV_BASE_API_URL, my_concept_id=my_concept_id, jwt_token=jwt_token).result()

        second_end = time.time()
        print(f"Second part takes {second_end - second_start} sec ")


        # print("Mutual Friends : ", friend_suggestions)
        random_users = []

        third_start = time.time()    
        total_data_needed = page * inpage
        remaining_data = total_data_needed - len(friend_suggestions)

        if remaining_data > 0 :
            count = 0     
            # print(result_get_all_users)
            users_data = result_get_all_users["data"]["data"]
            for data in users_data:
                if isinstance(data['data']['the_user'], dict):
                    user_cid = int(data["id"])
                    if user_cid not in friend_suggestions and my_concept_id != int(user_cid):
                        if remaining_data == count:
                            break
                        else:
                            random_users.append(data)
                            count += 1


        # print(random_users)
        third_end = time.time()
        print(f"Third part takes {third_end-third_start} sec ")

        final_recommendation = friend_suggestions_with_data + list(random_users)

        # print("Final Recommendation : ", final_recommendation)
        start_index = (page-1) * inpage
        end_index = start_index + inpage
        
        print("-------------------")
        

        return final_recommendation[start_index:end_index]

    except Exception as e:
        return e


@app.get("/api/get_group_feed_without_secondary_linkers", dependencies=[Depends(JWTBearer())], tags=["Group Feeds"])
def group_data(page:int=1, inpage:int=10, jwt_token: str = Depends(JWTBearer())):
    user_cid = get_user_concept_id(jwt_token)
    
    total_count = group_feed.count_group(PROD_BASE_API_URL, jwt_token, user_cid)
    enrolled_group = f"{PROD_BASE_API_URL}/Connection/get-link?compositionId={user_cid}&linker=group_members_by&inpage={total_count}&page=1"
    group = fetch_data_from_api(enrolled_group, jwt_token)
    # print(group['count'])
    group_list = [ i['id'] for i in group['output'] ]
    group_list_with_info = [ i for i in group['output'] ]
    
    # print("Group with info : ", group_list_with_info)
    
    
    group_posts = []
    
    # Create a ThreadPoolExecutor to execute the loop in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(group_feed.process_group, PROD_BASE_API_URL, group, jwt_token) for group in group_list_with_info]

    # Collect the results as they become available
    group_posts = []
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result is not None:
            group_posts.append(result)
        

    # Create a ThreadPoolExecutor to execute the loop in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(group_feed.process_group_post, PROD_BASE_API_URL,  group_post,  jwt_token) for group_post in group_posts]

    # Collect the results as they become available
    group_shared_data = []
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        group_shared_data.extend(result)

    # Reverse sort the list based on 'shared_on' date
    sorted_group_posts = sorted(group_shared_data, key=lambda x: int(x['group_post_shared']['data']['boom_shared_group_post']['shared_on']), reverse=True)
    
    start_index =  ( page - 1 ) * inpage
    end_index = start_index + inpage


    indexed_data = sorted_group_posts[start_index:end_index]


    return indexed_data



@app.get("/devapi/get_group_feed_without_secondary_linkers", dependencies=[Depends(JWTBearer())], tags=["Group Feeds"])
def group_data(page:int=1, inpage:int=10, jwt_token: str = Depends(JWTBearer())):
    user_cid = get_user_concept_id(jwt_token)
    
    total_count = group_feed.count_group(DEV_BASE_API_URL, jwt_token, user_cid)
    enrolled_group = f"{DEV_BASE_API_URL}/Connection/get-link?compositionId={user_cid}&linker=group_members_by&inpage={total_count}&page=1"
    group = fetch_data_from_api(enrolled_group, jwt_token)
    # print(group['count'])
    group_list = [ i['id'] for i in group['output'] ]
    group_list_with_info = [ i for i in group['output'] ]
    
    # print("Group with info : ", group_list_with_info)
    
    
    group_posts = []
    
    # Create a ThreadPoolExecutor to execute the loop in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(group_feed.process_group, DEV_BASE_API_URL, group, jwt_token) for group in group_list_with_info]

    # Collect the results as they become available
    group_posts = []
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result is not None:
            group_posts.append(result)
        

    # Create a ThreadPoolExecutor to execute the loop in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(group_feed.process_group_post, DEV_BASE_API_URL,  group_post,  jwt_token) for group_post in group_posts]

    # Collect the results as they become available
    group_shared_data = []
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        group_shared_data.extend(result)

    # Reverse sort the list based on 'shared_on' date
    sorted_group_posts = sorted(group_shared_data, key=lambda x: int(x['group_post_shared']['data']['boom_shared_group_post']['shared_on']), reverse=True)
    
    start_index =  ( page - 1 ) * inpage
    end_index = start_index + inpage


    indexed_data = sorted_group_posts[start_index:end_index]


    return indexed_data
    

# @app.get("/get_group_feed_without_secondary_linker", dependencies=[Depends(JWTBearer())])
# def group_data(page:int=1, inpage:int=10, jwt_token: str = Depends(JWTBearer())):
#     user_cid = get_user_concept_id(jwt_token)
    
#     total_count = group_feed.count_group(jwt_token, user_cid)
#     enrolled_group = f"{BASE_API_URL}/Connection/get-link?compositionId={user_cid}&linker=group_members_by&inpage={total_count}&page=1"
#     group = fetch_data_from_api(enrolled_group, jwt_token)
#     # print(group['count'])
#     group_list = [ i['id'] for i in group['output'] ]
#     group_list_with_info = [ i for i in group['output'] ]
    
#     # print("Group with info : ", group_list_with_info)
    
#     group_posts = []
    
#     for group in group_list_with_info:
#         group_id = group['id']
#         # group_name = group['data']['connectionGroup']['groupName']
#         boom_shared_boomgpt_linker = f"{BASE_API_URL}/Connection/get-link?compositionId={group_id}&linker=group_shared_boomgpt_s&inpage=10&page=1"
#         shared_gpt = fetch_data_from_api(boom_shared_boomgpt_linker, jwt_token)
        
#         # print("Group Name : ", group)
#         # print(shared_gpt)

#         if shared_gpt['count'] != 0:
#             data = {
#                 "group_data" : group,
#                 "group_data_total_count" : shared_gpt['count']
#             }
#             group_posts.append(data)
#         else:
#             # print("Detected..")
#             pass
       
#     group_shared_data = []
    
#     # Retrieve all individual group total post
#     for group_post in group_posts:
#         group_id = int(group_post['group_data']['id'])
#         total_group_post = group_post['group_data_total_count']
                
#         # Function to fetch linker data with linker name "group_shared_boomgpt_s" from group id
#         group_shared_gpt_data = group_feed.get_link_linker_data(token=jwt_token, composition_id = group_id, linker='group_shared_boomgpt_s', page=1, inpage=total_group_post )
        
        
#         for group_post_data in group_shared_gpt_data['output']:                
#             post_id = int(group_post_data['id'])
#             # Function to fetch linker data with linker name "group_shared_boomgpt_data_s" from shared_post_id
#             group_post_shared_data = group_feed.get_link_linker_data(token=jwt_token, composition_id = post_id, linker='group_shared_boomgpt_data_s', page=1, inpage=total_group_post )
            
#             combined_data = {
#                 'group_post_shared_by' : group_post['group_data'],
#                 'group_post_shared' : group_post_data,
#                 'group_shared_post_data' : group_post_shared_data
#             }
#             group_shared_data.append(combined_data)
    
#     # Reverse sort the list based on 'shared_on' date
#     sorted_group_posts = sorted(group_shared_data, key=lambda x: int(x['group_post_shared']['data']['boom_shared_group_post']['shared_on']), reverse=True)
    
#     start_index =  ( page - 1 ) * inpage
#     end_index = start_index + inpage

#     print(start_index, ' ', end_index)

#     indexed_data = sorted_group_posts[start_index:end_index]

#     print("Indexed Data : ", indexed_data)

#     return indexed_data


    