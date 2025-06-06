#!/usr/bin/python3
import sys
osmc_home = sys.argv[1]

#osmc_home = '/usr/share/kodi/addons/skin.estuary/xml/Home.xml'
home_xml = osmc_home 
file1 = open(home_xml, 'r')
Lines = file1.readlines()
out_xml = ''
item_flag = False
new_item = '''

						<item>
							<label>$LOCALIZE[10134]</label>
							<onclick>ActivateWindow(favourites)</onclick>
							<property name="menu_id">$NUMBER[14000]</property>
							<thumb>icons/sidemenu/favourites.png</thumb>
							<property name="id">favorites</property>
							<visible>!Skin.HasSetting(HomeMenuNoFavButton)</visible>
						</item>

'''
item_count = 0
change_flag = False
for line in Lines:
	if item_flag == False and not '<item>' in line:
		out_xml = out_xml + line 
	if '<item>' in line:
		item_flag = True
		string = line
		item_count = item_count + 1
		continue
	if item_flag == True:
		string  = string + line
	if '</item>' in line:
		item_flag = False
		curr_item = string.split('<property name="id">')[1].split('</property>')[0]
		print(item_count, curr_item )
		if curr_item == 'movies' and item_count == 1:
			string = new_item + string 
			change_flag = True
		if curr_item == 'favorites' and item_count == 1:
			change_flag = False
		if curr_item == 'favorites' and item_count > 2:
			continue
			change_flag = True
		out_xml = out_xml + string

if change_flag == True:
	file1 = open(home_xml, 'w')
	file1.writelines(out_xml)
	file1.close()
	print(out_xml)


#osmc_home = '/usr/share/kodi/addons/skin.estuary/xml/VideoOSD.xml'
osmc_home = osmc_home.replace('Home.xml','VideoOSD.xml')
home_xml = osmc_home 
file1 = open(home_xml, 'r')
Lines = file1.readlines()
out_xml = ''
item_flag = False
old_item = '''<defaultcontrol always="true">602</defaultcontrol>'''
new_item = '''
	<defaultcontrol always="true">70048</defaultcontrol>
'''

item_count = 0
change_flag = False
for line in Lines:
	if item_flag == False and old_item in str(line):
		out_xml = out_xml + new_item 
		item_flag = True
		change_flag = True
	else:
		out_xml = out_xml + line


if change_flag == True:
	file1 = open(home_xml, 'w')
	file1.writelines(out_xml)
	file1.close()
	print(out_xml)

line_593_594 = """				<onup>noop</onup>
			<ondown>105</ondown>"""
line_593 = """<onup>noop</onup>"""
line_594 = """<ondown>105</ondown>"""
line_3 = """<defaultcontrol always="true">300</defaultcontrol>"""

line_593_594_new = """				<onup>300</onup>
				<ondown>300</ondown>
"""
line_3_new = """	<defaultcontrol always="true">105</defaultcontrol>
"""

osmc_home = osmc_home.replace('VideoOSD.xml','DialogKeyboard.xml')
home_xml = osmc_home 
file1 = open(home_xml, 'r')
Lines = file1.readlines()
out_xml = ''
item_flag = False
item_count = 0
change_flag = False
for line in Lines:
	if line_3 in str(line):
		out_xml = out_xml + line_3_new 
		item_flag = True
		change_flag = True
	if line_593 in str(line):
		out_xml = out_xml + line_593_594_new 
		item_flag = True
		change_flag = True
	elif line_594 in str(line):
		continue
	else:
		out_xml = out_xml + line


if change_flag == True:
	file1 = open(home_xml, 'w')
	file1.writelines(out_xml)
	file1.close()
	print(out_xml)