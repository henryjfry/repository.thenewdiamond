import requests, json, time

imdb_profile_id = "p.n1bcdefghijklmnopqrstuvwxy"

def get_imdb_user_lists_full(identifier):
	api_url = "https://graphql.prod.api.imdb.a2z.com/"
	headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "x-imdb-client-name": "imdb-web-next", "Origin": "https://www.imdb.com"}
	try:
		ur_id = identifier
		if identifier.startswith("p."):
			q_res = """query Resolve($p: ID) { userProfile(input: { profileId: $p }) { userId } }"""
			r1 = requests.post(api_url, headers=headers, data=json.dumps({"query": q_res, "variables": {"p": identifier}}, separators=(',', ':')))
			ur_id = r1.json().get("data", {}).get("userProfile", {}).get("userId")
		if not ur_id: return "Error: Failed to resolve User ID"
		q_main = """query ListsPage($u: ID!) { userListSearch(filter: { anyClassTypes: [LIST] }, first: 250, listOwnerUserId: $u) { edges { node { id name { originalText } items(first: 0) { total } } } } }"""
		payload = {"operationName": "ListsPage", "query": q_main, "variables": {"u": ur_id}}
		r2 = requests.post(api_url, headers=headers, json=payload)
		data = r2.json()
		if "errors" in data: return f"GraphQL Error: {data['errors']}"
		edges = data.get("data", {}).get("userListSearch", {}).get("edges", [])
		return {"ur_id": ur_id, "custom_lists": [{"ls_id": e["node"]["id"], "name": e["node"]["name"]["originalText"], "count": e["node"]["items"]["total"]} for e in edges]}
	except Exception as e: return f"Failed: {str(e)}"

imdb_user_lists = json.dumps(get_imdb_user_lists_full(imdb_profile_id), indent=2)


#import requests, json
def get_urconst_from_profile_id(profile_id):
	url = "https://api.graphql.imdb.com/"
	headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "x-imdb-client-name": "imdb-web-next"}
	query = """query RatingInsightsInterestTopRatedWithProfileId($profileId: ID) { userProfile(input: { profileId: $profileId }) { userId } }"""
	variables = {"profileId": profile_id}
	try:
		response = requests.post(url, headers=headers, data=json.dumps({"query": query, "variables": variables}, separators=(',', ':')))
		print(f"DEBUG RESPONSE: {response.text}")
		if response.status_code != 200: return f"Error: {response.status_code}"
		ur_const = response.json().get("data", {}).get("userProfile", {}).get("userId")
		return ur_const if ur_const else "UR ID not found"
	except Exception as e: return f"Failed: {str(e)}"

ur_id = get_urconst_from_profile_id("p.n1bcdefghijklmnopqrstuvwxy")

#import requests, json
def get_watchlist_lsid_from_ur(ur_id):
	url = "https://api.graphql.imdb.com/"
	headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "x-imdb-client-name": "imdb-web-next"}
	# Corrected to WATCH_LIST and userId based on standard IMDb GraphQL field names
	query = """query WatchlistDiscovery($ur_id: ID!) { predefinedList(classType: WATCH_LIST, userId: $ur_id) { id items(first: 0) { total } } }"""
	variables = {"ur_id": ur_id}
	try:
		response = requests.post(url, headers=headers, data=json.dumps({"query": query, "variables": variables}))
		print(f"DEBUG RESPONSE: {response.text}")
		if response.status_code != 200: return f"Error: {response.status_code}"
		data = response.json()
		ls_id = data.get("data", {}).get("predefinedList", {}).get("id")
		total = data.get("data", {}).get("predefinedList", {}).get("items",{}).get("total")
		ls_dict = {'ls_id': ls_id, 'name': 'watchlist', 'count': total}
		return ls_id,ls_dict if ls_id else "Watchlist not found (check if profile is public)"
	except Exception as e: return f"Failed: {str(e)}"

