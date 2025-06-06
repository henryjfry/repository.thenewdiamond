import xbmcgui

from resources.lib.modules.globals import g
import pytz


def validate_timezone_detected():
	if g.LOCAL_TIMEZONE and isinstance(g.LOCAL_TIMEZONE, pytz.BaseTzInfo) and g.LOCAL_TIMEZONE.zone != 'UTC':
		return
	g.set_setting("general.manualtimezone", True)
	notify_timezone_not_detected()


def notify_timezone_not_detected():
	if confirm := xbmcgui.Dialog().yesno(g.get_language_string(30549), g.get_language_string(30550)):
		choose_timezone()


def choose_timezone():
	current = g.get_setting("general.localtimezone")
	time_zones = [i for i in pytz.common_timezones if len(i.split('/')) >= 2 and i.split('/')[0] != 'US']

	# Note we deliberately don't include the US timezones as they have too many assumptions for historic dates
	try:
		preselect = time_zones.index(current)
	except ValueError:
		preselect = -1
	tz_index = xbmcgui.Dialog().select(g.get_language_string(30548), time_zones, preselect=preselect)
	if tz_index != -1:
		g.set_setting("general.localtimezone", time_zones[tz_index])
