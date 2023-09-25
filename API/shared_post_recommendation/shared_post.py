import requests
import networkx as nx

# Call API to fetch all shared post data 
def extract_boom_shared_post_data_from_api(token, page:int, inpage:int):
    try:
        header = {
            "Authorization": f"Bearer  {token}"
        }
        # api_url = "https://apischema.freeschema.com/api/list-with-api-data-user-id"
        api_url = "https://apischema.freeschema.com/api/concepts/list-with-total"
                
        paramaters = {
            "type": "boom_shared_post",
            "page": page,
            "inpage": inpage
        }
        response = requests.get(api_url, headers=header, params=paramaters)
        response.raise_for_status()
        response_json = response.json()
                
        return response_json
    
    except requests.exceptions.RequestException as e:
        print(f"Error : {e}")
        return e

# Plot friends posts in graph 
def friendsPost(user_id, data_list, followed_to):
    G = nx.DiGraph()
    G.add_node(user_id, color='red', layer=1)  # Assign layer attribute

    shared_edges = []  # Initialize a list to store shared edges

    for friend in followed_to:
        G.add_edge(user_id, friend, label='Followed To')
        G.add_node(friend, color='blue', layer=2)  # Assign layer attribute
        for boom_shared_post in data_list:
            post_id = boom_shared_post['id']
            try:
                sharedby = boom_shared_post['data']['boom_shared_post']['sharedby']['userid']

                if friend == sharedby:
                    G.add_edge(friend, post_id, label='Shared')
                    G.add_node(post_id, color='green', layer=3)  # Assign layer attribute
                    shared_edges.append(post_id)  # Store shared edges
            except:
                continue
    # Draw the graph
    # pos = nx.spring_layout(G, seed=42)
    # colors = [node[1]['color'] for node in G.nodes(data=True)]
    # layers = [node[1]['layer'] for node in G.nodes(data=True)]
    # nx.draw(G, pos, with_labels=True, node_color=colors, font_color='blue', font_weight='bold', node_size=100)
    
    # Add edge labels manually using 'label' attribute
    # edge_labels = {(user_id, friend): edge_data['label'] for user_id, friend, edge_data in G.edges(data=True)}
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black')
    
    # plt.title(f"Friends' Posts and Connections for User {user_id}")
    # plt.figure(figsize=(80, 20))
    
    # plt.show()

    return shared_edges



# Append only valid post with proper userid and other information
def populate_shared_valid_post(token, page_counter):
    valid_post = []
    check_post_id = set()
    # Limit 100 shared post in inpage and add counter to page parameter
    filtered_shared_post = extract_boom_shared_post_data_from_api(token, page_counter, 100)
    returned_datas_data = filtered_shared_post['data']['data']    

    for post in returned_datas_data:
        if isinstance(post['data']['boom_shared_post'], dict):
            try:
                boom_shared_post = post['data']['boom_shared_post']
                shared_post_id = post['id']
                sharedby = boom_shared_post.get("sharedby", {})
                if sharedby:  # Check sharedby is not null
                    # shared_date = int(boom_shared_post["shared_on"])
                    # userConceptId = sharedby['userid']
                    if shared_post_id not in check_post_id:
                        valid_post.append(post)
                        check_post_id.add(shared_post_id)
            except:
                pass

    return valid_post

# To rank friends post first and others post after than
def manage_shared_post(valid_post, friends_post, user_cid):
    recommended_friends_post_series = []
    unknown_users_post_series = []
    
    for shared_post in valid_post:
        shared_post_id = shared_post['id']
        try:
            shared_post_userID = shared_post['data']['boom_shared_post']['sharedby']['userid'] 
            # Check if the post is shared by a friends
            if shared_post_id in friends_post:
                recommended_friends_post_series.append(shared_post)
            # Check if the post is shared by ownself
            elif int(shared_post_userID) == int(user_cid):
                pass
            # Post shared by unknown users
            else:
                unknown_users_post_series.append(shared_post)
        except:
            continue

    # Sort friends post by reverse date
    sorted_recommended_friends_post = sorted(recommended_friends_post_series, key=lambda x:x['data']['boom_shared_post']['shared_on'], reverse=True)
    sorted_unknown_post = sorted(unknown_users_post_series, key=lambda x:x['data']['boom_shared_post']['shared_on'], reverse=True)
    
    sorted_recommended_shared_post = sorted_recommended_friends_post + sorted_unknown_post
    
    return sorted_recommended_shared_post
