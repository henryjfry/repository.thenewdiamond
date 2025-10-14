
import xbmc
import xbmcgui
import json

def search_and_switch_channel(search_text):
	# Prepare JSON-RPC request to get all TV channels with current broadcast
	request = {
		"jsonrpc": "2.0",
		"id": 1,
		"method": "PVR.GetChannels",
		"params": {
			"channelgroupid": "alltv",
			"properties": [
				"channelnumber",
				"broadcastnow"
			]
		}
	}

	# Send request to Kodi
	response = xbmc.executeJSONRPC(json.dumps(request))
	data = json.loads(response)

	# Extract matching channels
	matches = []
	channels = data.get("result", {}).get("channels", [])
	for channel in channels:
		broadcast = channel.get("broadcastnow")
		label = channel.get("label")
		if broadcast and (search_text.lower() in label.lower() or search_text.lower() in broadcast.get("title", "").lower()):
			matches.append({
				"id": channel["channelid"],
				"name": f'{channel["label"]} - {broadcast["title"]}'
			})
		elif not broadcast and search_text.lower() in label.lower():
			matches.append({
				"id": channel["channelid"],
				"name": f'{channel["label"]}'
			})

	# If no matches found
	if not matches:
		xbmcgui.Dialog().ok("No Matches", f"No channels found with '{search_text}' in the current programme.")
		return

	# Show selection dialog
	options = [match["name"] for match in matches]
	selected = xbmcgui.Dialog().select("Select a Channel", options)

	if selected >= 0:
		channel_id = matches[selected]["id"]

		# Switch to selected channel
		switch_request = {
			"jsonrpc": "2.0",
			"id": 1,
			"method": "Player.Open",
			"params": {
				"item": {
					"channelid": channel_id
				}
			}
		}
		xbmc.executebuiltin('Dialog.Close(all,true)')
		xbmc.executeJSONRPC(json.dumps(switch_request))
	else:
		xbmcgui.Dialog().ok("Cancelled", "No channel selected.")
