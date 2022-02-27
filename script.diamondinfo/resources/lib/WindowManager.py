import re, urllib.request, urllib.parse, urllib.error
import xbmc, xbmcgui, xbmcaddon
from resources.lib import Utils
import sys
import gc
import importlib

global dialog
dialog = None

class WindowManager(object):
    if not 'auto_library' in str(sys.argv) and not xbmc.Player().isPlaying():
        Utils.show_busy()
    window_stack = []

    def __init__(self):
        global dialog
        self.reopen_window = False
        self.last_control = None
        self.active_dialog = None
        osAndroid = xbmc.getCondVisibility('system.platform.android')
        if osAndroid:
            self.osAndroid_path = '-android'
        else:
            self.osAndroid_path = ''

    def add_to_stack(self, window):
        if Utils.window_stack_enable == 'true':
            self.window_stack.append(window)
        if Utils.window_stack_enable == 'false':
            try: window_stack = []
            except: pass
            try: self.window_stack = window_stack
            except: pass
            try: self.reopen_window = False
            except: pass
            try: self.last_control = None
            except: pass
            try: self.active_dialog = None
            except: pass
            try: window = None
            except: pass
            try: del window
            except: pass
            gc.collect()
            try:
                for k,v in sys.modules.items():
                    if k.startswith('xbmc'):
                        importlib.reload(v)
                import xbmc, xbmcgui, xbmcaddon
            except:
                pass
            return

    #def global_dialog(self):
    #    global dialog
    #    return dialog

    def close_stack(self, window):
        window.close()
        try:
            self.active_dialog.close()
        except:
            pass
        self.reopen_window = False
        self.last_control = None
        self.active_dialog = None
        try: window = None
        except: pass
        try: del window
        except: pass
        self.window_stack = []
        gc.collect()
        try:
            for k,v in sys.modules.items():
                if k.startswith('xbmc'):
                    importlib.reload(v)
            import xbmc, xbmcgui, xbmcaddon
        except:
            pass
        try: del self.active_dialog
        except: pass
        gc.collect()
        return

    def pop_stack2(self, window):
        self.active_dialog = window
        window = None
        try: del window
        except: pass
        gc.collect()
        self.active_dialog.doModal()
        try: del self.active_dialog
        except: pass
        gc.collect()
        #if self.last_control:
        #    xbmc.sleep(100)
        #    xbmc.executebuiltin('SetFocus(%s)' % self.last_control)
        #return


    def pop_stack(self):
        if self.window_stack and Utils.window_stack_enable == 'true':
            self.active_dialog = self.window_stack.pop()
            xbmc.sleep(250)
            self.active_dialog.doModal()
        elif self.reopen_window:
            xbmc.sleep(500)
            xbmc.executebuiltin('Action(Info)')
            if self.last_control:
                xbmc.sleep(100)
                xbmc.executebuiltin('SetFocus(%s)' % self.last_control)

    def open_movie_info(self, prev_window=None, movie_id=None, dbid=None, name=None, imdb_id=None):
        #global dialog
        #dialog = None
        from resources.lib.library import addon_ID
        from resources.lib.TheMovieDB import get_movie_tmdb_id, play_movie_trailer
        from resources.lib.DialogVideoInfo import get_movie_window
        if not 'tt' in str(imdb_id):
            imdb_id=None
        if not movie_id:
            movie_id = get_movie_tmdb_id(imdb_id=imdb_id, dbid=dbid, name=name)
        movieclass = get_movie_window(DialogXML)
        if Utils.NETFLIX_VIEW == 'true' or Utils.NETFLIX_VIEW2 == 'true':
            dialog = movieclass(str(addon_ID())+'-DialogVideoInfo-Netflix.xml', Utils.ADDON_PATH, id=movie_id, dbid=dbid)
            if Utils.AUTOPLAY_TRAILER == 'true' and not xbmc.getCondVisibility('VideoPlayer.IsFullscreen') and not xbmc.Player().isPlayingAudio():
                play_movie_trailer(movie_id)
        else:
            if Utils.SKIN_DIR == 'skin.estuary':
                dialog = movieclass(str(addon_ID())+self.osAndroid_path+'-DialogVideoInfo-Estuary.xml', Utils.ADDON_PATH, id=movie_id, dbid=dbid)
            elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
                dialog = movieclass(str(addon_ID())+'-DialogVideoInfo-Aura.xml', Utils.ADDON_PATH, id=movie_id, dbid=dbid)
            else:
                dialog = movieclass(str(addon_ID())+'-DialogVideoInfo.xml', Utils.ADDON_PATH, id=movie_id, dbid=dbid)
        self.open_dialog(dialog, prev_window)
        try: del dialog
        except: pass
        try: del movieclass
        except: pass
        try: del get_movie_window
        except: pass
        gc.collect()

    def open_tvshow_info(self, prev_window=None, tmdb_id=None, dbid=None, tvdb_id=None, imdb_id=None, name=None):
        #global dialog
        #dialog = None
        from resources.lib.library import addon_ID
        dbid = int(dbid) if dbid and int(dbid) > 0 else None
        from resources.lib.TheMovieDB import get_show_tmdb_id, search_media, play_tv_trailer, get_tvshow_info
        from resources.lib.DialogTVShowInfo import get_tvshow_window
        from resources.lib.local_db import get_imdb_id_from_db
        from resources.lib.local_db import get_info_from_db
        if tmdb_id:
            pass
        elif tvdb_id:
            tmdb_id = get_show_tmdb_id(tvdb_id)
        elif imdb_id and 'tt' in str(imdb_id):
            tmdb_id = get_show_tmdb_id(imdb_id=imdb_id, source='imdb_id')
        elif dbid:
            tvdb_id = get_imdb_id_from_db(media_type='tvshow', dbid=dbid)
            tv_info = get_info_from_db(media_type='tvshow', dbid=dbid)
            try: year = str(tv_info['year'])
            except: year = ''
            if tvdb_id:
                try:
                    tmdb_id = get_show_tmdb_id(tvdb_id)
                except IndexError:
                    if name:
                        if year != '':
                            tvshow = get_tvshow_info(tvshow_label=name, year=year)
                            if tvshow and tvshow.get('id'):
                                tmdb_id = tvshow.get('id')
                            else:
                                tmdb_id = search_media(media_name=name, year='', media_type='tv')
                    else:
                        name = xbmc.getInfoLabel('listitem.TvShowTitle')
                        if str(name) != '':
                            name = xbmc.getInfoLabel('listitem.Label')
                        tvshow = get_tvshow_info(tvshow_label=name, year=year)
                        if tvshow and tvshow.get('id'):
                            tmdb_id = tvshow.get('id')
                        else:
                            tmdb_id = search_media(media_name=name, year='', media_type='tv')
        elif name:
            tvshow = get_tvshow_info(tvshow_label=name, year=year)
            if tvshow and tvshow.get('id'):
                tmdb_id = tvshow.get('id')
            else:
                tmdb_id = search_media(media_name=name, year='', media_type='tv')
        tvshow_class = get_tvshow_window(DialogXML)
        if Utils.NETFLIX_VIEW == 'true' or Utils.NETFLIX_VIEW2 == 'true':
            dialog = tvshow_class(str(addon_ID())+'-DialogVideoInfo-Netflix.xml', Utils.ADDON_PATH, tmdb_id=tmdb_id, dbid=dbid)
            if Utils.AUTOPLAY_TRAILER == 'true' and not xbmc.getCondVisibility('VideoPlayer.IsFullscreen') and not xbmc.Player().isPlayingAudio():
                play_tv_trailer(tmdb_id)
        else:
            if Utils.SKIN_DIR == 'skin.estuary':
                dialog = tvshow_class(str(addon_ID())+self.osAndroid_path+'-DialogVideoInfo-Estuary.xml', Utils.ADDON_PATH, tmdb_id=tmdb_id, dbid=dbid)
            elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
                dialog = tvshow_class(str(addon_ID())+'-DialogVideoInfo-Aura.xml', Utils.ADDON_PATH, tmdb_id=tmdb_id, dbid=dbid)
            else:
                dialog = tvshow_class(str(addon_ID())+'-DialogVideoInfo.xml', Utils.ADDON_PATH, tmdb_id=tmdb_id, dbid=dbid)
        self.open_dialog(dialog, prev_window)
        try: del dialog
        except: pass
        try: del tvshow_class
        except: pass
        try: del get_tvshow_window
        except: pass
        gc.collect()

    def open_season_info(self, prev_window=None, tvshow_id=None, season=None, tvshow=None, dbid=None):
        #global dialog
        #dialog = None
        from resources.lib.library import addon_ID
        from resources.lib.TheMovieDB import get_tmdb_data
        from resources.lib.DialogSeasonInfo import get_season_window
        if not tvshow_id:
            response = get_tmdb_data('search/tv?query=%s&language=%s&' % (Utils.url_quote(tvshow), xbmcaddon.Addon().getSetting('LanguageID')), 30)
            if response['results']:
                tvshow_id = str(response['results'][0]['id'])
            else:
                tvshow = re.sub('\(.*?\)', '', tvshow)
                response = get_tmdb_data('search/tv?query=%s&language=%s&' % (Utils.url_quote(tvshow), xbmcaddon.Addon().getSetting('LanguageID')), 30)
                if response['results']:
                    tvshow_id = str(response['results'][0]['id'])
        season_class = get_season_window(DialogXML)
        if Utils.NETFLIX_VIEW == 'true' or Utils.NETFLIX_VIEW2 == 'true':
            dialog = season_class(str(addon_ID())+'-DialogVideoInfo-Netflix.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, dbid=dbid)
        else:
            if Utils.SKIN_DIR == 'skin.estuary':
                dialog = season_class(str(addon_ID())+self.osAndroid_path+'-DialogVideoInfo-Estuary.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, dbid=dbid)
            elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
                dialog = season_class(str(addon_ID())+'-DialogVideoInfo-Aura.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, dbid=dbid)
            else:
                dialog = season_class(str(addon_ID())+'-DialogVideoInfo.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, dbid=dbid)
        self.open_dialog(dialog, prev_window)
        try: del dialog
        except: pass
        try: del season_class
        except: pass
        try: del get_season_window
        except: pass
        gc.collect()

    def open_episode_info(self, prev_window=None, tvshow_id=None, tvdb_id=None, season=None, episode=None, tvshow=None, dbid=None):
        #global dialog
        #dialog = None
        from resources.lib.library import addon_ID
        from resources.lib.TheMovieDB import get_tmdb_data, get_show_tmdb_id
        from resources.lib.DialogEpisodeInfo import get_episode_window
        if not tvshow_id:
            if tvdb_id:
                tvshow_id = get_show_tmdb_id(tvdb_id)
            else:
                response = get_tmdb_data('search/tv?query=%s&language=%s&' % (Utils.url_quote(tvshow), xbmcaddon.Addon().getSetting('LanguageID')), 30)
                if response['results']:
                    tvshow_id = str(response['results'][0]['id'])
                else:
                    tvshow = re.sub('\(.*?\)', '', tvshow)
                    response = get_tmdb_data('search/tv?query=%s&language=%s&' % (Utils.url_quote(tvshow), xbmcaddon.Addon().getSetting('LanguageID')), 30)
                    if response['results']:
                        tvshow_id = str(response['results'][0]['id'])
        ep_class = get_episode_window(DialogXML)
        if Utils.NETFLIX_VIEW == 'true' or Utils.NETFLIX_VIEW2 == 'true':
            dialog = ep_class(str(addon_ID())+'-DialogVideoInfo-Netflix.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, episode=episode, dbid=dbid)
        else:
            if Utils.SKIN_DIR == 'skin.estuary':
                dialog = ep_class(str(addon_ID())+self.osAndroid_path+'-DialogVideoInfo-Estuary.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, episode=episode, dbid=dbid)
            elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
                dialog = ep_class(str(addon_ID())+'-DialogVideoInfo-Aura.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, episode=episode, dbid=dbid)
            else:
                dialog = ep_class(str(addon_ID())+'-DialogVideoInfo.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, episode=episode, dbid=dbid)
        self.open_dialog(dialog, prev_window)
        prev_window = None
        try: del dialog
        except: pass
        try: del ep_class
        except: pass
        try: del get_episode_window
        except: pass
        gc.collect()

    def open_actor_info(self, prev_window=None, actor_id=None, name=None):
        #global dialog
        #dialog = None
        from resources.lib.DialogActorInfo import get_actor_window
        from resources.lib.TheMovieDB import get_person_info
        from resources.lib.library import addon_ID
        if not actor_id:
            try:
                name = name.decode('utf-8').split(' ' + 'as' + ' ')
            except:
                name = str(name).split(' ' + 'as' + ' ')
            names = name[0].strip().split(' / ')
            if len(names) > 1:
                ret = xbmcgui.Dialog().select(heading='Select person', list=names)
                if ret == -1:
                    return None
                name = names[ret]
            else:
                name = names[0]
            Utils.show_busy()
            actor_info = get_person_info(name)
            if actor_info:
                actor_id = actor_info['id']
            else:
                return None
        else:
            Utils.show_busy()
        actor_class = get_actor_window(DialogXML)
        if Utils.SKIN_DIR == 'skin.estuary':
            dialog = actor_class(str(addon_ID())+self.osAndroid_path+'-DialogInfo-Estuary.xml', Utils.ADDON_PATH, id=actor_id)
        elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
            dialog = actor_class(str(addon_ID())+'-DialogInfo-Aura.xml', Utils.ADDON_PATH, id=actor_id)
        else:
            dialog = actor_class(str(addon_ID())+'-DialogInfo.xml', Utils.ADDON_PATH, id=actor_id)
        self.open_dialog(dialog, prev_window)
        try: del dialog
        except: pass
        try: del actor_class
        except: pass
        try: del get_actor_window
        except: pass
        gc.collect()

    def open_video_list(self, prev_window=None, listitems=None, filters=[], mode='filter', list_id=False, filter_label='', media_type='movie', search_str=''):
        #global dialog
        #dialog = None
        from resources.lib.library import addon_ID
        from resources.lib.DialogVideoList import get_tmdb_window
        browser_class = get_tmdb_window(DialogXML)
        if Utils.NETFLIX_VIEW == 'true':
            dialog = browser_class(str(addon_ID())+'-VideoList-Netflix.xml', Utils.ADDON_PATH, listitems=listitems, filters=filters, mode=mode, list_id=list_id, filter_label=filter_label, type=media_type, search_str=search_str)
        else:
            if Utils.SKIN_DIR == 'skin.estuary':
                dialog = browser_class(str(addon_ID())+self.osAndroid_path+'-VideoList-Estuary.xml', Utils.ADDON_PATH, listitems=listitems, filters=filters, mode=mode, list_id=list_id, filter_label=filter_label, type=media_type, search_str=search_str)
            elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
                dialog = browser_class(str(addon_ID())+'-VideoList-Aura.xml', Utils.ADDON_PATH, listitems=listitems, filters=filters, mode=mode, list_id=list_id, filter_label=filter_label, type=media_type, search_str=search_str)
            else:
                dialog = browser_class(str(addon_ID())+'-VideoList.xml', Utils.ADDON_PATH, listitems=listitems, filters=filters, mode=mode, list_id=list_id, filter_label=filter_label, type=media_type, search_str=search_str)
        if prev_window:
            self.add_to_stack(prev_window)
            prev_window.close()
            prev_window = None
            try: del prev_window
            except: pass
        Utils.hide_busy()
        gc.collect()
        dialog.doModal()
        try: dialog.close()
        except: pass
        try: del dialog
        except: pass
        try: del browser_class
        except: pass
        del get_tmdb_window
        try: del self
        except: pass
        gc.collect()

    def open_youtube_list(self, search_str="", filters=None, filter_label="", media_type="video"):
        """
        open video list, deal with window stack
        """
        from resources.lib.library import addon_ID
        from resources.lib.DialogYoutubeList import get_youtube_window
        browser_class = get_youtube_window(DialogXML)
        dialog = browser_class(str(addon_ID())+'-YoutubeList.xml', Utils.ADDON_PATH, search_str=search_str, filters=[] if not filters else filters, type='video')
        #self.open_dialog(dialog)
        dialog.doModal()
        try: dialog.close()
        except: pass
        try: del dialog
        except: pass
        try: del browser_class
        except: pass
        del get_youtube_window
        try: del self
        except: pass
        gc.collect()

    def open_slideshow(self, listitems, index):
        from resources.lib.library import addon_ID
        if Utils.SKIN_DIR == 'skin.estuary':
            slideshow = SlideShow(str(addon_ID())+'-SlideShow-Estuary.xml', Utils.ADDON_PATH, listitems=listitems, index=index)
        elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
            slideshow = SlideShow(str(addon_ID())+'-SlideShow-Aura.xml', Utils.ADDON_PATH, listitems=listitems, index=index)
        else:
            slideshow = SlideShow(str(addon_ID())+'-SlideShow.xml', Utils.ADDON_PATH, listitems=listitems, index=index)
        Utils.hide_busy()
        slideshow.doModal()
        return slideshow.position

    def open_textviewer(self, header='', text='', color='FFFFFFFF'):
        dialog = TextViewerDialog('DialogTextViewer.xml', Utils.ADDON_PATH, header=header, text=text, color=color)
        Utils.hide_busy()
        dialog.doModal()
        try: del dialog
        except: pass
        gc.collect()

    def open_selectdialog(self, listitems):
        dialog = SelectDialog('DialogSelect.xml', Utils.ADDON_PATH, listing=listitems)
        Utils.hide_busy()
        dialog.doModal()
        return dialog.listitem, dialog.index

    def open_dialog(self, dialog, prev_window):
        #global dialog
        if dialog.data:
            if Utils.window_stack_enable == 'true':
                self.active_dialog = dialog
            if xbmc.getCondVisibility('Window.IsVisible(movieinformation)'):
                self.reopen_window = True
                try:
                    self.last_control = xbmc.getInfoLabel('System.CurrentControlId').decode('utf-8')
                except:
                    self.last_control = xbmc.getInfoLabel('System.CurrentControlId')
                xbmc.executebuiltin('Dialog.Close(movieinformation)')
            if prev_window:
                if xbmc.Player().isPlayingVideo() and not xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
                    xbmc.Player().stop()
                self.add_to_stack(prev_window)
                prev_window.close()
                prev_window = None
                del prev_window
            Utils.hide_busy()
            gc.collect()
            dialog.doModal()
            dialog.close()
            try: del dialog
            except: pass
            try: del prev_window
            except: pass
            try: self.active_dialog.close()
            except: pass
            try: del self.active_dialog
            except: pass
            try: del self
            except: pass
            gc.collect()
        else:
            Utils.hide_busy()
            self.active_dialog = None
            try: dialog.close()
            except: pass
            try: del dialog
            except: pass
            try: del prev_window
            except: pass
            self.active_dialog.close()
            try: del self.active_dialog
            except: pass
            gc.collect()
            Utils.notify('Could not find item at MovieDB')

wm = WindowManager()

class DialogXML(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.window_type = 'dialog'

    def onInit(self):
        self.window_id = xbmcgui.getCurrentWindowDialogId()
        self.window = xbmcgui.Window(self.window_id)

class TextViewerDialog(xbmcgui.WindowXMLDialog):

    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.text = kwargs.get('text')
        self.header = kwargs.get('header')
        self.color = kwargs.get('color')

    def onInit(self):
        window_id = xbmcgui.getCurrentWindowDialogId()
        xbmcgui.Window(window_id).setProperty('WindowColor', self.color)
        self.getControl(1).setLabel(self.header)
        self.getControl(5).setText(self.text)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, control_id):
        pass

    def onFocus(self, control_id):
        pass

class SlideShow(DialogXML):

    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        self.images = kwargs.get('listitems')
        self.index = kwargs.get('index')
        self.image = kwargs.get('image')
        self.action = None

    def onInit(self):
        super(SlideShow, self).onInit()
        if not self.images:
            return None
        self.getControl(10001).addItems(Utils.create_listitems(self.images))
        self.getControl(10001).selectItem(self.index)
        self.setFocusId(10001)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.position = self.getControl(10001).getSelectedPosition()
            self.close()

class SelectDialog(xbmcgui.WindowXMLDialog):

    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.items = kwargs.get('listing')
        self.listitems = Utils.create_listitems(self.items)
        self.listitem = None
        self.index = -1

    def onInit(self):
        self.list = self.getControl(6)
        self.getControl(3).setVisible(False)
        self.getControl(5).setVisible(False)
        self.getControl(1).setLabel('Choose option')
        self.list.addItems(self.listitems)
        self.setFocus(self.list)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, control_id):
        if control_id == 6 or control_id == 3:
            self.index = int(self.list.getSelectedItem().getProperty('index'))
            self.listitem = self.items[self.index]
            self.close()

    def onFocus(self, control_id):
        pass