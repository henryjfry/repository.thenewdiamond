def get_imdb_user_list_id(user_profile_id, return_dict=False):
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
	def get_watchlist_lsid_from_ur(ur_id):
		url = "https://api.graphql.imdb.com/"
		headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "x-imdb-client-name": "imdb-web-next"}
		# Corrected to WATCH_LIST and userId based on standard IMDb GraphQL field names
		query = """query WatchlistDiscovery($ur_id: ID!) { predefinedList(classType: WATCH_LIST, userId: $ur_id) { id items(first: 0) { total } } }"""
		variables = {"ur_id": ur_id}
		try:
			response = requests.post(url, headers=headers, data=json.dumps({"query": query, "variables": variables}))
			#print(f"DEBUG RESPONSE: {response.text}")
			if response.status_code != 200: return f"Error: {response.status_code}"
			data = response.json()
			ls_id = data.get("data", {}).get("predefinedList", {}).get("id")
			total = data.get("data", {}).get("predefinedList", {}).get("items",{}).get("total")
			ls_dict = {'ls_id': ls_id, 'name': 'watchlist', 'count': total}
			return ls_id,ls_dict if ls_id else "Watchlist not found (check if profile is public)"
		except Exception as e: return f"Failed: {str(e)}"
	ur_id = user_profile_id
	if ur_id[:2].lower() == 'ur':
		ls_id,ls_dict =get_watchlist_lsid_from_ur(ur_id)
	else:
		ur_id = get_urconst_from_profile_id(user_profile_id)
		ls_id,ls_dict =get_watchlist_lsid_from_ur(ur_id)
	if return_dict == False:
		return ls_id
	else:
		watchlist_dict = {}
		watchlist_dict['watchlist_id'] = ls_id
		watchlist_dict['ur_list_str'] = ur_id
		watchlist_dict['total'] = ls_dict['count']
		watchlist_dict['name'] = f"IMDB - {ur_id} Watchlist - " + str(ls_dict['count'])
		return watchlist_dict


#imdb_profile_id = "p.n1bcdefghijklmnopqrstuvwxy"
#ur_id = get_urconst_from_profile_id(imdb_profile_id)
#nickname, imdb_list = get_user_lists_via_search(ur_id)
ls_id = get_imdb_user_list_id("p.n1bcdefghijklmnopqrstuvwxy",return_dict=False)
print(ls_id)
ls_id = get_imdb_user_list_id('ur0123456',return_dict=False)
print(ls_id)
ls_id = get_imdb_user_list_id("p.n1bcdefghijklmnopqrstuvwxy",return_dict=True)
print(ls_id)
ls_id = get_imdb_user_list_id('ur0123456',return_dict=True)
print(ls_id)