#import requests, json
def get_watchlist_lsid_from_ur(profile_id):
	url = "https://api.graphql.imdb.com/"
	headers = {
		"Content-Type": "application/json", 
		"User-Agent": "Mozilla/5.0", 
		"x-imdb-client-name": "imdb-web-next"
	}
	# Step 1: Resolve the ur_id and nickName using the profileId
	id_query = """query ResolveProfile($profile_id: ID!) { userProfile(input: { profileId: $profile_id }) { userId nickName } }"""
	try:
		id_resp = requests.post(url, headers=headers, data=json.dumps({"query": id_query, "variables": {"profile_id": profile_id}}))
		print(f"DEBUG ID RESPONSE: {id_resp.text}")
		if id_resp.status_code != 200: return None, f"Error: {id_resp.status_code}"
		id_data = id_resp.json().get("data", {}).get("userProfile")
		if not id_data: return None, "Profile not found or invalid profileId"
		ur_id = id_data.get("userId")
		nickname = id_data.get("nickName")
		# Step 2: Use the ur_id to fetch the watchlist
		wl_query = """query WatchlistDiscovery($ur_id: ID!) { predefinedList(classType: WATCH_LIST, userId: $ur_id) { id items(first: 0) { total } } }"""
		wl_resp = requests.post(url, headers=headers, data=json.dumps({"query": wl_query, "variables": {"ur_id": ur_id}}))
		print(f"DEBUG WL RESPONSE: {wl_resp.text}")
		if wl_resp.status_code != 200: return None, f"WL Error: {wl_resp.status_code}"
		wl_data = wl_resp.json().get("data", {}).get("predefinedList")
		if not wl_data: return None, "Watchlist not found (check if profile is public)"
		ls_id = wl_data.get("id")
		ls_dict = {
			'nickname': nickname,
			'ur_id': ur_id,
			'ls_id': ls_id, 
			'name': 'watchlist', 
			'count': wl_data.get("items", {}).get("total")
		}
		return ls_id, ls_dict
	except Exception as e: return None, f"Failed: {str(e)}"

ls_id,ls_dict = get_watchlist_lsid_from_ur(ur_id)
imdb_user_lists_dict = eval(imdb_user_lists)
imdb_user_lists_dict['custom_lists'].append(ls_dict)
print(imdb_user_lists_dict)


import requests, json
def get_user_lists_via_search(ur_id):
	url = "https://api.graphql.imdb.com/"
	headers = {
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0",
		"x-imdb-client-name": "imdb-web-next"
	}
	# This query finds all lists owned by a specific userId
	query = """
	query UserLists($ur_id: ID!) { userListSearch(first: 10, listOwnerUserId: $ur_id) { edges { node { id name { originalText }  items(first: 0) { total }  author {  nickName  userId } } } total } }"""
	variables = {"ur_id": ur_id}
	try:
		response = requests.post(url, headers=headers, data=json.dumps({"query": query, "variables": variables}))
		print(f"DEBUG RESPONSE: {response.text}")
		if response.status_code != 200: return None, f"Error: {response.status_code}"
		data = response.json().get("data", {}).get("userListSearch", {})
		edges = data.get("edges", [])
		if not edges: return None, "No public lists found for this user"
		# Extracting nickname and lists
		first_list = edges[0].get("node", {})
		nickname = first_list.get("author", {}).get("nickName")
		results = []
		for edge in edges:
			node = edge.get("node", {})
			results.append({
				"ls_id": node.get("id"),
				"name": node.get("name", {}).get("originalText"),
				"count": node.get("items", {}).get("total")
			})
		# ... (rest of the function above remains the same)
		nickname = first_list.get("author", {}).get("nickName", "User")
		imdb_list = {"imdb_list": []}
		# Mapping results to the specific {id: "IMDB - Name - Count"} format
		for edge in edges:
			node = edge.get("node", {})
			list_id = node.get("id")
			list_name = node.get("name", {}).get("originalText", "Unnamed List")
			if list_name.lower() == 'watchlist':
				list_name = str(nickname) + ' ' + 'Watchlist'
			list_count = node.get("items", {}).get("total", 0)
			
			imdb_list["imdb_list"].append({
				list_id: f"IMDB - {list_name} - {list_count}"
			})
		return nickname, imdb_list
	except Exception as e: return None, f"Failed: {str(e)}"

nickname, imdb_list = get_user_lists_via_search(ur_id)