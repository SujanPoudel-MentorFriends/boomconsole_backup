# Main.py History


# @app.get("/get_recommended_boom_shared_post", dependencies=[Depends(JWTBearer())])
# def recommended_shared_post(page:int = 1, inpage:int = 10, jwt_token: str = Depends(JWTBearer())):
    
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         # API CALL
#         result_get_all_users = get_all_users(jwt_token)  
#         # own user id
#         user_id = int(get_user_id(jwt_token))  # Get user id based on token

#     # Convert userid to user_concept_id
#     my_concept_id = next(int(key) for key, value in result_get_all_users['userConcepts'].items() if value == user_id) 
#     # print("My concept id : ", my_concept_id)
    
#     # api_search_my_following = "https://apischema.freeschema.com/api/searchConcept?composition=my_following&search="+str(my_concept_id)+"&type=followed_by&page=1&inpage=1000"
#     api_search_my_following = f"https://apischema.freeschema.com/api/searchConcept?composition=my_following&search={my_concept_id}&type=followed_by&page=1&inpage=1000"
    
#     # my_following_list = my_following(api_search_my_following, jwt_token)  # Call my_following composition from api
    
#     # Load functions concurrently using ThreadPoolExecutor
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         returned_data = executor.submit(shared_post.extract_boom_shared_post_data_from_api, token=jwt_token, page=1, inpage=1).result()
#         my_following_list = executor.submit(my_following_to, api_url=api_search_my_following, token=jwt_token).result()   # Call my_following composition from api

    
#     followed_to = []  

#     for user in my_following_list:
#         user_concept_id = user["data"]["my_following"]["followed_to"]
#         followed_to.append(user_concept_id)

#     pagging_index = 0  # Initialize the pagination index
#     sorted_recommended_shared_post = []  # Initialize the list for results
    
#     # returned_data = extract_boom_shared_post_data_from_api(jwt_token, 1, 1 )  # Extract data from API of boom_shared_post
    
    
#     # print("Returned Data : ", returned_data)
    
#     total_shared_data = returned_data['data']['total']
#     # print("Total data ", total_shared_data)
    
#     page_counter = 1
    
#     valid_post = shared_post.populate_shared_valid_post(jwt_token, page_counter)
    
    
#     # print("Valid Post : ", valid_post)
#     friends_post = shared_post.friendsPost(user_id, valid_post, followed_to)  # Call friends post function to get post shared by friends

#     # print(friends_post)

#     # Return from manage_shared_post
#     sorted_recommended_shared_post = shared_post.manage_shared_post(valid_post, friends_post, my_concept_id)
        
#     start_index = ( page - 1 ) * inpage
#     print("Start Index : ", start_index )
#     end_index = start_index + inpage
#     print("End Index : ", end_index)
#     total_requested_index = end_index
    

#     if total_requested_index > len(sorted_recommended_shared_post):
#         iteration = int(total_shared_data/100)
#         page_counter = page_counter + 1

#         additional_valid_post = shared_post.populate_shared_valid_post(jwt_token, page_counter)  # Call function populate_shared_valid_post
        
#         # print("0"*20)
#         # print("Additional Valid Post length : ", len(additional_valid_post))
#         # print("Additional Valid Post : ", additional_valid_post)
        
#         sorted_valid_post = shared_post.manage_shared_post(additional_valid_post, friends_post, my_concept_id) # Call function manage_shared_post
        
#         # print("0"*20)
#         # print("Sorted Valid Post length : ",len(sorted_valid_post))
#         # print("Sorted Valid Post : ", sorted_valid_post)
        
#         sorted_recommended_shared_post += sorted_valid_post
#         # print("I go inside")
#         # print("Total requested index :", total_requested_index)
#         # print("Length of sorted shared post : ", len(sorted_recommended_shared_post))
        
#         if start_index < len(sorted_recommended_shared_post):
#             return sorted_recommended_shared_post[start_index:end_index]
#         else:
#             return {'Message' : 'No more boom shared data to return'}

#     else:
#         print("Total requested index :", total_requested_index)
#         print("Length of sorted shared post : ", len(sorted_recommended_shared_post))
#         return sorted_recommended_shared_post[start_index:end_index]
    



#@app.get("/get_user_suggestions", dependencies=[Depends(JWTBearer())])
# async def get_recommendations(page: int = 1, inpage: int = 10, replace_concept_id: int = None, jwt_token: str = Depends(JWTBearer())):
#     # Fetch data from api
#     try:
#         my_following_url = "https://apischema.freeschema.com/api/list-api-clean?type=my_following"
#         # my_following_url = "https://apischema.freeschema.com/api/list-api-clean?type=my_following"
#         my_following_list = graph_user_suggestions.my_following(my_following_url)
#     except:
#         return "Could not able to go through my_following api" 
    
#     users_data = graph_user_suggestions.get_all_users(jwt_token)
#     users_data = graph_user_suggestions.get_all_users(jwt_token)
#     total_users = users_data['total']

#     user_concept_id = set(int(user) for user in users_data['userConcepts'])
    
#     # own concept id
#     user_id = int(get_user_id(jwt_token))  # Get user id based on token
#     # print("User Id : ", user_id)
#     # print("User Id type : ", type(user_id))
#     concept_id = next(int(key) for key, value in users_data['userConcepts'].items() if value == user_id) # Convert userid to user_concept_id
#     print("Concept ID" ,concept_id)
#     print("Type : ", type(concept_id))
    
    
#     if concept_id not in user_concept_id:
#         raise HTTPException(status_code=404, detail="Concept ID not found")
        
