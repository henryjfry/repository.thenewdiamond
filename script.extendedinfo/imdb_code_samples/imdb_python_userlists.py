

def get_imdb_user_lists(user_profile_id):
	import requests, json, re
	def get_urconst_from_profile_id(profile_id):
		url = "https://api.graphql.imdb.com/"
		headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "x-imdb-client-name": "imdb-web-next"}
		query = """query RatingInsightsInterestTopRatedWithProfileId($profileId: ID) { userProfile(input: { profileId: $profileId }) { userId } }"""
		variables = {"profileId": profile_id}
		try:
			response = requests.post(url, headers=headers, data=json.dumps({"query": query, "variables": variables}, separators=(',', ':')))
			#print(f"DEBUG RESPONSE: {response.text}")
			if response.status_code != 200: return f"Error: {response.status_code}"
			ur_const = response.json().get("data", {}).get("userProfile", {}).get("userId")
			return ur_const if ur_const else "UR ID not found"
		except Exception as e: return f"Failed: {str(e)}"
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
			#print(f"DEBUG RESPONSE: {response.text}")
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
	ur_id = user_profile_id
	if ur_id[:2].lower() == 'ur':
		nickname, imdb_list = get_user_lists_via_search(ur_id)
	else:
		ur_id = get_urconst_from_profile_id(user_profile_id)
		nickname, imdb_list = get_user_lists_via_search(ur_id)
	return imdb_list


#imdb_profile_id = "p.n1bcdefghijklmnopqrstuvwxy"
#ur_id = get_urconst_from_profile_id(imdb_profile_id)
#nickname, imdb_list = get_user_lists_via_search(ur_id)
get_imdb_user_lists("p.n1bcdefghijklmnopqrstuvwxy")
get_imdb_user_lists('ur0123456')