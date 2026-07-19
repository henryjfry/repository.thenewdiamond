"""
	Fenomscrapers Module
"""

from gearsscrapers.modules.control import addonPath, addonVersion, joinPath
from gearsscrapers.modules.textviewer import TextViewerXML


def get():
	gearsscrapers_path = addonPath()
	gearsscrapers_version = addonVersion()
	changelogfile = joinPath(gearsscrapers_path, 'changelog.txt')
	r = open(changelogfile, 'r', encoding='utf-8', errors='ignore')
	text = r.read()
	r.close()
	heading = '[B]gearsscrapers -  v%s - ChangeLog[/B]' % gearsscrapers_version
	windows = TextViewerXML('textviewer.xml', gearsscrapers_path, heading=heading, text=text)
	windows.run()
	del windows
