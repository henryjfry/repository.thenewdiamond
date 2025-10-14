import xbmc

title = xbmc.getInfoLabel('ListItem.Title')
if title:
    xbmc.executebuiltin(
        f'RunScript(script.xtreme_vod,info=search_title,search_text={title})'
    )
