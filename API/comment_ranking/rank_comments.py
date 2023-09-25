import pandas as pd
import sqlalchemy
import networkx as nx
import requests
from datetime import datetime
from os import environ as env


# conn_engine = sqlalchemy.create_engine(env["DATABASE_URL"])


def web_url_comments(api_url, token):
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
        return e


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
        # print(f"Error : {e}")
        return e

# def conceptId_to_userId(concept_id):
#     userId_df = pd.read_sql_query(f"SELECT id FROM the_users WHERE concept_id={concept_id}", conn_engine)
#     converted_user_id = userId_df['id'].item()
#     return converted_user_id
    

# def followed_to(my_following_search_api, jwt_token):
#     followed_to_concept_id_list = []
#     followed_to_user_id_list = []

#     following_data  = my_following(my_following_search_api, jwt_token) # Call my_following function

#     # print(following_data)

#     for follow in following_data:
#         if isinstance(follow, dict):   
#             followed_to_cid = follow['my_following']['followed_to']
#             followed_to_concept_id_list.append(followed_to_cid)

#             # Convert concept_id to user_id
#             user_id = conceptId_to_userId(followed_to_cid)
#             followed_to_user_id_list.append(user_id)
#         else:
#             pass
#     return followed_to_user_id_list

# print(followed_to_concept_id_list)
# followed_to_user_id_list = followed_to()
# print(followed_to_user_id_list)

def create_graph(user_id, followed_to_user_id_list, commented_data):
    G = nx.DiGraph()
    
    # Add nodes for the user and followed users
    G.add_node(user_id, color='red')
    
    for followed_to_user in followed_to_user_id_list:
        G.add_edge(user_id, followed_to_user, value='followed_to')
        G.add_node(followed_to_user, color='blue')
        
        # Add edge if the friend's id have comment associated with it
        for data in commented_data:
            if data['boomext_web_comments']['user_id'] == followed_to_user:
                comment_id = data['boomext_web_comments']['id']
                G.add_edge(followed_to_user, comment_id, value="comment_id")
                G.add_node(comment_id, color='green')
    
    return G

# def draw_graph(G):
#     pos = nx.spring_layout(G)
#     node_colors = [G.nodes[node]['color'] for node in G.nodes]
#     nx.draw(G, pos, with_labels=True, node_color=node_colors, font_color='white', node_size=1000, font_size=10)
    
#     # Add edge labels
#     edge_labels = {(source, target): G.edges[source, target]['value'] for source, target in G.edges}
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
#     # Show the plot
#     plt.show()
      

# draw_graph(G)


def friends_comment(G, commented_data, user_id):
    show_ranked_comment_without_date_sorted = []

    # Extract nodes directed with the label 'comment_id'
    comment_id_nodes = []
    for source, target, value in G.edges(data='value'):
        if value == "comment_id":
            comment_id_nodes.append(target)

    # print("Nodes directed with 'comment_id' label:", comment_id_nodes)
    
    for comment_id in comment_id_nodes:
        for boomext_web_comments in commented_data:
            # Extract commented da
            created_on = boomext_web_comments['boomext_web_comments']['data']['created_on']
            if comment_id == boomext_web_comments['boomext_web_comments']['id']:
                # Insert comment in unsorted order by date
                show_ranked_comment_without_date_sorted.append(boomext_web_comments)
                
    # Sort the data based on the 'commented_date' key in show_ranked_comment_without_date_sorted list
    sorted_ranked1_comment = sorted(show_ranked_comment_without_date_sorted, key=lambda x: x['boomext_web_comments']['data']['created_on'], reverse=True)    
            
    return sorted_ranked1_comment
        

# length = len(friends_comment(G))
# print(length)


def same_url_comment(commented_data, user_id):
    # Loop through boomext_web_comments composition
    count = 0
    my_comments = []
    for boomext_web_comments in commented_data:
        user = boomext_web_comments['boomext_web_comments']['user_id']

        if int(user_id) == int(user):
            my_comments.append(boomext_web_comments)

    
    # print(my_comments)
    sorted_my_comments = sorted(my_comments, key=lambda x:x['boomext_web_comments']['data']['created_on'], reverse=True)
    # print("sorted my comments", len(sorted_my_comments))
    unique_url = []
    same_url_comment = []
    # Extract only one comment latest comment from unique url that given user is following
    for i in sorted_my_comments:
        web_url = i['boomext_web_comments']['data']['web_url']
        # print(web_url)
        if web_url not in unique_url:
            same_url_comment.append(i)
            
    
    return same_url_comment


# print(len(same_url_comment()))  
# print(same_url_comment())


def sorted_comment(commented_data):
    sorted_web_comments = []
    sorted_comments = sorted(commented_data, key=lambda x:x['boomext_web_comments']['data']['created_on'], reverse=True)
    sorted_web_comments.append(sorted_comments)
    # Convert double list to single list
    flattened_list = [item for sublist in sorted_web_comments for item in sublist]
    return flattened_list

# sorted_comment()
# l = len(sorted_comment())
# print(l)
