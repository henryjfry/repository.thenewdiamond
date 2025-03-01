# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import datetime
import xbmc
import xbmcgui

from resources.lib.WindowManager import wm
from resources.lib import YouTube
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.DialogBaseList import DialogBaseList
from resources.lib import Utils
from resources.lib.VideoPlayer import PLAYER

ch = OnClickHandler()

ID_BUTTON_SORTTYPE = 5001
ID_BUTTON_PUBLISHEDFILTER = 5002
ID_BUTTON_LANGUAGEFILTER = 5003
ID_BUTTON_DIMENSIONFILTER = 5006
ID_BUTTON_DURATIONFILTER = 5008
ID_BUTTON_CAPTIONFILTER = 5009
ID_BUTTON_DEFINITIONFILTER = 5012
ID_BUTTON_TYPEFILTER = 5013

import xbmcaddon
addon = xbmcaddon.Addon()

def get_youtube_window(window_type):

    class DialogYoutubeList(DialogBaseList, window_type):

        TYPES = ["video", "playlist", "channel"]

        FILTERS = {"channelId": xbmc.getLocalizedString(19029),
                   "publishedAfter": xbmc.getLocalizedString(172),
                   "regionCode": xbmc.getLocalizedString(248),
                   "videoDimension": addon.getLocalizedString(32057),
                   "videoDuration": xbmc.getLocalizedString(180),
                   "videoCaption": xbmc.getLocalizedString(287),
                   "videoDefinition": 'Resolution',
                   "videoType": "Type",
                   "relatedToVideoId": addon.getLocalizedString(32058)}

        TRANSLATIONS = {"video": xbmc.getLocalizedString(157),
                        "playlist": xbmc.getLocalizedString(559),
                        "channel": xbmc.getLocalizedString(19029)}

        SORTS = {"video": {"date": xbmc.getLocalizedString(552),
                           "rating": xbmc.getLocalizedString(563),
                           "relevance": addon.getLocalizedString(32060),
                           "title": xbmc.getLocalizedString(369),
                           "viewCount": xbmc.getLocalizedString(567)},
                 "playlist": {"date": xbmc.getLocalizedString(552),
                              "rating": xbmc.getLocalizedString(563),
                              "relevance": addon.getLocalizedString(32060),
                              "title": xbmc.getLocalizedString(369),
                              "videoCount": addon.getLocalizedString(32068),
                              "viewCount": xbmc.getLocalizedString(567)},
                 "channel": {"date": xbmc.getLocalizedString(552),
                             "rating": xbmc.getLocalizedString(563),
                             "relevance": addon.getLocalizedString(32060),
                             "title": xbmc.getLocalizedString(369),
                             "videoCount": addon.getLocalizedString(32068),
                             "viewCount": xbmc.getLocalizedString(567)}}

        LABEL2 = {"date": lambda x: x.get_info("date"),
                  "relevance": lambda x: x.get_property("relevance"),
                  "title": lambda x: x.get_info("title"),
                  "viewCount": lambda x: x.get_property("viewCount"),
                  "videoCount": lambda x: x.get_property("videoCount"),
                  "rating": lambda x: x.get_info("rating")}

        def __init__(self, *args, **kwargs):
            super(DialogYoutubeList, self).__init__(*args, **kwargs)
            Utils.show_busy()
            self.data = []
            self.type = kwargs.get('type', "video")
            #self.FocusedItem = None
            self.search_str = kwargs.get('search_str')
            self.yt_listitems = None
            #self.listitems = self.get_youtube_vids(self.search_str)
            #xbmc.log(str(self.total_pages)+'===>OPENINFO', level=xbmc.LOGINFO)
            #xbmc.log(str(self.total_items)+'===>OPENINFO', level=xbmc.LOGINFO)
            self.sort = None
            self.sort_label = None
            self.order = 'asc'
            self.page = 1
            #self.total_items = None
            #self.total_pages = None
            self.curr_window = None
            self.prev_window = None
            self.filter_url = None
            self.filter = None
            #self.setProperty('TotalPages', str(self.total_pages))
            #self.setProperty('TotalItems', str(self.total_items))
            #self.window_id = xbmcgui.getCurrentWindowDialogId()
            #self.window = xbmcgui.Window(self.window_id)
            #xbmc.log(str(self.window_id)+'===>OPENINFO', level=xbmc.LOGINFO)
            self.update_content(force_update=kwargs.get('force', False))

        def onClick(self, control_id):
            super(DialogYoutubeList, self).onClick(control_id)
            ch.serve(control_id, self)

        def onAction(self, action):
            super(DialogYoutubeList, self).onAction(action)
            ch.serve_action(action, self.getFocusId(), self)

        @ch.click(500)
        def main_list_click(self):
            #xbmc.log(str(self.listitem.getProperty('id'))+'===>OPENINFO', level=xbmc.LOGINFO)
            #listitem = self.FocusedItem(control_id)
            youtube_id = self.listitem.getProperty("youtube_id")
            media_type = self.listitem.getProperty("type")
            if media_type == "channel":
                filter_ = [{"id": youtube_id,
                            "type": "channelId",
                            "label": self.listitem.getLabel().decode("utf-8")}]
                wm.open_youtube_list(filters=filter_)
            else:
                PLAYER.playtube(self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

        @ch.click(5007)
        def main_type_buton(self):
            listitems = []
            listitems += ['All Movies']
            listitems += ['All TV']
            listitems += ['Reopen Last Video List']
            listitems += ['Youtube']
            selection = xbmcgui.Dialog().select(heading='Choose List Type', list=listitems)
            if listitems[selection] == 'All Movies':
                self.close()
                return wm.open_video_list(media_type='movie',mode='filter')
            elif listitems[selection] == 'All TV':
                self.close()
                return wm.open_video_list(media_type='tv',mode='filter')
            elif listitems[selection] == 'Reopen Last Video List':
                self.close()
                return wm.open_video_list(search_str='', mode='reopen_window')
            elif listitems[selection] == 'Youtube':
                self.close()
                return wm.open_youtube_list(search_str='')

        @ch.click(ID_BUTTON_PUBLISHEDFILTER)
        def set_published_filter(self):
            options = [(1, addon.getLocalizedString(32062)),
                       (7, addon.getLocalizedString(32063)),
                       (31, addon.getLocalizedString(32064)),
                       (365, addon.getLocalizedString(32065)),
                       ("custom", xbmc.getLocalizedString(636))]
            deltas = [i[0] for i in options]
            labels = [i[1] for i in options]
            index = xbmcgui.Dialog().select(heading=addon.getLocalizedString(32151),
                                            list=labels)
            if index == -1:
                return None
            delta = deltas[index]
            if delta == "custom":
                delta = xbmcgui.Dialog().input(heading=addon.getLocalizedString(32067),
                                               type=xbmcgui.INPUT_NUMERIC)
            if not delta:
                return None
            d = datetime.datetime.now() - datetime.timedelta(int(delta))
            self.add_filter(key="publishedAfter",
                            value=d.isoformat('T')[:-7] + "Z",
                            label=labels[index])
            self.mode = 'filter'
            self.page = 1
            self.update()

        def choose_filter(self, filter_code, header, options):
            """
            open dialog and let user choose filter from *options
            filter gets removed in case value is empty
            filter_code: filter code from API
            options: list of tuples with 2 items each: first is value, second is label
            """
            values = [i[0] for i in options]
            labels = [i[1] for i in options]
            if header > 31000:
                index = xbmcgui.Dialog().select(heading=addon.getLocalizedString(header),
                                                list=labels)
            else:
                index = xbmcgui.Dialog().select(heading=xbmc.getLocalizedString(header),
                                                list=labels)
            if index == -1:
                return None
            if not values[index]:
                self.remove_filter(filter_code)
            self.add_filter(key=filter_code,
                            value=values[index],
                            label=labels[index])

        def choose_sort_method(self, sort_key):
            """
            open dialog and let user choose sortmethod
            returns True if sorthmethod changed
            """
            listitems = list(self.SORTS[sort_key].values())
            sort_strings = list(self.SORTS[sort_key].keys())
            preselect = listitems.index(self.sort_label) if self.sort_label in listitems else -1
            index = xbmcgui.Dialog().select(heading=addon.getLocalizedString(32104),
                                            list=listitems,
                                            preselect=preselect)
            if index == -1 or listitems[index] == self.sort_label:
                return False
            self.sort = sort_strings[index]
            self.sort_label = listitems[index]
            self.page = 1
            return True

        @ch.click(ID_BUTTON_LANGUAGEFILTER)
        def set_language_filter(self):
            options = [("en", "en"),
                       ("de", "de"),
                       ("fr", "fr")]
            self.choose_filter("regionCode", 32151, options)
            self.mode = 'filter'
            self.page = 1
            self.update()

        @ch.click(ID_BUTTON_DIMENSIONFILTER)
        def set_dimension_filter(self):
            options = [("2d", "2D"),
                       ("3d", "3D"),
                       ("any", xbmc.getLocalizedString(593))]
            self.choose_filter("videoDimension", 32151, options)
            self.mode = 'filter'
            self.page = 1
            self.update()

        @ch.click(ID_BUTTON_DURATIONFILTER)
        def set_duration_filter(self):
            options = [("long", addon.getLocalizedString(33013)),
                       ("medium", xbmc.getLocalizedString(601)),
                       ("short", addon.getLocalizedString(33012)),
                       ("any", xbmc.getLocalizedString(593))]
            self.choose_filter("videoDuration", 32151, options)
            self.mode = 'filter'
            self.page = 1
            self.update()

        @ch.click(ID_BUTTON_CAPTIONFILTER)
        def set_caption_filter(self):
            options = [("closedCaption", xbmc.getLocalizedString(107)),
                       ("none", xbmc.getLocalizedString(106)),
                       ("any", xbmc.getLocalizedString(593))]
            self.choose_filter("videoCaption", 287, options)
            self.mode = 'filter'
            self.page = 1
            self.update()

        @ch.click(ID_BUTTON_DEFINITIONFILTER)
        def set_definition_filter(self):
            options = [("high", xbmc.getLocalizedString(419)),
                       ("standard", xbmc.getLocalizedString(602)),
                       ("any", xbmc.getLocalizedString(593))]
            self.choose_filter("videoDefinition", 169, options)
            self.mode = 'filter'
            self.page = 1
            self.update()

        @ch.click(ID_BUTTON_TYPEFILTER)
        def set_type_filter(self):
            options = [("movie", xbmc.getLocalizedString(20338)),
                       ("episode", xbmc.getLocalizedString(20359)),
                       ("any", xbmc.getLocalizedString(593))]
            self.choose_filter("videoType", 32151, options)
            self.mode = 'filter'
            self.page = 1
            self.update()

        @ch.click(ID_BUTTON_SORTTYPE)
        def get_sort_type(self):
            if not self.choose_sort_method(self.type):
                return None
            self.update()

        @ch.click(5018)
        def close_all(self):
            xbmc.executebuiltin('Dialog.Close(all,true)')
            wm.window_stack_empty()

        #@ch.context("video")
        @ch.action('contextmenu', 500)
        def context_menu(self):
            listitem = self.listitem
            if self.type == "video":
                more_vids = "{} [B]{}[/B]".format(addon.getLocalizedString(32081),
                                                  listitem.getProperty("channel_title"))
                index = xbmcgui.Dialog().contextmenu(list=[addon.getLocalizedString(32069), more_vids])
                if index < 0:
                    return None
                elif index == 0:
                    filter_ = [{"id": listitem.getProperty("youtube_id"),
                                "type": "relatedToVideoId",
                                "label": listitem.getLabel()}]
                    self.close()
                    wm.open_youtube_list(filters=filter_)
                elif index == 1:
                    filter_ = [{"id": listitem.getProperty("channel_id"),
                                "type": "channelId",
                                "label": listitem.getProperty("channel_title")}]
                    self.close()
                    wm.open_youtube_list(filters=filter_)

        def update_ui(self):
            is_video = self.type == "video"
            self.getControl(ID_BUTTON_DIMENSIONFILTER).setVisible(is_video)
            self.getControl(ID_BUTTON_DURATIONFILTER).setVisible(is_video)
            self.getControl(ID_BUTTON_CAPTIONFILTER).setVisible(is_video)
            self.getControl(ID_BUTTON_DEFINITIONFILTER).setVisible(is_video)
            self.setProperty('TotalPages', str(self.total_pages))
            self.setProperty('TotalItems', str(self.total_items))
            super(DialogYoutubeList, self).update_ui()

        def go_to_next_page(self):
            self.get_column()
            if self.page < self.total_pages:
                wm.page_position = self.position -44
                Utils.show_busy()
                self.page += 1
                self.prev_page_token = self.page_token
                self.page_token = self.next_page_token
                Utils.show_busy()
                pre_page = self.page
                pre_curr_page = self.getProperty('CurrentPage')
                self.update()
                post_page = self.page
                post_curr_page = self.getProperty('CurrentPage')
                if pre_page == post_page and pre_curr_page == post_curr_page:
                    self.update()

        def go_to_prev_page(self):
            self.get_column()
            if self.page > 1:
                wm.prev_page_flag = True
                wm.prev_page_num = self.page -1 
                wm.page_position = self.position +44
                Utils.show_busy()
                self.page -= 1
                self.next_page_token = self.page_token
                self.page_token = self.prev_page_token
                Utils.show_busy()
                pre_page = self.page
                pre_curr_page = self.getProperty('CurrentPage')
                self.update()
                post_page = self.page
                post_curr_page = self.getProperty('CurrentPage')
                if pre_page == post_page and pre_curr_page == post_curr_page:
                    self.update()

        @property
        def default_sort(self):
            return "relevance"

        def add_filter(self, **kwargs):
            kwargs["typelabel"] = self.FILTERS[kwargs["key"]]
            super(DialogYoutubeList, self).add_filter(force_overwrite=True,
                                                      **kwargs)

        #@Utils.run_async
        def get_youtube_vids(self, search_str):
            #try:
            #    youtube_list = self.getControl(500)
            #except:
            #    return None
            filter_str = ''
            #xbmc.log(str(self.sort)+'===>OPENINFO', level=xbmc.LOGINFO)
            #xbmc.log(str(self.filters)+'===>OPENINFO', level=xbmc.LOGINFO)
            for i in self.filters:
                filter_str = filter_str + str(i['type']) + '=' + str(i['id']) + '&'
            if self.sort:
                filter_str = filter_str + str('order=') + self.sort + '&'
            #xbmc.log(str(filter_str)+'===>OPENINFO', level=xbmc.LOGINFO)
            filter_str = filter_str.replace('regionCode','relevanceLanguage')
            if self.page ==1:
                result = YouTube.search_youtube(search_str, limit = 48, filter_str=filter_str)
            else:
                result = YouTube.search_youtube(search_str, limit = 48, page = self.page_token, filter_str=filter_str)
            #result = YouTube.search_youtube(search_str=search_str, hd=True, limit=1000, extended=False, page=str(self.page), filter_str='')
            #xbmc.log(str(result)+'===>OPENINFO', level=xbmc.LOGINFO)
            self.total_items = int(48)
            try: self.total_pages = int(result['total_results']/48)
            except: return None
            self.prev_page_token = str(result['prev_page_token'])
            self.next_page_token = str(result['next_page_token'])
            #try:
            #    result = YouTube.search_youtube(search_str, limit=10)
            #    xbmc.log(str(result)+'result===>OPENINFO', level=xbmc.LOGINFO)
            #except:
            #    return None
            #if not self.yt_listitems:
            self.yt_listitems = result.get('listitems', [])
            if 'videos' in self.data:
                vid_ids = [item['key'] for item in self.data['videos']]
                self.yt_listitems = [i for i in self.yt_listitems if i['youtube_id'] not in vid_ids]
            #youtube_list.reset()
            #youtube_list.addItems(Utils.create_listitems(self.yt_listitems))
            #self.listitems = Utils.create_listitems(self.yt_listitems)
            """
            info = {
                'listitems': self.yt_listitems,
                'results_per_page': self.total_items,
                'total_results': self.total_pages, 
                'next_page_token': self.next_page_token,
                'prev_page_token': self.prev_page_token
                }
            """
            #self.listitems = Utils.create_listitems(self.yt_listitems,preload_images=0, enable_clearlogo=False, info=info)
            return self.yt_listitems

        def fetch_data(self, force=False):

            if wm.pop_video_list == True:
                self.page = int(wm.prev_window['params']['page'])
                self.mode = wm.prev_window['params']['mode']
                self.type = wm.prev_window['params']['type']
                self.order = wm.prev_window['params']['order']
                self.search_str =wm.prev_window['params']['search_str']
                self.filter_label =wm.prev_window['params']['filter_label']
                self.list_id = wm.prev_window['params']['list_id']
                self.filter_url = wm.prev_window['params']['filter_url']
                self.media_type = wm.prev_window['params']['media_type']
                self.filters = wm.prev_window['params']['filters']
                self.filter = wm.prev_window['params']['filter']
                info = {
                    'listitems': wm.prev_window['params']['listitems'],
                    'results_per_page': wm.prev_window['params']['total_pages'],
                    'total_results': wm.prev_window['params']['total_items'],
                    'next_page_token': wm.prev_window['params']['next_page_token'],
                    'prev_page_token': wm.prev_window['params']['prev_page_token']
                    }
                self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
                self.position = xbmcgui.Window(10000).getProperty('position')
                if str(self.position) != 'No position':
                    xbmc.executebuiltin('Control.SetFocus(%s,%s)' % (self.focus_id,self.position))
                wm.pop_video_list = False
                return info

            yt_listitems = self.get_youtube_vids(self.search_str)

            self.set_filter_label()
            if self.search_str:
                self.filter_label = 'Results for: %s' % (self.search_str) + "  " + self.filter_label
            info = {
                'listitems': yt_listitems,
                'results_per_page': self.total_pages,
                'total_results': self.total_items,
                'next_page_token': self.next_page_token,
                'prev_page_token': self.prev_page_token
                }
            return info
            #return youtube.search(search_str=self.search_str,
            #                      orderby=self.sort,
            #                      extended=True,
            #                      filters={item["type"]: item["id"] for item in self.filters},
            #                      media_type=self.type,
            #                      page=self.page_token)

    Utils.hide_busy()
    return DialogYoutubeList


def open(self, search_str="", filters=None, sort="relevance", filter_label="", media_type="video"):
    """
    open video list, deal with window stack
    """
    YouTube = get_window(windows.DialogXML)
    dialog = YouTube(u'script-%s-YoutubeList.xml' % addon.NAME, addon.PATH,
                     search_str=search_str,
                     filters=[] if not filters else filters,
                     filter_label=filter_label,
                     type=media_type)
    return dialog