#     if replace_concept_id is not None and replace_concept_id not in user_concept_id:
#         raise HTTPException(status_code=404, detail="Replace Concept ID not found")

#     G = nx.DiGraph() # Create a instance of the Directed Graph
    
#     for concept_id in user_concept_id:
#         G.add_node(concept_id)
    
#     # print("Following List : ", my_following_list)
#     for item in my_following_list:
#         try:
#             followed_to = item['data']['my_following']['followed_to']
#             followed_by = item['data']['my_following']['followed_by']
#             # Convert to integers
#             followed_to = int(followed_to)
#             followed_by = int(followed_by)

#             # Check if both followed_by and followed_to are in user_concept_id
#             if followed_by in user_concept_id and followed_to in user_concept_id:
#                 G.add_edge(followed_by, followed_to)
#             else:
#                 # Handle the case where one or both users are not in the database
#                 pass
# #                 print(f"Skipping edge ({followed_by} -> {followed_to}): One or both users not in the database")
#         except:
#             pass
            
#     # nx.draw(G, with_labels=True)
#     # plt.show()
#     # User Suggestions logic
#     recommended_users = graph_user_suggestions.recommend_users(G, concept_id, page, inpage, replace_concept_id=replace_concept_id)
#     # print(len(recommended_users))
#     # print(recommend_users)
#     return {
#         "Recommended_users Concept ID": recommended_users
#     }



# @app.get("/rank_boomext_web_comments", dependencies=[Depends(JWTBearer())])
# async def ranked_comments( page: int = 1, inpage:int =10, jwt_token: str = Depends(JWTBearer())):

#     api_with_userId = "https://apischema.freeschema.com/api/list-with-api-data-user-id?type=boomext_web_comments"
    
#     with ThreadPoolExecutor(max_workers=3) as executor:     
#         commented_data = executor.submit(rank_comments.web_url_comments, api_url = api_with_userId, token=jwt_token).result()
#         result_get_all_users = executor.submit(get_all_users, token=jwt_token).result()
#         result_get_user_id = executor.submit(get_user_id, token=jwt_token).result()
        
#     with ThreadPoolExecutor(max_workers=2) as executor:        
#         user_id = int(result_get_user_id)
#         # Convert userid to user_concept_id
#         my_concept_id = next(int(key) for key, value in result_get_all_users['userConcepts'].items() if value == user_id) 


#     # my_following_search_api = "https://apischema.freeschema.com/api/search-api-clean?composition=my_following&type=followed_to"
#     my_following_search_api = f"https://apischema.freeschema.com/api/searchConcept?composition=my_following&search={my_concept_id}&type=followed_by&page=1&inpage=1000"
#     my_following_list = my_following_to(my_following_search_api, jwt_token)  # Call my_following composition from api
    
#     followed_to_user_id_list = []  

#     for user in my_following_list:
#         user_concept_id = user["data"]["my_following"]["followed_to"]
#         # Convert user_concept_id to user_id
#         converted_user_id = next(int(value) for key, value in result_get_all_users['userConcepts'].items() if key == user_concept_id) 
#         followed_to_user_id_list.append(converted_user_id)

#     # print("Followed To User ID : ", followed_to_user_id_list)
#     G = rank_comments.create_graph(user_id, followed_to_user_id_list, commented_data)
#     # followed_to_user_cid = []  

#     # for user in my_following_list:
#     #     user_concept_id = user["data"]["my_following"]["followed_to"]
#     #     followed_to_user_cid.append(user_concept_id)

#     #     # followed_to_user_id_list = followed_to(my_following_search_api, jwt_token)   # return followed user list
    
#     # G = rank_comments.create_graph(user_id, followed_to_user_cid, commented_data)
    
    
#     # Load functions concurrently using ThreadPoolExecutor
#     with ThreadPoolExecutor(max_workers=3) as executor:
#         rank1 = executor.submit(rank_comments.friends_comment, G=G, commented_data=commented_data, user_id=user_id).result()
#         rank2 = executor.submit(rank_comments.same_url_comment, commented_data=commented_data, user_id=user_id).result()
#         rank3 = executor.submit(rank_comments.sorted_comment, commented_data=commented_data).result()
    
#     # Create an empty set to track added comments
#     added_comments = set()

#     # Create a list to store the combined ranked comments
#     combined_ranked_web_comments = []

#     # Append Rank1, Rank2, and Rank3 comments if not already added
#     for rank in (rank1, rank2, rank3):
#         for comment in rank:
#             comment_id = comment['boomext_web_comments']['id']
#             if comment_id not in added_comments:
#                 combined_ranked_web_comments.append(comment)
#                 added_comments.add(comment_id)

#     # Filter out comments made by the user
#     combined_ranked_web_comments_without_you = [
#         comment for comment in combined_ranked_web_comments
#         if comment['boomext_web_comments']['user_id'] != user_id
#     ]
        
#     start_index = (page - 1) * inpage
#     end_index = start_index + inpage
    
#     combined_ranked_web_comments_with_paging = combined_ranked_web_comments_without_you[start_index:end_index]
    
#     # print("with paging : ", combined_ranked_web_comments_with_paging)

#     return combined_ranked_web_comments_with_paging


