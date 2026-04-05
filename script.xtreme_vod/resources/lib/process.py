import os, shutil
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from resources.lib import Utils
from resources.lib.WindowManager import wm
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import icon_path

from urllib.parse import quote, urlencode, quote_plus, unquote, unquote_plus
import time

from resources.lib.Utils import tools_log as log
from inspect import currentframe, getframeinfo

#log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

def start_info_actions(infos, params):
	addonID = addon_ID()
	addonID_short = addon_ID_short()

	wm.custom_filter = params.get('meta_filter')
	log(Utils.db_con)
	if wm.custom_filter:
		wm.custom_filter = eval(unquote(wm.custom_filter))

	keep_stack = params.get('keep_stack',False)

	if 'imdbid' in params and 'imdb_id' not in params:
		params['imdb_id'] = params['imdbid']
	for info in infos:
		Utils.show_busy()
		data = [], ''

		if info == 'imdb_trailers_best' or info == 'imdb_trailers_choice':
			import imdb_trailers
			imdb_id = params.get('imdb_id')
			if info == 'imdb_trailers_best':
				select = False
			else:
				try: select = params.get('select')
				except: select = False
				if str(select).lower() == 'true' or select == True:
					select = True
				else:
					select = False
			try: season = int(params.get('season'))
			except: season = None
			imdb_trailers.play_imdb_trailer(imdb_id=imdb_id, select=select, season=season)

		if info == 'select_pvr_client':
			client = select_pvr_client()
			if client:
				xbmc.executebuiltin('Dialog.Close(all,true)')
				xbmcaddon.Addon(addon_ID()).setSetting('pvr_client', client)
				Utils.tools_log(client)
			xbmcgui.Dialog().notification("pvr_client_UPDATED",client)
			Utils.hide_busy()
			return

		if info == 'reset_stuff':
			reset_stuff()
			Utils.hide_busy()
			return

		if info == 'm3u_ts_m3u8':
			from xtream2m3u_run import m3u_ts_m3u8
			m3u_ts_m3u8()
			Utils.hide_busy()
			return

		if info == 'generate_m3u_xml':
			from xtream2m3u_run import generate_m3u
			from xtream2m3u_run import generate_xmltv
			Utils.show_busy()
			generate_m3u()
			generate_xmltv()
			Utils.hide_busy()
			return

		if info == 'get_all_vod':
			from resources.lib.TheMovieDB import get_vod_data
			movies = get_vod_data(action= 'get_vod_streams' ,cache_days=1) 
			vod_movies = []
			for i in movies:
				vod_movies.append(i['name'])
			movies = get_vod_data(action= 'get_series' ,cache_days=1) 
			vod_tv = []
			for i in movies:
				vod_tv.append(i['name'])
			Utils.tools_log(vod_movies)
			Utils.tools_log(vod_tv)
			Utils.hide_busy()
			return

		if info == 'test':
			Utils.tools_log('ResetEPG')
			Utils.ResetEPG()
			Utils.hide_busy()
			return

		elif info == 'video_play_unpop':
			wm.video_play_unpop()
			return

		elif info == 'pop_stack':
			wm.pop_stack()
			return

		if info == 'test_route':
			from resources.lib.TheMovieDB import load_vod_to_sql
			load_vod_to_sql()
			#return
			
			from resources.lib.TheMovieDB import filter_vod
			test_list = [{'title': 'True Romance', 'Label': 'True Romance', 'OriginalTitle': 'True Romance', 'id': '319', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=319&year=1993', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Clarence marries hooker Alabama, steals cocaine from her pimp, and tries to sell it in Hollywood, while the owners of the coke try to reclaim it.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=319', 'Popularity': 6.6252, 'Rating': 7.536, 'credit_id': '52fe4237c3a36847f800ce91', 'character': 'Mentor', 'job': '', 'department': '', 'Votes': 3014, 'User_Rating': '', 'year': '1993', 'genre': 'Action / Crime / Romance', 'Premiered': '1993-09-09', 'poster': 'https://image.tmdb.org/t/p/w500/39lXk6ud6KiJgGbbWI2PUKS7y2.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/39lXk6ud6KiJgGbbWI2PUKS7y2.jpg', 'original': 'https://image.tmdb.org/t/p/original/1Uh8yuXlFcMDpVHWZJidjanT06e.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/39lXk6ud6KiJgGbbWI2PUKS7y2.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/39lXk6ud6KiJgGbbWI2PUKS7y2.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/1Uh8yuXlFcMDpVHWZJidjanT06e.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/1Uh8yuXlFcMDpVHWZJidjanT06e.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/1Uh8yuXlFcMDpVHWZJidjanT06e.jpg'}, {'title': 'Batman Forever', 'Label': 'Batman Forever', 'OriginalTitle': 'Batman Forever', 'id': '414', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=414&year=1995', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Batman faces off against two foes: the schizophrenic, horribly scarred former District Attorney Harvey Dent, aka Two-Face, and the Riddler, a disgruntled ex-Wayne Enterprises inventor seeking revenge against his former employer by unleashing his brain-sucking weapon on Gotham City's residents. As the caped crusader also copes with tortured memories of his parents' murder, he has a new romance, with psychologist Chase Meridian.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=414', 'Popularity': 7.1195, 'Rating': 5.453, 'credit_id': '52fe4240c3a36847f800fdf5', 'character': 'Bruce Wayne / Batman', 'job': '', 'department': '', 'Votes': 5534, 'User_Rating': '', 'year': '1995', 'genre': 'Action / Crime / Fantasy', 'Premiered': '1995-06-16', 'poster': 'https://image.tmdb.org/t/p/w500/i0fJS8M5UKoETjjJ0zwUiKaR8tr.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/i0fJS8M5UKoETjjJ0zwUiKaR8tr.jpg', 'original': 'https://image.tmdb.org/t/p/original/snlu32RmjldF9b068UURJg8sQtn.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/i0fJS8M5UKoETjjJ0zwUiKaR8tr.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/i0fJS8M5UKoETjjJ0zwUiKaR8tr.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/snlu32RmjldF9b068UURJg8sQtn.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/snlu32RmjldF9b068UURJg8sQtn.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/snlu32RmjldF9b068UURJg8sQtn.jpg'}, {'title': 'Heat', 'Label': 'Heat', 'OriginalTitle': 'Heat', 'id': '949', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=949&year=1995', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Obsessive master thief Neil McCauley leads a top-notch crew on various daring heists throughout Los Angeles while determined detective Vincent Hanna pursues him without rest. Each man recognizes and respects the ability and the dedication of the other even though they are aware their cat-and-mouse game may end in violence.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=949', 'Popularity': 17.9261, 'Rating': 7.93, 'credit_id': '52fe4292c3a36847f80291fd', 'character': 'Chris Shiherlis', 'job': '', 'department': '', 'Votes': 8212, 'User_Rating': '', 'year': '1995', 'genre': 'Crime / Drama / Action', 'Premiered': '1995-12-15', 'poster': 'https://image.tmdb.org/t/p/w500/umSVjVdbVwtx5ryCA2QXL44Durm.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/umSVjVdbVwtx5ryCA2QXL44Durm.jpg', 'original': 'https://image.tmdb.org/t/p/original/xKsnZDERG1dk95wuZ5q9iks3OL3.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/umSVjVdbVwtx5ryCA2QXL44Durm.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/umSVjVdbVwtx5ryCA2QXL44Durm.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/xKsnZDERG1dk95wuZ5q9iks3OL3.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/xKsnZDERG1dk95wuZ5q9iks3OL3.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/xKsnZDERG1dk95wuZ5q9iks3OL3.jpg'}, {'title': 'Memorial: Letters from American Soldiers', 'Label': 'Memorial: Letters from American Soldiers', 'OriginalTitle': 'Memorial: Letters from American Soldiers', 'id': '244738', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=244738&year=1991', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Memorial: Letters from American Soldiers is a 1991 American short documentary film directed by Bill Couturié. It shows footage from World War I, World War II, the Korean War, the Vietnam War and the Gulf War, overlaid with readings of letters from US troops fighting in each war. It was nominated for an Academy Award for Best Documentary Short.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=244738', 'Popularity': 1.2722, 'Rating': 5.7, 'credit_id': '6138b88b7a1bd6002cfb2032', 'character': 'Reader', 'job': '', 'department': '', 'Votes': 3, 'User_Rating': '', 'year': '1991', 'genre': 'Documentary', 'Premiered': '1991-01-01', 'poster': 'https://image.tmdb.org/t/p/w500/wnErKRknRBIr7aTI0wXDNuRuV4E.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/wnErKRknRBIr7aTI0wXDNuRuV4E.jpg', 'original': 'https://image.tmdb.org/t/p/original/wnErKRknRBIr7aTI0wXDNuRuV4E.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/wnErKRknRBIr7aTI0wXDNuRuV4E.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/wnErKRknRBIr7aTI0wXDNuRuV4E.jpg'}, {'title': 'The Real McCoy', 'Label': 'The Real McCoy', 'OriginalTitle': 'The Real McCoy', 'id': '2047', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=2047&year=1993', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Karen McCoy is released from prison with nothing but the clothes on her back. Before being incarcerated, Karen was the bank robber of her time, but now she wishes for nothing more than to settle down and start a new life. Unfortunately, between a dirty parole officer, old business partners, and an idiot ex, she will have to do the unthinkable in order to save her son.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=2047', 'Popularity': 1.9864, 'Rating': 5.7, 'credit_id': '52fe4330c3a36847f8040fbd', 'character': 'J.T. Barker', 'job': '', 'department': '', 'Votes': 259, 'User_Rating': '', 'year': '1993', 'genre': 'Action / Crime / Drama / Thriller', 'Premiered': '1993-09-10', 'poster': 'https://image.tmdb.org/t/p/w500/6sZTcKhLRNp07cVoqgcMZoK9Noo.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/6sZTcKhLRNp07cVoqgcMZoK9Noo.jpg', 'original': 'https://image.tmdb.org/t/p/original/fWuOFLP57Zapja5AqInxjDezdT2.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/6sZTcKhLRNp07cVoqgcMZoK9Noo.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/6sZTcKhLRNp07cVoqgcMZoK9Noo.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/fWuOFLP57Zapja5AqInxjDezdT2.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/fWuOFLP57Zapja5AqInxjDezdT2.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/fWuOFLP57Zapja5AqInxjDezdT2.jpg'}, {'title': 'The Saint', 'Label': 'The Saint', 'OriginalTitle': 'The Saint', 'id': '10003', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=10003&year=1997', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Simon Templar (The Saint), is a thief for hire, whose latest job to steal the secret process for cold fusion puts him at odds with a traitor bent on toppling the Russian government, as well as the woman who holds its secret.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=10003', 'Popularity': 3.3754, 'Rating': 6.097, 'credit_id': '52fe43039251416c750001c7', 'character': 'Simon Templar', 'job': '', 'department': '', 'Votes': 1224, 'User_Rating': '', 'year': '1997', 'genre': 'Thriller / Action / Romance / Science Fiction / Adventure', 'Premiered': '1997-04-03', 'poster': 'https://image.tmdb.org/t/p/w500/k43wPAVeepqzGwP52dKcknQjquj.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/k43wPAVeepqzGwP52dKcknQjquj.jpg', 'original': 'https://image.tmdb.org/t/p/original/3cdfnihGSrMiQWzmVPaEs3p2Mp1.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/k43wPAVeepqzGwP52dKcknQjquj.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/k43wPAVeepqzGwP52dKcknQjquj.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/3cdfnihGSrMiQWzmVPaEs3p2Mp1.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/3cdfnihGSrMiQWzmVPaEs3p2Mp1.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/3cdfnihGSrMiQWzmVPaEs3p2Mp1.jpg'}, {'title': 'Top Gun', 'Label': 'Top Gun', 'OriginalTitle': 'Top Gun', 'id': '744', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=744&year=1986', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "For Lieutenant Pete 'Maverick' Mitchell and his friend and co-pilot Nick 'Goose' Bradshaw, being accepted into an elite training school for fighter pilots is a dream come true. But a tragedy, as well as personal demons, will threaten Pete's dreams of becoming an ace pilot.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=744', 'Popularity': 12.5486, 'Rating': 7.1, 'credit_id': '52fe426fc3a36847f801e6c1', 'character': 'Ice', 'job': '', 'department': '', 'Votes': 9428, 'User_Rating': '', 'year': '1986', 'genre': 'Action / Drama / Romance', 'Premiered': '1986-05-16', 'poster': 'https://image.tmdb.org/t/p/w500/xUuHj3CgmZQ9P2cMaqQs4J0d4Zc.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/xUuHj3CgmZQ9P2cMaqQs4J0d4Zc.jpg', 'original': 'https://image.tmdb.org/t/p/original/dBgxEkWe17R0AJDAvAhpeVELQx2.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/xUuHj3CgmZQ9P2cMaqQs4J0d4Zc.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/xUuHj3CgmZQ9P2cMaqQs4J0d4Zc.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/dBgxEkWe17R0AJDAvAhpeVELQx2.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/dBgxEkWe17R0AJDAvAhpeVELQx2.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/dBgxEkWe17R0AJDAvAhpeVELQx2.jpg'}, {'title': 'The Doors', 'Label': 'The Doors', 'OriginalTitle': 'The Doors', 'id': '10537', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=10537&year=1991', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The story of the famous and influential 1960s rock band and its lead singer and composer, Jim Morrison.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=10537', 'Popularity': 4.2322, 'Rating': 7.108, 'credit_id': '52fe43839251416c75013437', 'character': 'Jim Morrison', 'job': '', 'department': '', 'Votes': 1578, 'User_Rating': '', 'year': '1991', 'genre': 'Music / Drama / History', 'Premiered': '1991-03-01', 'poster': 'https://image.tmdb.org/t/p/w500/x1LM3dzGuG6xOz0aT2e71o11vhu.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/x1LM3dzGuG6xOz0aT2e71o11vhu.jpg', 'original': 'https://image.tmdb.org/t/p/original/kGlEhkmFaGUvhBvLvhhq9i9OOXX.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/x1LM3dzGuG6xOz0aT2e71o11vhu.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/x1LM3dzGuG6xOz0aT2e71o11vhu.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/kGlEhkmFaGUvhBvLvhhq9i9OOXX.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/kGlEhkmFaGUvhBvLvhhq9i9OOXX.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/kGlEhkmFaGUvhBvLvhhq9i9OOXX.jpg'}, {'title': 'Willow', 'Label': 'Willow', 'OriginalTitle': 'Willow', 'id': '847', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=847&year=1988', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "The evil Queen Bavmorda hunts the newborn princess Elora Danan, a child prophesied to bring about her downfall. When the royal infant is found by Willow, a timid farmer and aspiring sorcerer, he's entrusted with delivering her from evil.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=847', 'Popularity': 5.7578, 'Rating': 7.004, 'credit_id': '52fe4281c3a36847f802425d', 'character': 'Madmartigan', 'job': '', 'department': '', 'Votes': 2132, 'User_Rating': '', 'year': '1988', 'genre': 'Fantasy / Adventure / Action', 'Premiered': '1988-05-20', 'poster': 'https://image.tmdb.org/t/p/w500/pAIRGMIdN7ZdZhflazdV2ezuJ9f.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/pAIRGMIdN7ZdZhflazdV2ezuJ9f.jpg', 'original': 'https://image.tmdb.org/t/p/original/3sF6AibdbTTkswfSRxXEGCt5w6s.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/pAIRGMIdN7ZdZhflazdV2ezuJ9f.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/pAIRGMIdN7ZdZhflazdV2ezuJ9f.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/3sF6AibdbTTkswfSRxXEGCt5w6s.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/3sF6AibdbTTkswfSRxXEGCt5w6s.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/3sF6AibdbTTkswfSRxXEGCt5w6s.jpg'}, {'title': 'The Ghost and the Darkness', 'Label': 'The Ghost and the Darkness', 'OriginalTitle': 'The Ghost and the Darkness', 'id': '10586', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=10586&year=1996', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Sir Robert Beaumont is behind schedule on a railroad in Africa. Enlisting noted engineer John Henry Patterson to right the ship, Beaumont expects results. Everything seems great until the crew discovers the mutilated corpse of the project's foreman, seemingly killed by a lion. After several more attacks, Patterson calls in famed hunter Charles Remington, who has finally met his match in the bloodthirsty lions.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=10586', 'Popularity': 3.7088, 'Rating': 6.827, 'credit_id': '52fe438d9251416c75014c83', 'character': 'Col. John Henry Patterson', 'job': '', 'department': '', 'Votes': 1129, 'User_Rating': '', 'year': '1996', 'genre': 'Adventure / Thriller / History', 'Premiered': '1996-10-11', 'poster': 'https://image.tmdb.org/t/p/w500/3KEPs6RKlin9pT9fqjtW7MSLC8H.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/3KEPs6RKlin9pT9fqjtW7MSLC8H.jpg', 'original': 'https://image.tmdb.org/t/p/original/kM2RkLCt3ElQ2NfHgw1CzZXRGfZ.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/3KEPs6RKlin9pT9fqjtW7MSLC8H.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/3KEPs6RKlin9pT9fqjtW7MSLC8H.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/kM2RkLCt3ElQ2NfHgw1CzZXRGfZ.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/kM2RkLCt3ElQ2NfHgw1CzZXRGfZ.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/kM2RkLCt3ElQ2NfHgw1CzZXRGfZ.jpg'}, {'title': 'Alexander', 'Label': 'Alexander', 'OriginalTitle': 'Alexander', 'id': '1966', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1966&year=2004', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Alexander, the King of Macedonia, leads his legions against the giant Persian Empire. After defeating the Persians, he leads his army across the then known world, venturing farther than any westerner had ever gone, all the way to India.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1966', 'Popularity': 6.9788, 'Rating': 5.953, 'credit_id': '52fe4327c3a36847f803e463', 'character': 'Philip', 'job': '', 'department': '', 'Votes': 3475, 'User_Rating': '', 'year': '2004', 'genre': 'War / History / Action / Adventure / Drama / Romance', 'Premiered': '2004-11-21', 'poster': 'https://image.tmdb.org/t/p/w500/jrwQu72sGwGqwE8Ijne89PSIvhp.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/jrwQu72sGwGqwE8Ijne89PSIvhp.jpg', 'original': 'https://image.tmdb.org/t/p/original/h21dxRjtR7xOhyZljtSYeTETCht.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/jrwQu72sGwGqwE8Ijne89PSIvhp.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/jrwQu72sGwGqwE8Ijne89PSIvhp.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/h21dxRjtR7xOhyZljtSYeTETCht.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/h21dxRjtR7xOhyZljtSYeTETCht.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/h21dxRjtR7xOhyZljtSYeTETCht.jpg'}, {'title': 'The Steam Experiment', 'Label': 'The Steam Experiment', 'OriginalTitle': 'The Steam Experiment', 'id': '20047', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=20047&year=2009', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A deranged scientist locks 6 people in a steam room and threatens to turn up the heat if the local paper doesn't publish his story about global warming.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=20047', 'Popularity': 0.9999, 'Rating': 4.2, 'credit_id': '52fe43d4c3a368484e000a2b', 'character': 'Jimmy', 'job': '', 'department': '', 'Votes': 61, 'User_Rating': '', 'year': '2009', 'genre': 'Crime / Drama / Thriller', 'Premiered': '2009-05-01', 'poster': 'https://image.tmdb.org/t/p/w500/vUfeNA0jLH0Q0TCWOziDtLfxQxA.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/vUfeNA0jLH0Q0TCWOziDtLfxQxA.jpg', 'original': 'https://image.tmdb.org/t/p/original/1z25GGl5ontXQwltr9fNdAow3j.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/vUfeNA0jLH0Q0TCWOziDtLfxQxA.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/vUfeNA0jLH0Q0TCWOziDtLfxQxA.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/1z25GGl5ontXQwltr9fNdAow3j.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/1z25GGl5ontXQwltr9fNdAow3j.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/1z25GGl5ontXQwltr9fNdAow3j.jpg'}, {'title': 'Kiss Kiss Bang Bang', 'Label': 'Kiss Kiss Bang Bang', 'OriginalTitle': 'Kiss Kiss Bang Bang', 'id': '5236', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=5236&year=2005', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A petty thief posing as an actor is brought to Los Angeles for an unlikely audition and finds himself in the middle of a murder investigation along with his high school dream girl and a detective who's been training him for his upcoming role...", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=5236', 'Popularity': 3.9197, 'Rating': 7.161, 'credit_id': '52fe43fec3a36847f807c3b9', 'character': 'Gay Perry', 'job': '', 'department': '', 'Votes': 2974, 'User_Rating': '', 'year': '2005', 'genre': 'Comedy / Crime / Mystery / Thriller', 'Premiered': '2005-09-14', 'poster': 'https://image.tmdb.org/t/p/w500/aWfjIkpENFX6Uw82pET7EQ6jnrd.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/aWfjIkpENFX6Uw82pET7EQ6jnrd.jpg', 'original': 'https://image.tmdb.org/t/p/original/x29PYzoNYPGzdj3M8FDwSwEgNpf.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/aWfjIkpENFX6Uw82pET7EQ6jnrd.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/aWfjIkpENFX6Uw82pET7EQ6jnrd.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/x29PYzoNYPGzdj3M8FDwSwEgNpf.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/x29PYzoNYPGzdj3M8FDwSwEgNpf.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/x29PYzoNYPGzdj3M8FDwSwEgNpf.jpg'}, {'title': 'Spartan', 'Label': 'Spartan', 'OriginalTitle': 'Spartan', 'id': '11169', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=11169&year=2004', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'U.S. government agent Scott is assigned to rescue the daughter of a high-ranking government official. As willing as he is to bend the rules to get things done, though, Scott is shocked to find that others are willing to go even further to protect a political career.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=11169', 'Popularity': 2.2794, 'Rating': 6.2, 'credit_id': '52fe44069251416c750266a1', 'character': 'Scott', 'job': '', 'department': '', 'Votes': 411, 'User_Rating': '', 'year': '2004', 'genre': 'Mystery / Action / Drama / Thriller / Crime', 'Premiered': '2004-03-12', 'poster': 'https://image.tmdb.org/t/p/w500/rcdhS2g1d38NOoeh0PPAN2bLE7w.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/rcdhS2g1d38NOoeh0PPAN2bLE7w.jpg', 'original': 'https://image.tmdb.org/t/p/original/1dm0kjWhYDcVPyBk0CZRThxwNyK.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/rcdhS2g1d38NOoeh0PPAN2bLE7w.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/rcdhS2g1d38NOoeh0PPAN2bLE7w.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/1dm0kjWhYDcVPyBk0CZRThxwNyK.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/1dm0kjWhYDcVPyBk0CZRThxwNyK.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/1dm0kjWhYDcVPyBk0CZRThxwNyK.jpg'}, {'title': 'Delgo', 'Label': 'Delgo', 'OriginalTitle': 'Delgo', 'id': '20542', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=20542&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'In a divided land, it takes a rebellious boy and his clandestine love for a Princess of an opposing race to stop a war orchestrated by a power hungry villain.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=20542', 'Popularity': 2.3213, 'Rating': 4.5, 'credit_id': '52fe43ecc3a368484e0063f9', 'character': 'Bogardus (voice)', 'job': '', 'department': '', 'Votes': 70, 'User_Rating': '', 'year': '2008', 'genre': 'Adventure / Fantasy / Animation / Science Fiction / Family', 'Premiered': '2008-12-12', 'poster': 'https://image.tmdb.org/t/p/w500/wtk430tDLZ0Ql5jCUWCja8qJJQQ.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/wtk430tDLZ0Ql5jCUWCja8qJJQQ.jpg', 'original': 'https://image.tmdb.org/t/p/original/phlfaINv7hOb7oCon3PHidPUHdF.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/wtk430tDLZ0Ql5jCUWCja8qJJQQ.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/wtk430tDLZ0Ql5jCUWCja8qJJQQ.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/phlfaINv7hOb7oCon3PHidPUHdF.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/phlfaINv7hOb7oCon3PHidPUHdF.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/phlfaINv7hOb7oCon3PHidPUHdF.jpg'}, {'title': 'Wonderland', 'Label': 'Wonderland', 'OriginalTitle': 'Wonderland', 'id': '4997', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=4997&year=2003', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'On the afternoon of July 1, 1981, Los Angeles police responded to a distress call on Wonderland Avenue and discovered a grisly quadruple homicide. The police investigation that followed uncovered two versions of the events leading up to the brutal murders - both involving legendary porn actor John Holmes.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=4997', 'Popularity': 2.1097, 'Rating': 6.083, 'credit_id': '52fe43edc3a36847f8078c45', 'character': 'John Holmes', 'job': '', 'department': '', 'Votes': 290, 'User_Rating': '', 'year': '2003', 'genre': 'Crime / Mystery / Drama', 'Premiered': '2003-10-23', 'poster': 'https://image.tmdb.org/t/p/w500/mfG8S7D4rYeVqvTzjc3D36PAK3R.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/mfG8S7D4rYeVqvTzjc3D36PAK3R.jpg', 'original': 'https://image.tmdb.org/t/p/original/jvgbITybzUZN6upjadXa644cwMD.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/mfG8S7D4rYeVqvTzjc3D36PAK3R.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/mfG8S7D4rYeVqvTzjc3D36PAK3R.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/jvgbITybzUZN6upjadXa644cwMD.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/jvgbITybzUZN6upjadXa644cwMD.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/jvgbITybzUZN6upjadXa644cwMD.jpg'}, {'title': 'Hard Cash', 'Label': 'Hard Cash', 'OriginalTitle': 'Hard Cash', 'id': '21106', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=21106&year=2002', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Released from prison, an infamous thief and his new crew pull of a brilliant robbery but then become embroiled with a corrupt FBI agent when they discover the money is marked.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=21106', 'Popularity': 1.7824, 'Rating': 4.6, 'credit_id': '52fe440bc3a368484e00c331', 'character': 'FBI Agent Mark C. Cornell', 'job': '', 'department': '', 'Votes': 70, 'User_Rating': '', 'year': '2002', 'genre': 'Crime / Action / Thriller', 'Premiered': '2002-02-15', 'poster': 'https://image.tmdb.org/t/p/w500/4bRMUS1zhvN1EJcjc1PrVWsauvy.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/4bRMUS1zhvN1EJcjc1PrVWsauvy.jpg', 'original': 'https://image.tmdb.org/t/p/original/iTcADFqn39COatobIUezlMnRcNQ.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/4bRMUS1zhvN1EJcjc1PrVWsauvy.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/4bRMUS1zhvN1EJcjc1PrVWsauvy.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/iTcADFqn39COatobIUezlMnRcNQ.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/iTcADFqn39COatobIUezlMnRcNQ.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/iTcADFqn39COatobIUezlMnRcNQ.jpg'}, {'title': 'Bad Lieutenant: Port of Call New Orleans', 'Label': 'Bad Lieutenant: Port of Call New Orleans', 'OriginalTitle': 'Bad Lieutenant: Port of Call New Orleans', 'id': '11699', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=11699&year=2009', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Terrence McDonagh is a New Orleans Police sergeant, who receives a medal and a promotion to lieutenant for heroism during Hurricane Katrina. Due to his heroic act, McDonagh injures his back and becomes addicted to prescription pain medication. He then finds himself involved with a drug dealer who is suspected of murdering a family of African immigrants.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=11699', 'Popularity': 3.6491, 'Rating': 6.186, 'credit_id': '52fe447b9251416c750365fd', 'character': 'Stevie Pruit', 'job': '', 'department': '', 'Votes': 1249, 'User_Rating': '', 'year': '2009', 'genre': 'Drama / Crime', 'Premiered': '2009-09-11', 'poster': 'https://image.tmdb.org/t/p/w500/zRULXsd0rb1lVfnSyQkYPi2nLcB.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/zRULXsd0rb1lVfnSyQkYPi2nLcB.jpg', 'original': 'https://image.tmdb.org/t/p/original/abF5X1C7KMJEJnbB7KidfHOIszj.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/zRULXsd0rb1lVfnSyQkYPi2nLcB.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/zRULXsd0rb1lVfnSyQkYPi2nLcB.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/abF5X1C7KMJEJnbB7KidfHOIszj.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/abF5X1C7KMJEJnbB7KidfHOIszj.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/abF5X1C7KMJEJnbB7KidfHOIszj.jpg'}, {'title': 'Double Identity', 'Label': 'Double Identity', 'OriginalTitle': 'Double Identity', 'id': '31453', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=31453&year=2009', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'In Chechnya, an American doctor takes a detour in life when he helps a mysterious woman escape from her would-be assailant.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=31453', 'Popularity': 1.5075, 'Rating': 4.8, 'credit_id': '52fe447e9251416c91012bd9', 'character': 'Dr. Nicholas Pinter', 'job': '', 'department': '', 'Votes': 66, 'User_Rating': '', 'year': '2009', 'genre': 'Crime / Thriller', 'Premiered': '2009-12-18', 'poster': 'https://image.tmdb.org/t/p/w500/w9jumrbylMill1LOllH5UBwu0BS.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/w9jumrbylMill1LOllH5UBwu0BS.jpg', 'original': 'https://image.tmdb.org/t/p/original/qKvzxhjGMMiGG0rWKJT6geoASZL.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/w9jumrbylMill1LOllH5UBwu0BS.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/w9jumrbylMill1LOllH5UBwu0BS.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/qKvzxhjGMMiGG0rWKJT6geoASZL.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/qKvzxhjGMMiGG0rWKJT6geoASZL.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/qKvzxhjGMMiGG0rWKJT6geoASZL.jpg'}, {'title': 'Hardwired', 'Label': 'Hardwired', 'OriginalTitle': 'Hardwired', 'id': '24051', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=24051&year=2009', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "After a tragic accident Luke Gibson is left with critical injuries and complete amnesia. A new technological breakthrough from the Hexx Corporation - a Psi-Comp Implant that's hardwired into Luke's brain - saves his life, but Luke soon finds out that this new technology comes with a price and that the Hexx Corporation harbors sinister plans for the new device.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=24051', 'Popularity': 1.8358, 'Rating': 5.1, 'credit_id': '52fe447fc3a368484e02674d', 'character': 'Virgil Kirkhill', 'job': '', 'department': '', 'Votes': 94, 'User_Rating': '', 'year': '2009', 'genre': 'Science Fiction / Adventure / Action / Thriller', 'Premiered': '2009-11-03', 'poster': 'https://image.tmdb.org/t/p/w500/q93fo24fFxruqiHG2VybLengsmb.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/q93fo24fFxruqiHG2VybLengsmb.jpg', 'original': 'https://image.tmdb.org/t/p/original/49HBB4LzWYwfMFMTkralkfJ5niz.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/q93fo24fFxruqiHG2VybLengsmb.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/q93fo24fFxruqiHG2VybLengsmb.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/49HBB4LzWYwfMFMTkralkfJ5niz.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/49HBB4LzWYwfMFMTkralkfJ5niz.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/49HBB4LzWYwfMFMTkralkfJ5niz.jpg'}, {'title': 'The Murders in the Rue Morgue', 'Label': 'The Murders in the Rue Morgue', 'OriginalTitle': 'The Murders in the Rue Morgue', 'id': '6174', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=6174&year=1986', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A detective comes out of retirement to help his daughter's fiance prove that he did not commit a series of murders.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=6174', 'Popularity': 1.3568, 'Rating': 5.9, 'credit_id': '52fe4443c3a36847f808bcc3', 'character': 'Philippe Huron', 'job': '', 'department': '', 'Votes': 36, 'User_Rating': '', 'year': '1986', 'genre': 'Crime / Horror / Mystery / TV Movie', 'Premiered': '1986-12-07', 'poster': 'https://image.tmdb.org/t/p/w500/roGb7CTNwNiRFeJLyJvIEPgz97g.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/roGb7CTNwNiRFeJLyJvIEPgz97g.jpg', 'original': 'https://image.tmdb.org/t/p/original/y9zmtCPXFVVNhlgzPTr7qXA87k7.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/roGb7CTNwNiRFeJLyJvIEPgz97g.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/roGb7CTNwNiRFeJLyJvIEPgz97g.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/y9zmtCPXFVVNhlgzPTr7qXA87k7.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/y9zmtCPXFVVNhlgzPTr7qXA87k7.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/y9zmtCPXFVVNhlgzPTr7qXA87k7.jpg'}, {'title': 'Déjà Vu', 'Label': 'Déjà Vu', 'OriginalTitle': 'Déjà Vu', 'id': '7551', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=7551&year=2006', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Called in to recover evidence in the aftermath of a horrific explosion on a New Orleans ferry, Federal agent Doug Carlin gets pulled away from the scene and taken to a top-secret government lab that uses a time-shifting surveillance device to help prevent crime.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=7551', 'Popularity': 8.9421, 'Rating': 6.876, 'credit_id': '52fe4483c3a36847f809a835', 'character': 'Paul Pryzwarra', 'job': '', 'department': '', 'Votes': 5216, 'User_Rating': '', 'year': '2006', 'genre': 'Action / Thriller / Science Fiction', 'Premiered': '2006-11-22', 'poster': 'https://image.tmdb.org/t/p/w500/eTX6hklzFOiEVqVukNCEedZKhix.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/eTX6hklzFOiEVqVukNCEedZKhix.jpg', 'original': 'https://image.tmdb.org/t/p/original/mhi2fRCbEXtN43FNiq45WQg0DFe.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/eTX6hklzFOiEVqVukNCEedZKhix.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/eTX6hklzFOiEVqVukNCEedZKhix.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/mhi2fRCbEXtN43FNiq45WQg0DFe.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/mhi2fRCbEXtN43FNiq45WQg0DFe.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/mhi2fRCbEXtN43FNiq45WQg0DFe.jpg'}, {'title': 'The Salton Sea', 'Label': 'The Salton Sea', 'OriginalTitle': 'The Salton Sea', 'id': '11468', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=11468&year=2002', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'After the murder of his beloved wife, a man in search of redemption is set adrift in a world where nothing is as it seems. On his journey, he befriends slacker Jimmy "The Finn", becomes involved in rescuing his neighbor Colette from her own demons, and gets entangled in a web of deceit full of unexpected twists and turns.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=11468', 'Popularity': 2.693, 'Rating': 6.581, 'credit_id': '52fe44469251416c7502efbf', 'character': 'Tom Van Allen | Danny Parker', 'job': '', 'department': '', 'Votes': 354, 'User_Rating': '', 'year': '2002', 'genre': 'Crime / Drama / Mystery / Thriller', 'Premiered': '2002-02-12', 'poster': 'https://image.tmdb.org/t/p/w500/i3InMSlLUNBEdQTKazMdyVP1ryX.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/i3InMSlLUNBEdQTKazMdyVP1ryX.jpg', 'original': 'https://image.tmdb.org/t/p/original/mGhz7vE2EvWm6MfFqPJXDidNgAY.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/i3InMSlLUNBEdQTKazMdyVP1ryX.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/i3InMSlLUNBEdQTKazMdyVP1ryX.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/mGhz7vE2EvWm6MfFqPJXDidNgAY.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/mGhz7vE2EvWm6MfFqPJXDidNgAY.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/mGhz7vE2EvWm6MfFqPJXDidNgAY.jpg'}, {'title': 'The Thaw', 'Label': 'The Thaw', 'OriginalTitle': 'The Thaw', 'id': '23410', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=23410&year=2009', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "At a remote Arctic research station, four ecology students discover the real horror of global warming is not the melting ice, but what's frozen within it. A prehistoric parasite is released from the carcass of a Woolly Mammoth upon the unsuspecting students who are forced to quarantine and make necessary sacrifices, or risk infecting the rest of the world.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=23410', 'Popularity': 1.807, 'Rating': 5.7, 'credit_id': '52fe4468c3a368484e021711', 'character': 'Dr. David Kruipen', 'job': '', 'department': '', 'Votes': 347, 'User_Rating': '', 'year': '2009', 'genre': 'Horror / Science Fiction', 'Premiered': '2009-08-30', 'poster': 'https://image.tmdb.org/t/p/w500/6oxJ75L6rB88TeSspcnPA7JqjWw.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/6oxJ75L6rB88TeSspcnPA7JqjWw.jpg', 'original': 'https://image.tmdb.org/t/p/original/5df3793jyBeUQupx0uq1cA6lGF8.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/6oxJ75L6rB88TeSspcnPA7JqjWw.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/6oxJ75L6rB88TeSspcnPA7JqjWw.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/5df3793jyBeUQupx0uq1cA6lGF8.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/5df3793jyBeUQupx0uq1cA6lGF8.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/5df3793jyBeUQupx0uq1cA6lGF8.jpg'}, {'title': 'Kill Me Again', 'Label': 'Kill Me Again', 'OriginalTitle': 'Kill Me Again', 'id': '31583', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=31583&year=1989', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "After Faye and her psychotic boyfriend, Vince, successfully rob a mob courier, Faye decides to abscond with the loot. She heads to Reno, where she hires feckless private investigator Jack Andrews to help fake her death. He pulls the scheme off and sets up Faye with a new identity, only to have her skip out on him without paying. Jack follows her to Vegas and learns he's not the only one after her. Vince has discovered that she's still alive.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=31583', 'Popularity': 1.5131, 'Rating': 6.1, 'credit_id': '52fe448a9251416c910144ef', 'character': 'Jack Andrews', 'job': '', 'department': '', 'Votes': 129, 'User_Rating': '', 'year': '1989', 'genre': 'Drama / Action / Thriller / Crime', 'Premiered': '1989-10-27', 'poster': 'https://image.tmdb.org/t/p/w500/vuYSteL8OqGLXhXfnnBVtxjxyuN.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/vuYSteL8OqGLXhXfnnBVtxjxyuN.jpg', 'original': 'https://image.tmdb.org/t/p/original/7SLDr3SA3NSpl6il6uIhR2VuDrH.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/vuYSteL8OqGLXhXfnnBVtxjxyuN.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/vuYSteL8OqGLXhXfnnBVtxjxyuN.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/7SLDr3SA3NSpl6il6uIhR2VuDrH.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/7SLDr3SA3NSpl6il6uIhR2VuDrH.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/7SLDr3SA3NSpl6il6uIhR2VuDrH.jpg'}, {'title': 'Champion', 'Label': 'Champion', 'OriginalTitle': 'Champion', 'id': '24235', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=24235&year=2005', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Danny Trejo, you know the man. He has fierce tattoos, and frequently plays a thug in your favorite movies. Behind the ink and the wicked characters he plays on screen lies the story of a troubled childhood which included drug addiction, armed robbery and extensive prison time. Champion offers an intimate, one of a kind view into the life of Danny Trejo before he turned himself around and after.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=24235', 'Popularity': 1.1039, 'Rating': 6.4, 'credit_id': '52fe448bc3a368484e028e61', 'character': 'Self', 'job': '', 'department': '', 'Votes': 13, 'User_Rating': '', 'year': '2005', 'genre': 'Documentary', 'Premiered': '2005-03-12', 'poster': 'https://image.tmdb.org/t/p/w500/fUekCoVWHKwjDr9S3TeNZv153p1.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/fUekCoVWHKwjDr9S3TeNZv153p1.jpg', 'original': 'https://image.tmdb.org/t/p/original/fUekCoVWHKwjDr9S3TeNZv153p1.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/fUekCoVWHKwjDr9S3TeNZv153p1.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/fUekCoVWHKwjDr9S3TeNZv153p1.jpg'}, {'title': 'Blind Horizon', 'Label': 'Blind Horizon', 'OriginalTitle': 'Blind Horizon', 'id': '24619', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=24619&year=2003', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Left for dead in the remote Southwest, Frank is found clinging to life and in a state of amnesia. As he recovers, ominous memories begin to flash back...', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=24619', 'Popularity': 1.7119, 'Rating': 5.7, 'credit_id': '52fe44a1c3a368484e02dc71', 'character': 'Frank Kavanaugh', 'job': '', 'department': '', 'Votes': 110, 'User_Rating': '', 'year': '2003', 'genre': 'Thriller', 'Premiered': '2003-12-14', 'poster': 'https://image.tmdb.org/t/p/w500/gmEHqjdjPiFFZnXq0nNV3VUXLS4.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/gmEHqjdjPiFFZnXq0nNV3VUXLS4.jpg', 'original': 'https://image.tmdb.org/t/p/original/goYLxO3gTrAJa2E7Q6r9mBUwaLo.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/gmEHqjdjPiFFZnXq0nNV3VUXLS4.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/gmEHqjdjPiFFZnXq0nNV3VUXLS4.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/goYLxO3gTrAJa2E7Q6r9mBUwaLo.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/goYLxO3gTrAJa2E7Q6r9mBUwaLo.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/goYLxO3gTrAJa2E7Q6r9mBUwaLo.jpg'}, {'title': 'Masked and Anonymous', 'Label': 'Masked and Anonymous', 'OriginalTitle': 'Masked and Anonymous', 'id': '24356', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=24356&year=2003', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A nation wracked with civil war and social unrest anticipates a giant charity concert, organized by deceptive promoter Uncle Sweetheart, who plans on raking in huge sums for himself from the event. Headlining is legendary musician Jack Fate, whose prison time is cut short with Sweetheart's help. Meanwhile, journalist Tom Friend investigates the corrupt concert and sets out to unmask the truth to the public.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=24356', 'Popularity': 1.7472, 'Rating': 5.1, 'credit_id': '52fe4491c3a368484e02a40d', 'character': 'Animal Wrangler', 'job': '', 'department': '', 'Votes': 57, 'User_Rating': '', 'year': '2003', 'genre': 'Drama / Music', 'Premiered': '2003-07-25', 'poster': 'https://image.tmdb.org/t/p/w500/zKxB2Ivm1717Hbnuvvy2lONC4R1.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/zKxB2Ivm1717Hbnuvvy2lONC4R1.jpg', 'original': 'https://image.tmdb.org/t/p/original/9zoo6uzFiewyzQxW9SXcE1ErM23.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/zKxB2Ivm1717Hbnuvvy2lONC4R1.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/zKxB2Ivm1717Hbnuvvy2lONC4R1.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/9zoo6uzFiewyzQxW9SXcE1ErM23.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/9zoo6uzFiewyzQxW9SXcE1ErM23.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/9zoo6uzFiewyzQxW9SXcE1ErM23.jpg'}, {'title': 'Tombstone', 'Label': 'Tombstone', 'OriginalTitle': 'Tombstone', 'id': '11969', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=11969&year=1993', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Legendary marshal Wyatt Earp, now a weary gunfighter, joins his brothers Morgan and Virgil to pursue their collective fortune in the thriving mining town of Tombstone. But Earp is forced to don a badge again and get help from his notorious pal Doc Holliday when a gang of renegade brigands and rustlers begins terrorizing the town.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=11969', 'Popularity': 7.4025, 'Rating': 7.584, 'credit_id': '52fe44ac9251416c7503cfb5', 'character': 'Doc Holliday', 'job': '', 'department': '', 'Votes': 2413, 'User_Rating': '', 'year': '1993', 'genre': 'Western / Action', 'Premiered': '1993-12-25', 'poster': 'https://image.tmdb.org/t/p/w500/wGFCvylul8iEQhJOKfwZGGvXMzA.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/wGFCvylul8iEQhJOKfwZGGvXMzA.jpg', 'original': 'https://image.tmdb.org/t/p/original/djPXXv9pPyTLGl9kMPCTyiBmIA5.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/wGFCvylul8iEQhJOKfwZGGvXMzA.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/wGFCvylul8iEQhJOKfwZGGvXMzA.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/djPXXv9pPyTLGl9kMPCTyiBmIA5.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/djPXXv9pPyTLGl9kMPCTyiBmIA5.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/djPXXv9pPyTLGl9kMPCTyiBmIA5.jpg'}, {'title': 'Played', 'Label': 'Played', 'OriginalTitle': 'Played', 'id': '31979', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=31979&year=2006', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "An examination of the malevolent London underworld with it's despicable criminal underground. Ray (Mick Rossi) just finished an eight year prison sentence after getting set up. Now he is back on the streets to settle the score.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=31979', 'Popularity': 1.197, 'Rating': 3.6, 'credit_id': '52fe44ae9251416c910191a3', 'character': 'Dillon', 'job': '', 'department': '', 'Votes': 19, 'User_Rating': '', 'year': '2006', 'genre': 'Thriller / Crime', 'Premiered': '2006-05-19', 'poster': 'https://image.tmdb.org/t/p/w500/5I8at2uTDCZRSImREtisF0kxdzY.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/5I8at2uTDCZRSImREtisF0kxdzY.jpg', 'original': 'https://image.tmdb.org/t/p/original/gnTrxJs6tuNnZ9AYUFhrZGtD4KM.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/5I8at2uTDCZRSImREtisF0kxdzY.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/5I8at2uTDCZRSImREtisF0kxdzY.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/gnTrxJs6tuNnZ9AYUFhrZGtD4KM.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/gnTrxJs6tuNnZ9AYUFhrZGtD4KM.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/gnTrxJs6tuNnZ9AYUFhrZGtD4KM.jpg'}, {'title': '2:22', 'Label': '2:22', 'OriginalTitle': '2:22', 'id': '25038', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=25038&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The plan was easy; the job was not. On a snowy night a tight crew of four criminals plan to pull off a routine heist. When things go horribly wrong, friendship, loyalty and trust are pushed to the limit.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=25038', 'Popularity': 0.5086, 'Rating': 5.2, 'credit_id': '52fe44b5c3a368484e032807', 'character': 'Maz', 'job': '', 'department': '', 'Votes': 52, 'User_Rating': '', 'year': '2008', 'genre': 'Thriller', 'Premiered': '2008-09-24', 'poster': 'https://image.tmdb.org/t/p/w500/w9Yd4lzYyFpzscvmFJKMPaUHPZq.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/w9Yd4lzYyFpzscvmFJKMPaUHPZq.jpg', 'original': 'https://image.tmdb.org/t/p/original/wEUPeCesbKZpWMuV0eBklOOXc5D.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/w9Yd4lzYyFpzscvmFJKMPaUHPZq.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/w9Yd4lzYyFpzscvmFJKMPaUHPZq.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/wEUPeCesbKZpWMuV0eBklOOXc5D.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/wEUPeCesbKZpWMuV0eBklOOXc5D.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/wEUPeCesbKZpWMuV0eBklOOXc5D.jpg'}, {'title': 'Top Secret!', 'Label': 'Top Secret!', 'OriginalTitle': 'Top Secret!', 'id': '8764', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=8764&year=1984', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Popular and dashing American singer Nick Rivers travels to East Germany to perform in a music festival. When he loses his heart to the gorgeous Hillary Flammond, he finds himself caught up in an underground resistance movement. Rivers joins forces with Agent Cedric and Flammond to attempt the rescue of her father, Dr. Paul, from the Germans, who have captured the scientist in hopes of coercing him into building a new naval mine.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=8764', 'Popularity': 3.659, 'Rating': 7.097, 'credit_id': '52fe44b7c3a36847f80a61b7', 'character': 'Nick Rivers', 'job': '', 'department': '', 'Votes': 1380, 'User_Rating': '', 'year': '1984', 'genre': 'Comedy', 'Premiered': '1984-06-22', 'poster': 'https://image.tmdb.org/t/p/w500/hRTbfR27xghnVMs3ZJ3EhK3zzud.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/hRTbfR27xghnVMs3ZJ3EhK3zzud.jpg', 'original': 'https://image.tmdb.org/t/p/original/yI0xd7X8UktQ6cb8TdWKNTOWxhm.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/hRTbfR27xghnVMs3ZJ3EhK3zzud.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/hRTbfR27xghnVMs3ZJ3EhK3zzud.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/yI0xd7X8UktQ6cb8TdWKNTOWxhm.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/yI0xd7X8UktQ6cb8TdWKNTOWxhm.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/yI0xd7X8UktQ6cb8TdWKNTOWxhm.jpg'}, {'title': 'The Missing', 'Label': 'The Missing', 'OriginalTitle': 'The Missing', 'id': '12146', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=12146&year=2003', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'When rancher and single mother of two Maggie Gilkeson sees her teenage daughter, Lily, kidnapped by Apache rebels, she reluctantly accepts the help of her estranged father, Samuel, in tracking down the kidnappers. Along the way, the two must learn to reconcile the past and work together if they are going to have any hope of getting Lily back before she is taken over the border and forced to become a prostitute.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=12146', 'Popularity': 3.7784, 'Rating': 6.3, 'credit_id': '52fe44be9251416c7503f731', 'character': 'Lt. Jim Ducharme', 'job': '', 'department': '', 'Votes': 683, 'User_Rating': '', 'year': '2003', 'genre': 'Thriller / Western / Adventure', 'Premiered': '2003-11-26', 'poster': 'https://image.tmdb.org/t/p/w500/86s5nw5F1G8lJtEowO0LBB4hoBW.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/86s5nw5F1G8lJtEowO0LBB4hoBW.jpg', 'original': 'https://image.tmdb.org/t/p/original/o8bs4oCB3qCooYfpMhXY4evNVLi.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/86s5nw5F1G8lJtEowO0LBB4hoBW.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/86s5nw5F1G8lJtEowO0LBB4hoBW.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/o8bs4oCB3qCooYfpMhXY4evNVLi.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/o8bs4oCB3qCooYfpMhXY4evNVLi.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/o8bs4oCB3qCooYfpMhXY4evNVLi.jpg'}, {'title': 'Red Planet', 'Label': 'Red Planet', 'OriginalTitle': 'Red Planet', 'id': '8870', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=8870&year=2000', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Astronauts search for solutions to save a dying Earth by searching on Mars, only to have the mission go terribly awry.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=8870', 'Popularity': 3.5249, 'Rating': 5.724, 'credit_id': '52fe44c2c3a36847f80a8605', 'character': 'Robby Gallagher', 'job': '', 'department': '', 'Votes': 1141, 'User_Rating': '', 'year': '2000', 'genre': 'Thriller / Action / Science Fiction', 'Premiered': '2000-11-10', 'poster': 'https://image.tmdb.org/t/p/w500/6svTVlVEJDoOOEz1G09HLeb7vtF.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/6svTVlVEJDoOOEz1G09HLeb7vtF.jpg', 'original': 'https://image.tmdb.org/t/p/original/zZcqSA3vudSPSLHjsvfnGJQpOKe.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/6svTVlVEJDoOOEz1G09HLeb7vtF.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/6svTVlVEJDoOOEz1G09HLeb7vtF.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/zZcqSA3vudSPSLHjsvfnGJQpOKe.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/zZcqSA3vudSPSLHjsvfnGJQpOKe.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/zZcqSA3vudSPSLHjsvfnGJQpOKe.jpg'}, {'title': 'The Love Guru', 'Label': 'The Love Guru', 'OriginalTitle': 'The Love Guru', 'id': '12177', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=12177&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Born in America and raised in an Indian ashram, Pitka returns to his native land to seek his fortune as a spiritualist and self-help expert. His skills are put to the test when he must get a brokenhearted hockey player's marriage back on track in time for the man to help his team win the Stanley Cup.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=12177', 'Popularity': 2.8482, 'Rating': 4.1, 'credit_id': '52fe44c49251416c750404cb', 'character': 'Val Kilmer (uncredited)', 'job': '', 'department': '', 'Votes': 763, 'User_Rating': '', 'year': '2008', 'genre': 'Comedy / Romance', 'Premiered': '2008-06-20', 'poster': 'https://image.tmdb.org/t/p/w500/sp8AV64ftAZCT9uWfgbCb3olGDW.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/sp8AV64ftAZCT9uWfgbCb3olGDW.jpg', 'original': 'https://image.tmdb.org/t/p/original/9E7RHTs5hyVCwZ8vmw0UtrcwfFD.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/sp8AV64ftAZCT9uWfgbCb3olGDW.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/sp8AV64ftAZCT9uWfgbCb3olGDW.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/9E7RHTs5hyVCwZ8vmw0UtrcwfFD.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/9E7RHTs5hyVCwZ8vmw0UtrcwfFD.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/9E7RHTs5hyVCwZ8vmw0UtrcwfFD.jpg'}, {'title': 'Thunderheart', 'Label': 'Thunderheart', 'OriginalTitle': 'Thunderheart', 'id': '12395', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=12395&year=1992', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A young mixed-blood FBI agent is assigned to work with a cynical veteran investigator on a murder on a poverty-stricken Sioux reservation.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=12395', 'Popularity': 2.6603, 'Rating': 6.305, 'credit_id': '52fe44dc9251416c75043755', 'character': 'Ray Levoi', 'job': '', 'department': '', 'Votes': 311, 'User_Rating': '', 'year': '1992', 'genre': 'Crime / Mystery / Thriller', 'Premiered': '1992-04-03', 'poster': 'https://image.tmdb.org/t/p/w500/uGbVd9gzRHk70E8WQPZcjiv6ZLk.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/uGbVd9gzRHk70E8WQPZcjiv6ZLk.jpg', 'original': 'https://image.tmdb.org/t/p/original/ezqMGAZNg1y2b3TPU9jWKUL8rKM.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/uGbVd9gzRHk70E8WQPZcjiv6ZLk.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/uGbVd9gzRHk70E8WQPZcjiv6ZLk.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/ezqMGAZNg1y2b3TPU9jWKUL8rKM.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/ezqMGAZNg1y2b3TPU9jWKUL8rKM.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/ezqMGAZNg1y2b3TPU9jWKUL8rKM.jpg'}, {'title': 'The Traveler', 'Label': 'The Traveler', 'OriginalTitle': 'The Traveler', 'id': '32612', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=32612&year=2010', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "On a dark Christmas Eve in a small town, the lone Sheriffs on the night shift encounter a mysterious man who goes by the name of Mr. Nobody. As the night progresses, the Sheriffs discover that this isn't just a nobody, but a vengeful killer whose past threatens to haunt them all.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=32612', 'Popularity': 1.5782, 'Rating': 5.4, 'credit_id': '52fe44dd9251416c9101f7e7', 'character': 'Mr. Nobody / Drifter', 'job': '', 'department': '', 'Votes': 114, 'User_Rating': '', 'year': '2010', 'genre': 'Horror / Thriller', 'Premiered': '2010-11-15', 'poster': 'https://image.tmdb.org/t/p/w500/7vZ2C66SwastgmQKJ1wC41F2WFK.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/7vZ2C66SwastgmQKJ1wC41F2WFK.jpg', 'original': 'https://image.tmdb.org/t/p/original/dsoIyzH8MSnqh0yK0b9SGcDDzpv.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/7vZ2C66SwastgmQKJ1wC41F2WFK.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/7vZ2C66SwastgmQKJ1wC41F2WFK.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/dsoIyzH8MSnqh0yK0b9SGcDDzpv.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/dsoIyzH8MSnqh0yK0b9SGcDDzpv.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/dsoIyzH8MSnqh0yK0b9SGcDDzpv.jpg'}, {'title': 'The Island of Dr. Moreau', 'Label': 'The Island of Dr. Moreau', 'OriginalTitle': 'The Island of Dr. Moreau', 'id': '9306', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=9306&year=1996', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A plane crash surviving attorney stumbles upon a mysterious island and is shocked to discover that a brilliant scientist and his lab assistant have found a way to combine human and animal DNA—with horrific results.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=9306', 'Popularity': 3.4642, 'Rating': 4.9, 'credit_id': '52fe44e5c3a36847f80b0681', 'character': 'Montgomery', 'job': '', 'department': '', 'Votes': 554, 'User_Rating': '', 'year': '1996', 'genre': 'Science Fiction / Horror', 'Premiered': '1996-08-23', 'poster': 'https://image.tmdb.org/t/p/w500/hOJeQXve8W9rNRhdgC1WV3GQJyA.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/hOJeQXve8W9rNRhdgC1WV3GQJyA.jpg', 'original': 'https://image.tmdb.org/t/p/original/5kAeJB8wR1Be0EFG7QjKdwFfHx7.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/hOJeQXve8W9rNRhdgC1WV3GQJyA.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/hOJeQXve8W9rNRhdgC1WV3GQJyA.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/5kAeJB8wR1Be0EFG7QjKdwFfHx7.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/5kAeJB8wR1Be0EFG7QjKdwFfHx7.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/5kAeJB8wR1Be0EFG7QjKdwFfHx7.jpg'}, {'title': 'Moscow Zero', 'Label': 'Moscow Zero', 'OriginalTitle': 'Moscow Zero', 'id': '25974', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=25974&year=2006', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'In Moscow, the priest Owen hires a team to guide him in the underworld to find his friend Sergei that is missing while researching the legend about the existence of demons and an entrance to hell beneath the city.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=25974', 'Popularity': 1.6564, 'Rating': 3.2, 'credit_id': '52fe44e8c3a368484e03da77', 'character': 'Andrey', 'job': '', 'department': '', 'Votes': 33, 'User_Rating': '', 'year': '2006', 'genre': 'Action / Horror / Drama', 'Premiered': '2006-11-05', 'poster': 'https://image.tmdb.org/t/p/w500/zkQHPAJ4iqC4BlnsQXzcigU0KO.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/zkQHPAJ4iqC4BlnsQXzcigU0KO.jpg', 'original': 'https://image.tmdb.org/t/p/original/eD2npNUJVkVaHq6MD3PVcbIAaAt.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/zkQHPAJ4iqC4BlnsQXzcigU0KO.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/zkQHPAJ4iqC4BlnsQXzcigU0KO.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/eD2npNUJVkVaHq6MD3PVcbIAaAt.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/eD2npNUJVkVaHq6MD3PVcbIAaAt.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/eD2npNUJVkVaHq6MD3PVcbIAaAt.jpg'}, {'title': '10th & Wolf', 'Label': '10th & Wolf', 'OriginalTitle': '10th & Wolf', 'id': '13197', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=13197&year=2006', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A former street thug returns to his Philadelphia home after a stint in the military. Back on his home turf, he once again finds himself tangling with the mob boss who was instrumental in his going off to be a soldier.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=13197', 'Popularity': 1.5555, 'Rating': 5.9, 'credit_id': '52fe454d9251416c75051e53', 'character': 'Murtha', 'job': '', 'department': '', 'Votes': 111, 'User_Rating': '', 'year': '2006', 'genre': 'Action / Crime / Drama / Mystery / Thriller', 'Premiered': '2006-02-19', 'poster': 'https://image.tmdb.org/t/p/w500/2OBZth9rnSyMzZR8M0WwGj8ivDG.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/2OBZth9rnSyMzZR8M0WwGj8ivDG.jpg', 'original': 'https://image.tmdb.org/t/p/original/vzXp9ayYUfSZQVdslIbAqc2MFoS.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/2OBZth9rnSyMzZR8M0WwGj8ivDG.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/2OBZth9rnSyMzZR8M0WwGj8ivDG.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/vzXp9ayYUfSZQVdslIbAqc2MFoS.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/vzXp9ayYUfSZQVdslIbAqc2MFoS.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/vzXp9ayYUfSZQVdslIbAqc2MFoS.jpg'}, {'title': 'Felon', 'Label': 'Felon', 'OriginalTitle': 'Felon', 'id': '13012', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=13012&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A family man convicted of killing an intruder must cope with life afterward in the violent penal system.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=13012', 'Popularity': 4.271, 'Rating': 7.147, 'credit_id': '52fe452f9251416c7504e73b', 'character': 'John Smith', 'job': '', 'department': '', 'Votes': 964, 'User_Rating': '', 'year': '2008', 'genre': 'Crime / Drama / Thriller / Action', 'Premiered': '2008-07-17', 'poster': 'https://image.tmdb.org/t/p/w500/1eYGh6DETJFXQt5PWjV8lp8YZvx.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/1eYGh6DETJFXQt5PWjV8lp8YZvx.jpg', 'original': 'https://image.tmdb.org/t/p/original/k0ACyZCXdqx50464BlE0ZeWR5cu.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/1eYGh6DETJFXQt5PWjV8lp8YZvx.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/1eYGh6DETJFXQt5PWjV8lp8YZvx.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/k0ACyZCXdqx50464BlE0ZeWR5cu.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/k0ACyZCXdqx50464BlE0ZeWR5cu.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/k0ACyZCXdqx50464BlE0ZeWR5cu.jpg'}, {'title': 'Conspiracy', 'Label': 'Conspiracy', 'OriginalTitle': 'Conspiracy', 'id': '13255', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=13255&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A Gulf War veteran with PTSD heads to a small town to find his friend. When he arrives his friend and his family have vanished and the townsfolk afraid to answer questions about their disappearance. He soon discovers that the town is owned and controlled by one man, and he doesn't like people asking questions.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=13255', 'Popularity': 1.5758, 'Rating': 5.4, 'credit_id': '52fe45539251416c75052b4d', 'character': 'MacPherson', 'job': '', 'department': '', 'Votes': 103, 'User_Rating': '', 'year': '2008', 'genre': 'Drama / Action / Thriller / Mystery', 'Premiered': '2008-02-15', 'poster': 'https://image.tmdb.org/t/p/w500/isJpvxaaZd8mHH3E4FFpdExSYEt.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/isJpvxaaZd8mHH3E4FFpdExSYEt.jpg', 'original': 'https://image.tmdb.org/t/p/original/y5g9mSbOpwX9gQk7LG4Lysfh7kA.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/isJpvxaaZd8mHH3E4FFpdExSYEt.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/isJpvxaaZd8mHH3E4FFpdExSYEt.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/y5g9mSbOpwX9gQk7LG4Lysfh7kA.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/y5g9mSbOpwX9gQk7LG4Lysfh7kA.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/y5g9mSbOpwX9gQk7LG4Lysfh7kA.jpg'}, {'title': 'Pollock', 'Label': 'Pollock', 'OriginalTitle': 'Pollock', 'id': '12509', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=12509&year=2000', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'In August of 1949, Life Magazine ran a banner headline that begged the question: "Jackson Pollock: Is he the greatest living painter in the United States?" The film is a look back into the life of an extraordinary man, a man who has fittingly been called "an artist dedicated to concealment, a celebrity who nobody knew." As he struggled with self-doubt, engaging in a lonely tug-of-war between needing to express himself and wanting to shut the world out, Pollock began a downward spiral.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=12509', 'Popularity': 2.205, 'Rating': 6.661, 'credit_id': '52fe44f19251416c75046439', 'character': 'Willem DeKooning', 'job': '', 'department': '', 'Votes': 344, 'User_Rating': '', 'year': '2000', 'genre': 'Drama / History', 'Premiered': '2000-09-06', 'poster': 'https://image.tmdb.org/t/p/w500/azsBSw2zw2uNHiCjTnbe9TJVEDB.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/azsBSw2zw2uNHiCjTnbe9TJVEDB.jpg', 'original': 'https://image.tmdb.org/t/p/original/diLUnClHswIfhpJSjpblvSjWL9U.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/azsBSw2zw2uNHiCjTnbe9TJVEDB.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/azsBSw2zw2uNHiCjTnbe9TJVEDB.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/diLUnClHswIfhpJSjpblvSjWL9U.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/diLUnClHswIfhpJSjpblvSjWL9U.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/diLUnClHswIfhpJSjpblvSjWL9U.jpg'}, {'title': 'The Prince of Egypt', 'Label': 'The Prince of Egypt', 'OriginalTitle': 'The Prince of Egypt', 'id': '9837', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=9837&year=1998', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The strong bond between two Royal Egyptian brothers is challenged when their chosen responsibilities set them at odds, with extraordinary consequences.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=9837', 'Popularity': 14.0513, 'Rating': 7.304, 'credit_id': '52fe4537c3a36847f80c2ab7', 'character': 'Moses (voice)', 'job': '', 'department': '', 'Votes': 4258, 'User_Rating': '', 'year': '1998', 'genre': 'Adventure / Animation / Drama / Family', 'Premiered': '1998-12-16', 'poster': 'https://image.tmdb.org/t/p/w500/2xUjYwL6Ol7TLJPPKs7sYW5PWLX.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/2xUjYwL6Ol7TLJPPKs7sYW5PWLX.jpg', 'original': 'https://image.tmdb.org/t/p/original/565DYYXgdRYMiETLi2EDx4p7s92.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/2xUjYwL6Ol7TLJPPKs7sYW5PWLX.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/2xUjYwL6Ol7TLJPPKs7sYW5PWLX.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/565DYYXgdRYMiETLi2EDx4p7s92.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/565DYYXgdRYMiETLi2EDx4p7s92.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/565DYYXgdRYMiETLi2EDx4p7s92.jpg'}, {'title': 'The Ten Commandments: The Musical', 'Label': 'The Ten Commandments: The Musical', 'OriginalTitle': 'The Ten Commandments: The Musical', 'id': '34164', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=34164&year=2006', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The tale of two brothers, Moses and Ramses: united by love, divided by destiny, they lead their two nations in an epic struggle between slavery and liberty. The Hebrews were slaves in Egypt 3,300 years ago. When Moses, a Hebrew baby raised as a brother to the Egyptian prince, learned of his true origins, he was thrust into a new life, leading his people to freedom.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=34164', 'Popularity': 0.7368, 'Rating': 6.2, 'credit_id': '52fe45589251416c9102f2c3', 'character': 'Moses', 'job': '', 'department': '', 'Votes': 5, 'User_Rating': '', 'year': '2006', 'genre': 'Music', 'Premiered': '2006-01-01', 'poster': 'https://image.tmdb.org/t/p/w500/nrL2X301kTyKj7GLgy4hpkNygI7.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/nrL2X301kTyKj7GLgy4hpkNygI7.jpg', 'original': 'https://image.tmdb.org/t/p/original/1qbkTs9I0MrRPOI60vO2OkULEEz.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/nrL2X301kTyKj7GLgy4hpkNygI7.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/nrL2X301kTyKj7GLgy4hpkNygI7.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/1qbkTs9I0MrRPOI60vO2OkULEEz.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/1qbkTs9I0MrRPOI60vO2OkULEEz.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/1qbkTs9I0MrRPOI60vO2OkULEEz.jpg'}, {'title': 'Dead Girl', 'Label': 'Dead Girl', 'OriginalTitle': 'Dead Girl', 'id': '34646', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=34646&year=1996', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Ari Rose is a failing actor who cannot distinguish between reality and fantasy. He first dreams about and then meets in real life a mysterious woman named Helen. A seemingly mutual obsession ensues, but gradually spirals downward into a web of desire and misperception.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=34646', 'Popularity': 1.2694, 'Rating': 4.4, 'credit_id': '52fe45709251416c9103270f', 'character': 'Dr. Dark', 'job': '', 'department': '', 'Votes': 9, 'User_Rating': '', 'year': '1996', 'genre': 'Comedy', 'Premiered': '1996-09-22', 'poster': 'https://image.tmdb.org/t/p/w500/exjBxTOxdHlnaHObfRErtrsjAtA.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/exjBxTOxdHlnaHObfRErtrsjAtA.jpg', 'original': 'https://image.tmdb.org/t/p/original/p0QyYAfo5CMBJFqqvRmw7ytCV4C.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/exjBxTOxdHlnaHObfRErtrsjAtA.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/exjBxTOxdHlnaHObfRErtrsjAtA.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/p0QyYAfo5CMBJFqqvRmw7ytCV4C.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/p0QyYAfo5CMBJFqqvRmw7ytCV4C.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/p0QyYAfo5CMBJFqqvRmw7ytCV4C.jpg'}, {'title': 'Columbus Day', 'Label': 'Columbus Day', 'OriginalTitle': 'Columbus Day', 'id': '14142', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=14142&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A thief tries to fix the damage done during the biggest heist of his career.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=14142', 'Popularity': 1.5999, 'Rating': 5.0, 'credit_id': '52fe45d09251416c750634d9', 'character': 'John Cologne', 'job': '', 'department': '', 'Votes': 41, 'User_Rating': '', 'year': '2008', 'genre': 'Crime / Drama / Thriller', 'Premiered': '2008-08-29', 'poster': 'https://image.tmdb.org/t/p/w500/cnhz3QCBrX162bJVrcYHRKnYHtB.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/cnhz3QCBrX162bJVrcYHRKnYHtB.jpg', 'original': 'https://image.tmdb.org/t/p/original/nbmNrJOAdj2Ao4b0Pqw5QZ91uLF.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/cnhz3QCBrX162bJVrcYHRKnYHtB.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/cnhz3QCBrX162bJVrcYHRKnYHtB.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/nbmNrJOAdj2Ao4b0Pqw5QZ91uLF.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/nbmNrJOAdj2Ao4b0Pqw5QZ91uLF.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/nbmNrJOAdj2Ao4b0Pqw5QZ91uLF.jpg'}, {'title': 'Have Dreams, Will Travel', 'Label': 'Have Dreams, Will Travel', 'OriginalTitle': 'Have Dreams, Will Travel', 'id': '14552', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=14552&year=2007', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "West Texas, in the 1960's. A tale of two 12-year-olds who embark on an adventure to find new parents in order to escape their unhappy and emotionally unsatisfying family life.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=14552', 'Popularity': 1.4597, 'Rating': 7.591, 'credit_id': '52fe45ff9251416c750699b7', 'character': 'Henderson', 'job': '', 'department': '', 'Votes': 55, 'User_Rating': '', 'year': '2007', 'genre': 'Drama / Romance', 'Premiered': '2007-05-21', 'poster': 'https://image.tmdb.org/t/p/w500/jMHkxZS8HEPbwyskI2KZRLKD4mb.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/jMHkxZS8HEPbwyskI2KZRLKD4mb.jpg', 'original': 'https://image.tmdb.org/t/p/original/1pWZm7nkG6MCBzPagrpPeCEbYQk.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/jMHkxZS8HEPbwyskI2KZRLKD4mb.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/jMHkxZS8HEPbwyskI2KZRLKD4mb.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/1pWZm7nkG6MCBzPagrpPeCEbYQk.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/1pWZm7nkG6MCBzPagrpPeCEbYQk.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/1pWZm7nkG6MCBzPagrpPeCEbYQk.jpg'}, {'title': 'Real Genius', 'Label': 'Real Genius', 'OriginalTitle': 'Real Genius', 'id': '14370', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=14370&year=1985', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'When teenage geniuses Mitch Taylor and Chris Knight, working on an advanced laser project, learn that the military wants to use it as a weapon, they decide to thwart the plan.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=14370', 'Popularity': 3.3801, 'Rating': 6.646, 'credit_id': '52fe45eb9251416c75066ed7', 'character': 'Chris Knight', 'job': '', 'department': '', 'Votes': 493, 'User_Rating': '', 'year': '1985', 'genre': 'Comedy / Romance / Science Fiction', 'Premiered': '1985-08-07', 'poster': 'https://image.tmdb.org/t/p/w500/8az0Tr8hEGDmrUH9WlFz1QIKsMy.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/8az0Tr8hEGDmrUH9WlFz1QIKsMy.jpg', 'original': 'https://image.tmdb.org/t/p/original/5gx3ZkoETzszwhEgdFW6M3roasH.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/8az0Tr8hEGDmrUH9WlFz1QIKsMy.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/8az0Tr8hEGDmrUH9WlFz1QIKsMy.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/5gx3ZkoETzszwhEgdFW6M3roasH.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/5gx3ZkoETzszwhEgdFW6M3roasH.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/5gx3ZkoETzszwhEgdFW6M3roasH.jpg'}, {'title': 'American Meth', 'Label': 'American Meth', 'OriginalTitle': 'American Meth', 'id': '60544', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=60544&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Actor Val Kilmer narrates this powerful film exploring the methamphetamine epidemic that's ravaged blue-collar America. Putting a human face on the problem, filmmaker Justin Hunt reveals the damage being done by this rural drug of choice, as well as the steps being taken by communities across the nation to wipe out the scourge. From Wyoming to New Mexico, Montana and Oregon, American Meth paints a picture of both devastation and hope.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=60544', 'Popularity': 0.7721, 'Rating': 6.6, 'credit_id': '52fe462ac3a368484e0824b5', 'character': 'Narrator', 'job': '', 'department': '', 'Votes': 15, 'User_Rating': '', 'year': '2008', 'genre': 'Documentary', 'Premiered': '2008-02-26'}, {'title': 'At First Sight', 'Label': 'At First Sight', 'OriginalTitle': 'At First Sight', 'id': '15556', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=15556&year=1999', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A blind man has an operation to regain his sight at the urging of his girlfriend and must deal with the changes to his life.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=15556', 'Popularity': 1.6755, 'Rating': 6.0, 'credit_id': '52fe46669251416c75077047', 'character': 'Virgil Adamson', 'job': '', 'department': '', 'Votes': 252, 'User_Rating': '', 'year': '1999', 'genre': 'Drama / Romance', 'Premiered': '1999-01-15', 'poster': 'https://image.tmdb.org/t/p/w500/9nylrKj8zWxTor9BCy3umv6WHZe.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/9nylrKj8zWxTor9BCy3umv6WHZe.jpg', 'original': 'https://image.tmdb.org/t/p/original/4guSmJ5dCX6Y8OFifFVk6Dp9dA6.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/9nylrKj8zWxTor9BCy3umv6WHZe.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/9nylrKj8zWxTor9BCy3umv6WHZe.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/4guSmJ5dCX6Y8OFifFVk6Dp9dA6.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/4guSmJ5dCX6Y8OFifFVk6Dp9dA6.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/4guSmJ5dCX6Y8OFifFVk6Dp9dA6.jpg'}, {'title': 'Stateside', 'Label': 'Stateside', 'OriginalTitle': 'Stateside', 'id': '43670', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=43670&year=2004', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The film follows a rebellious teenager on leave from the Marines who falls in love with a female musician. The relationship is threatened when she develops a mental illness...', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=43670', 'Popularity': 1.3487, 'Rating': 5.0, 'credit_id': '52fe4658c3a36847f80f9e93', 'character': 'Staff Sergeant Skeer', 'job': '', 'department': '', 'Votes': 35, 'User_Rating': '', 'year': '2004', 'genre': 'Drama / Music / Romance', 'Premiered': '2004-05-23', 'poster': 'https://image.tmdb.org/t/p/w500/dPRZpD44rA1ZqgcLjKyVw4fIlgo.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/dPRZpD44rA1ZqgcLjKyVw4fIlgo.jpg', 'original': 'https://image.tmdb.org/t/p/original/4FNhPAjmkStEcZgQzSXyRn1kJwo.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/dPRZpD44rA1ZqgcLjKyVw4fIlgo.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/dPRZpD44rA1ZqgcLjKyVw4fIlgo.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/4FNhPAjmkStEcZgQzSXyRn1kJwo.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/4FNhPAjmkStEcZgQzSXyRn1kJwo.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/4FNhPAjmkStEcZgQzSXyRn1kJwo.jpg'}, {'title': 'American Cowslip', 'Label': 'American Cowslip', 'OriginalTitle': 'American Cowslip', 'id': '44700', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=44700&year=2009', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "In Blythe, California, a small town in the remote California desert, Ethan Inglebrink is an eccentric, agoraphobic heroin addict who is obsessed with his garden. This dark comedy follows the last days of Ethan's life as he struggles to find purpose at a time when it might be too late to even matter.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=44700', 'Popularity': 1.4713, 'Rating': 5.1, 'credit_id': '52fe4698c3a36847f8107675', 'character': 'Todd Inglebrink', 'job': '', 'department': '', 'Votes': 17, 'User_Rating': '', 'year': '2009', 'genre': 'Comedy', 'Premiered': '2009-07-24', 'poster': 'https://image.tmdb.org/t/p/w500/qYJvcQ8Y6C9Q7ocBghwCnNUnEQN.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/qYJvcQ8Y6C9Q7ocBghwCnNUnEQN.jpg', 'original': 'https://image.tmdb.org/t/p/original/cbfPFGAsHach0jhUVDTzUFYj1zY.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/qYJvcQ8Y6C9Q7ocBghwCnNUnEQN.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/qYJvcQ8Y6C9Q7ocBghwCnNUnEQN.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/cbfPFGAsHach0jhUVDTzUFYj1zY.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/cbfPFGAsHach0jhUVDTzUFYj1zY.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/cbfPFGAsHach0jhUVDTzUFYj1zY.jpg'}, {'title': 'MacGruber', 'Label': 'MacGruber', 'OriginalTitle': 'MacGruber', 'id': '37931', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=37931&year=2010', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Ex-special operative MacGruber is called back into action to take down his archenemy, Dieter Von Cunth, who's in possession of a nuclear warhead and bent on destroying Washington, DC.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=37931', 'Popularity': 1.7583, 'Rating': 5.419, 'credit_id': '52fe467f9251416c91056611', 'character': 'Cunth', 'job': '', 'department': '', 'Votes': 600, 'User_Rating': '', 'year': '2010', 'genre': 'Action / Comedy', 'Premiered': '2010-05-21', 'poster': 'https://image.tmdb.org/t/p/w500/1eZEk793evkaIOjBwNO2cFS6h5x.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/1eZEk793evkaIOjBwNO2cFS6h5x.jpg', 'original': 'https://image.tmdb.org/t/p/original/q3ySVO0N9tHw00heI0Wd1B9Qwih.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/1eZEk793evkaIOjBwNO2cFS6h5x.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/1eZEk793evkaIOjBwNO2cFS6h5x.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/q3ySVO0N9tHw00heI0Wd1B9Qwih.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/q3ySVO0N9tHw00heI0Wd1B9Qwih.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/q3ySVO0N9tHw00heI0Wd1B9Qwih.jpg'}, {'title': 'Mindhunters', 'Label': 'Mindhunters', 'OriginalTitle': 'Mindhunters', 'id': '16617', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=16617&year=2004', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Trainees in the FBI's psychological profiling program must put their training into practice when they discover a killer in their midst.  Based very loosely on Agatha Christie's And Then There Were None.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=16617', 'Popularity': 3.9217, 'Rating': 6.452, 'credit_id': '52fe46de9251416c750864ab', 'character': 'Jake Harris', 'job': '', 'department': '', 'Votes': 1301, 'User_Rating': '', 'year': '2004', 'genre': 'Mystery / Thriller / Crime', 'Premiered': '2004-05-07', 'poster': 'https://image.tmdb.org/t/p/w500/uTTGRvnqCI9ZC7WkyP9u7XRiOaA.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/uTTGRvnqCI9ZC7WkyP9u7XRiOaA.jpg', 'original': 'https://image.tmdb.org/t/p/original/eSMrNCvCzRZUhz1mhxpOvgrtvdI.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/uTTGRvnqCI9ZC7WkyP9u7XRiOaA.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/uTTGRvnqCI9ZC7WkyP9u7XRiOaA.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/eSMrNCvCzRZUhz1mhxpOvgrtvdI.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/eSMrNCvCzRZUhz1mhxpOvgrtvdI.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/eSMrNCvCzRZUhz1mhxpOvgrtvdI.jpg'}, {'title': 'Bloodworth', 'Label': 'Bloodworth', 'OriginalTitle': 'Bloodworth', 'id': '67198', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=67198&year=2010', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "E.F. Bloodworth has returned to his home - a forgotten corner of Tennessee - after forty years of roaming. The wife he walked out on has withered and faded, his three sons are grown and angry. Warren is a womanizing alcoholic, Boyd is driven by jealousy to hunt down his wife and her lover, and Brady puts hexes on his enemies from his mamma's porch. Only Fleming, the old man's grandson, treats him with the respect his age commands, and sees past all the hatred to realize the way it can poison a man's soul. It is ultimately the love of Raven Lee, a sloe-eyed beauty from another town, that gives Fleming the courage to reject this family curse.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=67198', 'Popularity': 1.4287, 'Rating': 6.5, 'credit_id': '52fe475cc3a368484e0c2bf3', 'character': 'Warren Bloodworth', 'job': '', 'department': '', 'Votes': 35, 'User_Rating': '', 'year': '2010', 'genre': 'Drama / Romance', 'Premiered': '2010-02-06', 'poster': 'https://image.tmdb.org/t/p/w500/ccaB2iIxZBFiQn4b8AGSmHxPhxC.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/ccaB2iIxZBFiQn4b8AGSmHxPhxC.jpg', 'original': 'https://image.tmdb.org/t/p/original/7tcCCbMR2kF38teW1cC4upWR2KC.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/ccaB2iIxZBFiQn4b8AGSmHxPhxC.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/ccaB2iIxZBFiQn4b8AGSmHxPhxC.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/7tcCCbMR2kF38teW1cC4upWR2KC.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/7tcCCbMR2kF38teW1cC4upWR2KC.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/7tcCCbMR2kF38teW1cC4upWR2KC.jpg'}, {'title': 'Kill the Irishman', 'Label': 'Kill the Irishman', 'OriginalTitle': 'Kill the Irishman', 'id': '51209', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=51209&year=2011', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Over the summer of 1976, thirty-six bombs detonate in the heart of Cleveland while a turf war raged between Irish mobster Danny Greene and the Italian mafia. Based on a true story, Kill the Irishman chronicles Greene's heroic rise from a tough Cleveland neighborhood to become an enforcer in the local mob.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=51209', 'Popularity': 3.0736, 'Rating': 6.777, 'credit_id': '52fe47e7c3a36847f814e71f', 'character': 'Joe Manditski', 'job': '', 'department': '', 'Votes': 693, 'User_Rating': '', 'year': '2011', 'genre': 'Action / Crime / Thriller / Drama', 'Premiered': '2011-03-10', 'poster': 'https://image.tmdb.org/t/p/w500/yjDvqAMyFlesBtWNUUZMgglo78y.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/yjDvqAMyFlesBtWNUUZMgglo78y.jpg', 'original': 'https://image.tmdb.org/t/p/original/7Cam3PU0nCNL0eD7HPxNhnvRggH.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/yjDvqAMyFlesBtWNUUZMgglo78y.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/yjDvqAMyFlesBtWNUUZMgglo78y.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/7Cam3PU0nCNL0eD7HPxNhnvRggH.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/7Cam3PU0nCNL0eD7HPxNhnvRggH.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/7Cam3PU0nCNL0eD7HPxNhnvRggH.jpg'}, {'title': 'Streets of Blood', 'Label': 'Streets of Blood', 'OriginalTitle': 'Streets of Blood', 'id': '19727', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=19727&year=2009', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A police officer's partner has died during Hurricane Katrina, but he later discovers that his partner may have been murdered. An investigation follows, taking the officer and his new partner into the depths of the criminal underworld.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=19727', 'Popularity': 2.1831, 'Rating': 4.3, 'credit_id': '52fe47ed9251416c750aa1c7', 'character': 'Detective Andy Devereaux', 'job': '', 'department': '', 'Votes': 75, 'User_Rating': '', 'year': '2009', 'genre': 'Action / Crime / Drama', 'Premiered': '2009-05-22', 'poster': 'https://image.tmdb.org/t/p/w500/UBLsks7CwsWqYil8PAkzOJauq8.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/UBLsks7CwsWqYil8PAkzOJauq8.jpg', 'original': 'https://image.tmdb.org/t/p/original/rc2U9zz3hNLnb8jcgpUGRwDFdRB.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/UBLsks7CwsWqYil8PAkzOJauq8.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/UBLsks7CwsWqYil8PAkzOJauq8.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/rc2U9zz3hNLnb8jcgpUGRwDFdRB.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/rc2U9zz3hNLnb8jcgpUGRwDFdRB.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/rc2U9zz3hNLnb8jcgpUGRwDFdRB.jpg'}, {'title': '5 Days of War', 'Label': '5 Days of War', 'OriginalTitle': '5 Days of War', 'id': '50601', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=50601&year=2011', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'An American journalist and his cameraman are caught in the combat zone during the first Russian airstrikes against Georgia. Rescuing Tatia, a young Georgian schoolteacher separated from her family during the attack, the two reporters agree to help reunite her with her family in exchange for serving as their interpreter. As the three attempt to escape to safety, they witness--and document--the devastation from the full-scale crossfire and cold-blooded murder of innocent civilians.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=50601', 'Popularity': 2.5257, 'Rating': 5.6, 'credit_id': '52fe47cdc3a36847f81492ad', 'character': 'Dutchman', 'job': '', 'department': '', 'Votes': 209, 'User_Rating': '', 'year': '2011', 'genre': 'War / Drama', 'Premiered': '2011-06-06', 'poster': 'https://image.tmdb.org/t/p/w500/hnMThO1o6zyKAY0C3LUmccVg7SU.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/hnMThO1o6zyKAY0C3LUmccVg7SU.jpg', 'original': 'https://image.tmdb.org/t/p/original/2dnkRdmv7nQxb18X7eXv9uNBA3R.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/hnMThO1o6zyKAY0C3LUmccVg7SU.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/hnMThO1o6zyKAY0C3LUmccVg7SU.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/2dnkRdmv7nQxb18X7eXv9uNBA3R.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/2dnkRdmv7nQxb18X7eXv9uNBA3R.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/2dnkRdmv7nQxb18X7eXv9uNBA3R.jpg'}, {'title': 'Joe the King', 'Label': 'Joe the King', 'OriginalTitle': 'Joe the King', 'id': '53151', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=53151&year=1999', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A destitute 14-year-old struggles to keep his life together despite harsh abuse at his mother's hands, harsher abuse at his father's, and a growing separation from his slightly older brother.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=53151', 'Popularity': 2.1107, 'Rating': 5.9, 'credit_id': '52fe4856c3a36847f8162449', 'character': 'Bob Henry', 'job': '', 'department': '', 'Votes': 45, 'User_Rating': '', 'year': '1999', 'genre': 'Crime / Drama', 'Premiered': '1999-01-22', 'poster': 'https://image.tmdb.org/t/p/w500/pJy18dUA9J9XDuKiboTjEtj6YWL.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/pJy18dUA9J9XDuKiboTjEtj6YWL.jpg', 'original': 'https://image.tmdb.org/t/p/original/eQYgghhQdxlW8hKAab40MhNeOnq.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/pJy18dUA9J9XDuKiboTjEtj6YWL.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/pJy18dUA9J9XDuKiboTjEtj6YWL.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/eQYgghhQdxlW8hKAab40MhNeOnq.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/eQYgghhQdxlW8hKAab40MhNeOnq.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/eQYgghhQdxlW8hKAab40MhNeOnq.jpg'}, {'title': 'Blood Out', 'Label': 'Blood Out', 'OriginalTitle': 'Blood Out', 'id': '54597', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=54597&year=2011', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "When big city detectives refuse to further investigate his kid brother's gang related murder, small town Sheriff Michael Spencer drops the badge and goes undercover to find his brother's killer and avenge his death.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=54597', 'Popularity': 1.5441, 'Rating': 5.252, 'credit_id': '52fe48a5c3a36847f81725af', 'character': 'Arturo', 'job': '', 'department': '', 'Votes': 116, 'User_Rating': '', 'year': '2011', 'genre': 'Action / Thriller', 'Premiered': '2011-04-25', 'poster': 'https://image.tmdb.org/t/p/w500/e7KebNqtudY3zRUSklwf8CqsEn.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/e7KebNqtudY3zRUSklwf8CqsEn.jpg', 'original': 'https://image.tmdb.org/t/p/original/fpSprErzCUH1XzfCyNIxUk4XKS0.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/e7KebNqtudY3zRUSklwf8CqsEn.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/e7KebNqtudY3zRUSklwf8CqsEn.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/fpSprErzCUH1XzfCyNIxUk4XKS0.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/fpSprErzCUH1XzfCyNIxUk4XKS0.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/fpSprErzCUH1XzfCyNIxUk4XKS0.jpg'}, {'title': 'Willow: Behind the Magic', 'Label': 'Willow: Behind the Magic', 'OriginalTitle': 'Willow: Behind the Magic', 'id': '1076366', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1076366&year=2023', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Featuring the breakout stars from the series and returning legends, this documentary takes viewers behind the scenes for an in-depth look at the making of the hit original series.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1076366', 'Popularity': 1.9959, 'Rating': 4.1, 'credit_id': '646bcb6c54a09800e410483b', 'character': 'Self / Madmartigan (archive footage) (uncredited)', 'job': '', 'department': '', 'Votes': 15, 'User_Rating': '', 'year': '2023', 'genre': 'Documentary / Comedy', 'Premiered': '2023-01-25', 'poster': 'https://image.tmdb.org/t/p/w500/AdTxTJQ3ut9tIgBi7J8idi7JMII.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/AdTxTJQ3ut9tIgBi7J8idi7JMII.jpg', 'original': 'https://image.tmdb.org/t/p/original/arOdqPV9ieT4ssXGYbr2VsbJVps.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/AdTxTJQ3ut9tIgBi7J8idi7JMII.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/AdTxTJQ3ut9tIgBi7J8idi7JMII.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/arOdqPV9ieT4ssXGYbr2VsbJVps.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/arOdqPV9ieT4ssXGYbr2VsbJVps.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/arOdqPV9ieT4ssXGYbr2VsbJVps.jpg'}, {'title': '7 Below', 'Label': '7 Below', 'OriginalTitle': '7 Below', 'id': '84577', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=84577&year=2012', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A group of strangers is trapped in a time warp house where a terrible event transpired exactly 100 years prior.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=84577', 'Popularity': 1.799, 'Rating': 3.612, 'credit_id': '52fe48fe9251416c9109f249', 'character': 'McCormick', 'job': '', 'department': '', 'Votes': 94, 'User_Rating': '', 'year': '2012', 'genre': 'Horror', 'Premiered': '2012-04-16', 'poster': 'https://image.tmdb.org/t/p/w500/qP7tRnSpuQngVD7MPnHH3yqewiO.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/qP7tRnSpuQngVD7MPnHH3yqewiO.jpg', 'original': 'https://image.tmdb.org/t/p/original/tRfQHwsFMQZV8pTmxUQywYn6UYf.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/qP7tRnSpuQngVD7MPnHH3yqewiO.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/qP7tRnSpuQngVD7MPnHH3yqewiO.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/tRfQHwsFMQZV8pTmxUQywYn6UYf.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/tRfQHwsFMQZV8pTmxUQywYn6UYf.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/tRfQHwsFMQZV8pTmxUQywYn6UYf.jpg'}, {'title': 'Twixt', 'Label': 'Twixt', 'OriginalTitle': 'Twixt', 'id': '78381', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=78381&year=2011', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A washed-up horror novelist arrives in a sleepy town on a book tour, only to stumble into a string of eerie murders. Haunted by dreams of a ghostly girl named V and guided by the spirit of Edgar Allan Poe, he’s drawn into a nightmarish world where fiction and reality blur—and the story he’s chasing leads back to his own buried guilt.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=78381', 'Popularity': 2.3023, 'Rating': 5.1, 'credit_id': '52fe499bc3a368484e134601', 'character': 'Hall Baltimore', 'job': '', 'department': '', 'Votes': 324, 'User_Rating': '', 'year': '2011', 'genre': 'Mystery / Fantasy / Horror', 'Premiered': '2011-09-10', 'poster': 'https://image.tmdb.org/t/p/w500/jSn7DVovIFeTSiwwoziSYpJFaaS.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/jSn7DVovIFeTSiwwoziSYpJFaaS.jpg', 'original': 'https://image.tmdb.org/t/p/original/6CRHoIGM25wZXpGgQzetmmnALzN.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/jSn7DVovIFeTSiwwoziSYpJFaaS.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/jSn7DVovIFeTSiwwoziSYpJFaaS.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/6CRHoIGM25wZXpGgQzetmmnALzN.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/6CRHoIGM25wZXpGgQzetmmnALzN.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/6CRHoIGM25wZXpGgQzetmmnALzN.jpg'}, {'title': 'Wings of Courage', 'Label': 'Wings of Courage', 'OriginalTitle': 'Wings of Courage', 'id': '78802', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=78802&year=1995', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'In 1930 South America, a small group of French pilots struggle to prove they can offer a reliable airmail service over the Andes. When one of the young pilots crashes on such a flight, he has to try and get back to civilization on foot. Back home, his wife and colleagues start to fear the worst.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=78802', 'Popularity': 1.1027, 'Rating': 6.477, 'credit_id': '52fe49b4c3a368484e13a27d', 'character': 'Jean Mermoz', 'job': '', 'department': '', 'Votes': 22, 'User_Rating': '', 'year': '1995', 'genre': 'Romance / Adventure', 'Premiered': '1995-06-16', 'poster': 'https://image.tmdb.org/t/p/w500/zoxqNb6v55C35DDqNn03Grzhzgr.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/zoxqNb6v55C35DDqNn03Grzhzgr.jpg', 'original': 'https://image.tmdb.org/t/p/original/26cC4TayVw21cUuwSp1rbDsix3l.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/zoxqNb6v55C35DDqNn03Grzhzgr.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/zoxqNb6v55C35DDqNn03Grzhzgr.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/26cC4TayVw21cUuwSp1rbDsix3l.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/26cC4TayVw21cUuwSp1rbDsix3l.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/26cC4TayVw21cUuwSp1rbDsix3l.jpg'}, {'title': 'The Fourth Dimension', 'Label': 'The Fourth Dimension', 'OriginalTitle': 'The Fourth Dimension', 'id': '102858', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=102858&year=2012', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Created under a 'manifesto' whose directives would make Lars von Trier shudder, an anthology is presented that might look on paper like an exercise in forced hipness. Fortunately, its creators – Harmony Korine (USA), Alexsei Fedorchenko (Russia) and Jan Kwiecinski (Poland) – prove innovative and just insane enough to make an exhilarating experiment.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=102858', 'Popularity': 0.7722, 'Rating': 5.5, 'credit_id': '52fe4a12c3a36847f81b743d', 'character': 'Val Kilmer (segment "The Lotus Community Workshop")', 'job': '', 'department': '', 'Votes': 10, 'User_Rating': '', 'year': '2012', 'genre': 'Drama', 'Premiered': '2012-04-24', 'poster': 'https://image.tmdb.org/t/p/w500/4IpnpbERckrIH9kWN8NPOsiavz4.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/4IpnpbERckrIH9kWN8NPOsiavz4.jpg', 'original': 'https://image.tmdb.org/t/p/original/s2rLKxIaraKYqpMvl4gUgB4rpHB.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/4IpnpbERckrIH9kWN8NPOsiavz4.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/4IpnpbERckrIH9kWN8NPOsiavz4.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/s2rLKxIaraKYqpMvl4gUgB4rpHB.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/s2rLKxIaraKYqpMvl4gUgB4rpHB.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/s2rLKxIaraKYqpMvl4gUgB4rpHB.jpg'}, {'title': "Wyatt Earp's Revenge", 'Label': "Wyatt Earp's Revenge", 'OriginalTitle': "Wyatt Earp's Revenge", 'id': '89888', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=89888&year=2012', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Wyatt Earp is approached by a journalist for an interview about how he became a famous sheriff. Earp told the story of how he was a fearless U.S. Marshall. If 27-year old Wyatt Earp comes out that his first girlfriend Dora Hand was murdered. Together with his friend Doc Holliday, Bat Masterson, Bill Tilghman and Charlie Bassett he goes hunting for the perpetrator ...', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=89888', 'Popularity': 0.9735, 'Rating': 4.4, 'credit_id': '52fe4a339251416c910c67c3', 'character': 'Wyatt Earp', 'job': '', 'department': '', 'Votes': 55, 'User_Rating': '', 'year': '2012', 'genre': 'Western / Drama', 'Premiered': '2012-03-06', 'poster': 'https://image.tmdb.org/t/p/w500/m1CQPm1tzzlxRj1nhOfUJ34Mkx.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/m1CQPm1tzzlxRj1nhOfUJ34Mkx.jpg', 'original': 'https://image.tmdb.org/t/p/original/4ORgs4625O97RN6qleN563KdCqL.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/m1CQPm1tzzlxRj1nhOfUJ34Mkx.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/m1CQPm1tzzlxRj1nhOfUJ34Mkx.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/4ORgs4625O97RN6qleN563KdCqL.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/4ORgs4625O97RN6qleN563KdCqL.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/4ORgs4625O97RN6qleN563KdCqL.jpg'}, {'title': 'Breathless', 'Label': 'Breathless', 'OriginalTitle': 'Breathless', 'id': '122930', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=122930&year=2012', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Lorna is a strong-willed Texas woman who’s had enough of her untrustworthy husband, Dale’s, criminal acts and lack of husbandry. Fed up, she enlists the help of her old friend, Tiny, to help her figure out what to do with Dale after his latest double-cross involving the theft of $100,000 from a bank.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=122930', 'Popularity': 1.5157, 'Rating': 5.893, 'credit_id': '52fe4a88c3a368484e158d8b', 'character': 'Dale', 'job': '', 'department': '', 'Votes': 56, 'User_Rating': '', 'year': '2012', 'genre': 'Comedy / Thriller / Mystery / Crime', 'Premiered': '2012-01-04', 'poster': 'https://image.tmdb.org/t/p/w500/eOo4VUHU1qwrAS7xf8PqaMSHj0x.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/eOo4VUHU1qwrAS7xf8PqaMSHj0x.jpg', 'original': 'https://image.tmdb.org/t/p/original/kzjNkzcuhL2uElito95yoOaNkLU.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/eOo4VUHU1qwrAS7xf8PqaMSHj0x.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/eOo4VUHU1qwrAS7xf8PqaMSHj0x.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/kzjNkzcuhL2uElito95yoOaNkLU.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/kzjNkzcuhL2uElito95yoOaNkLU.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/kzjNkzcuhL2uElito95yoOaNkLU.jpg'}, {'title': 'The Seventh Man', 'Label': 'The Seventh Man', 'OriginalTitle': 'The Seventh Man', 'id': '1153674', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1153674&year=2003', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The story chronicles 2 years in the life of the best 6-man football team in Texas, the Panther Creek Panthers.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1153674', 'Popularity': 0.5438, 'Rating': 0.0, 'credit_id': '64b70f85d036b601325a6c7b', 'character': 'Self - Narrator (voice)', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '2003', 'genre': 'Documentary', 'Premiered': '2003-11-01'}, {'title': 'Planes', 'Label': 'Planes', 'OriginalTitle': 'Planes', 'id': '151960', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=151960&year=2013', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Dusty is a cropdusting plane who dreams of competing in a famous aerial race. The problem? He is hopelessly afraid of heights. With the support of his mentor Skipper and a host of new friends, Dusty sets off to make his dreams come true.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=151960', 'Popularity': 4.8011, 'Rating': 5.933, 'credit_id': '52fe4b129251416c910ceef1', 'character': 'Bravo (voice)', 'job': '', 'department': '', 'Votes': 1805, 'User_Rating': '', 'year': '2013', 'genre': 'Animation / Family / Adventure / Comedy', 'Premiered': '2013-08-09', 'poster': 'https://image.tmdb.org/t/p/w500/i2xgU0y0p77WTrB0oIkbpdaWq8R.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/i2xgU0y0p77WTrB0oIkbpdaWq8R.jpg', 'original': 'https://image.tmdb.org/t/p/original/uIIaORh2QoU2a0JokwE9m2vYUm2.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/i2xgU0y0p77WTrB0oIkbpdaWq8R.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/i2xgU0y0p77WTrB0oIkbpdaWq8R.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/uIIaORh2QoU2a0JokwE9m2vYUm2.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/uIIaORh2QoU2a0JokwE9m2vYUm2.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/uIIaORh2QoU2a0JokwE9m2vYUm2.jpg'}, {'title': 'Deep in the Heart', 'Label': 'Deep in the Heart', 'OriginalTitle': 'Deep in the Heart', 'id': '136490', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=136490&year=2012', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'An alcoholic man refocuses himself on putting kids through college via 4H and FFA scholarship donations. Guiding him is a spiritual figure he calls "The Bearded Man".', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=136490', 'Popularity': 0.954, 'Rating': 5.3, 'credit_id': '52fe4c17c3a368484e1a695b', 'character': 'The Bearded Man', 'job': '', 'department': '', 'Votes': 17, 'User_Rating': '', 'year': '2012', 'genre': 'Drama', 'Premiered': '2012-01-01', 'poster': 'https://image.tmdb.org/t/p/w500/pbkTRMvJbQnR17k0xaK7KPyrZ5l.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/pbkTRMvJbQnR17k0xaK7KPyrZ5l.jpg', 'original': 'https://image.tmdb.org/t/p/original/vlTANwIb1gjhkaEYZc451tCfiB6.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/pbkTRMvJbQnR17k0xaK7KPyrZ5l.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/pbkTRMvJbQnR17k0xaK7KPyrZ5l.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/vlTANwIb1gjhkaEYZc451tCfiB6.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/vlTANwIb1gjhkaEYZc451tCfiB6.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/vlTANwIb1gjhkaEYZc451tCfiB6.jpg'}, {'title': 'Palo Alto', 'Label': 'Palo Alto', 'OriginalTitle': 'Palo Alto', 'id': '192132', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=192132&year=2014', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A lack of parental guidance encourages teens in an affluent California town to rebel with substance abuse and casual sex.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=192132', 'Popularity': 2.9607, 'Rating': 6.1, 'credit_id': '52fe4c9c9251416c910fa6c9', 'character': 'Stewart', 'job': '', 'department': '', 'Votes': 910, 'User_Rating': '', 'year': '2014', 'genre': 'Drama', 'Premiered': '2014-05-09', 'poster': 'https://image.tmdb.org/t/p/w500/yjcwwYP3eSigxLKKVBoVVz85ZWv.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/yjcwwYP3eSigxLKKVBoVVz85ZWv.jpg', 'original': 'https://image.tmdb.org/t/p/original/1CbxtdiBSBnihJh5F4nG4sH868L.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/yjcwwYP3eSigxLKKVBoVVz85ZWv.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/yjcwwYP3eSigxLKKVBoVVz85ZWv.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/1CbxtdiBSBnihJh5F4nG4sH868L.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/1CbxtdiBSBnihJh5F4nG4sH868L.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/1CbxtdiBSBnihJh5F4nG4sH868L.jpg'}, {'title': 'Riddle', 'Label': 'Riddle', 'OriginalTitle': 'Riddle', 'id': '170194', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=170194&year=2013', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Holly &amp; Nathan Teller live in a small town in Pennsylvania. Holly is on the cheerleading team and has a close relationship with her younger brother Nathan, who is subjected to bullying at school.  Nathan is taken for a car ride one day by the bullies, whose intent about what they are going to do with Nathan is not clear. He gives them the slip, but disappears and is still missing after three years.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=170194', 'Popularity': 1.5413, 'Rating': 4.6, 'credit_id': '52fe4cf2c3a36847f82463f7', 'character': 'Sheriff Richards', 'job': '', 'department': '', 'Votes': 77, 'User_Rating': '', 'year': '2013', 'genre': 'Mystery / Thriller', 'Premiered': '2013-01-10', 'poster': 'https://image.tmdb.org/t/p/w500/umS2K9OvTLT7Encz4DCPeIlkVmi.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/umS2K9OvTLT7Encz4DCPeIlkVmi.jpg', 'original': 'https://image.tmdb.org/t/p/original/iMY6L1aKXJjBk05IjCkEDWw2Fj1.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/umS2K9OvTLT7Encz4DCPeIlkVmi.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/umS2K9OvTLT7Encz4DCPeIlkVmi.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/iMY6L1aKXJjBk05IjCkEDWw2Fj1.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/iMY6L1aKXJjBk05IjCkEDWw2Fj1.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/iMY6L1aKXJjBk05IjCkEDWw2Fj1.jpg'}, {'title': 'Standing Up', 'Label': 'Standing Up', 'OriginalTitle': 'Standing Up', 'id': '179154', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=179154&year=2013', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Based on one of the most beloved Young Adult novels of all time: Two kids are stripped naked and left together on an island in a lake - victims of a vicious summer camp prank; But rather than have to return to camp and face the humiliation, they decide to take off, on the run together. What follows is a three day odyssey of discovery and self-discovery.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=179154', 'Popularity': 1.4455, 'Rating': 6.7, 'credit_id': '52fe4da2c3a36847f826bd6b', 'character': 'Hofstadder', 'job': '', 'department': '', 'Votes': 70, 'User_Rating': '', 'year': '2013', 'genre': 'Drama', 'Premiered': '2013-08-16', 'poster': 'https://image.tmdb.org/t/p/w500/kOfwxDQ1REdQyZ9lyiBKEqSM6K9.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/kOfwxDQ1REdQyZ9lyiBKEqSM6K9.jpg', 'original': 'https://image.tmdb.org/t/p/original/kfDx5kHAcPUFTrT42VyrjWMqDZy.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/kOfwxDQ1REdQyZ9lyiBKEqSM6K9.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/kOfwxDQ1REdQyZ9lyiBKEqSM6K9.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/kfDx5kHAcPUFTrT42VyrjWMqDZy.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/kfDx5kHAcPUFTrT42VyrjWMqDZy.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/kfDx5kHAcPUFTrT42VyrjWMqDZy.jpg'}, {'title': 'Gun', 'Label': 'Gun', 'OriginalTitle': 'Gun', 'id': '51250', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=51250&year=2010', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The Detroit Police launches a full-scale war against gun runners with the cooperation of the Feds and target a criminal named Rich. When a gun exchange goes bad and Rich’s old friend Angel, steps up big time and saves his life, they form a bond that makes his supplier and lover, Gabriella paranoid. But there is a snitch in the group and Gabriella’s biggest deal goes bad only to have an even bigger secret revealed, one that rocks Rich to his core.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=51250', 'Popularity': 2.056, 'Rating': 5.2, 'credit_id': '53557549c3a368116200017a', 'character': 'Angel', 'job': '', 'department': '', 'Votes': 106, 'User_Rating': '', 'year': '2010', 'genre': 'Action / Crime', 'Premiered': '2010-07-30', 'poster': 'https://image.tmdb.org/t/p/w500/u9dUF1YjDPL5OOlR6GbeYcvu6Q0.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/u9dUF1YjDPL5OOlR6GbeYcvu6Q0.jpg', 'original': 'https://image.tmdb.org/t/p/original/cvHvamW0dggql9Myw894S4xaKEe.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/u9dUF1YjDPL5OOlR6GbeYcvu6Q0.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/u9dUF1YjDPL5OOlR6GbeYcvu6Q0.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/cvHvamW0dggql9Myw894S4xaKEe.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/cvHvamW0dggql9Myw894S4xaKEe.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/cvHvamW0dggql9Myw894S4xaKEe.jpg'}, {'title': 'One Too Many', 'Label': 'One Too Many', 'OriginalTitle': 'One Too Many', 'id': '1198472', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1198472&year=1985', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Four high school friends find their lives changed forever when one of the friends drives drunk with devastating results.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1198472', 'Popularity': 1.0257, 'Rating': 0.0, 'credit_id': '653fcca6c8a5ac011d6e309c', 'character': 'Eric', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '1985', 'genre': 'Drama / Family', 'Premiered': '1985-05-01', 'poster': 'https://image.tmdb.org/t/p/w500/j0FlKcBGQgueg6ZHIeCj7g70gHG.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/j0FlKcBGQgueg6ZHIeCj7g70gHG.jpg', 'original': 'https://image.tmdb.org/t/p/original/j0FlKcBGQgueg6ZHIeCj7g70gHG.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/j0FlKcBGQgueg6ZHIeCj7g70gHG.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/j0FlKcBGQgueg6ZHIeCj7g70gHG.jpg'}, {'title': 'Riddle Me This: Why Is Batman Forever?', 'Label': 'Riddle Me This: Why Is Batman Forever?', 'OriginalTitle': 'Riddle Me This: Why Is Batman Forever?', 'id': '294656', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=294656&year=1995', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "How a new director and cast created a new version of Gotham's classic good and bad guys.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=294656', 'Popularity': 1.095, 'Rating': 7.0, 'credit_id': '54224ed0c3a368086e0009a9', 'character': 'Self - Batman', 'job': '', 'department': '', 'Votes': 17, 'User_Rating': '', 'year': '1995', 'genre': 'Documentary / TV Movie', 'Premiered': '1995-06-14', 'poster': 'https://image.tmdb.org/t/p/w500/y3S1f7LuJd6UmndmyVFJ1NVaBwn.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/y3S1f7LuJd6UmndmyVFJ1NVaBwn.jpg', 'original': 'https://image.tmdb.org/t/p/original/2W1uWG6kz42fiPPMKR3llt8tlca.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/y3S1f7LuJd6UmndmyVFJ1NVaBwn.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/y3S1f7LuJd6UmndmyVFJ1NVaBwn.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/2W1uWG6kz42fiPPMKR3llt8tlca.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/2W1uWG6kz42fiPPMKR3llt8tlca.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/2W1uWG6kz42fiPPMKR3llt8tlca.jpg'}, {'title': 'Danger Zone: The Making of Top Gun', 'Label': 'Danger Zone: The Making of Top Gun', 'OriginalTitle': 'Danger Zone: The Making of Top Gun', 'id': '1022047', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1022047&year=2004', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A comprehensive 6-part documentary on the making of "Top Gun" featuring all-new interviews with the cast and crew. Available on Disc 2 of the "Top Gun" 2-Disc Special Collector\'s Edition DVD.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1022047', 'Popularity': 1.2817, 'Rating': 6.0, 'credit_id': '63195ec6880c92007f12e541', 'character': 'Self', 'job': '', 'department': '', 'Votes': 1, 'User_Rating': '', 'year': '2004', 'genre': 'Documentary', 'Premiered': '2004-05-10', 'poster': 'https://image.tmdb.org/t/p/w500/fhjM1vsPfjIzHsIC2GE1w5RcfCP.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/fhjM1vsPfjIzHsIC2GE1w5RcfCP.jpg', 'original': 'https://image.tmdb.org/t/p/original/r0OGNs8auphBzrUK4ZkdSyHSZGy.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/fhjM1vsPfjIzHsIC2GE1w5RcfCP.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/fhjM1vsPfjIzHsIC2GE1w5RcfCP.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/r0OGNs8auphBzrUK4ZkdSyHSZGy.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/r0OGNs8auphBzrUK4ZkdSyHSZGy.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/r0OGNs8auphBzrUK4ZkdSyHSZGy.jpg'}, {'title': 'Tom Sawyer & Huckleberry Finn', 'Label': 'Tom Sawyer & Huckleberry Finn', 'OriginalTitle': 'Tom Sawyer & Huckleberry Finn', 'id': '172390', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=172390&year=2014', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Tom Sawyer and his pal Huckleberry Finn have great adventures on the Mississippi River, pretending to be pirates, attending their own funeral and witnessing a murder.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=172390', 'Popularity': 1.0429, 'Rating': 5.5, 'credit_id': '5454f4e1c3a3682be9001d4b', 'character': 'Mark Twain', 'job': '', 'department': '', 'Votes': 39, 'User_Rating': '', 'year': '2014', 'genre': 'Family / Action / Adventure / Drama', 'Premiered': '2014-10-23', 'poster': 'https://image.tmdb.org/t/p/w500/sUkYVwtZzWj4Rg1LVR4qWY7wAV7.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/sUkYVwtZzWj4Rg1LVR4qWY7wAV7.jpg', 'original': 'https://image.tmdb.org/t/p/original/rH9pV7XodQwP5kU6rIC7SbLwT58.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/sUkYVwtZzWj4Rg1LVR4qWY7wAV7.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/sUkYVwtZzWj4Rg1LVR4qWY7wAV7.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/rH9pV7XodQwP5kU6rIC7SbLwT58.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/rH9pV7XodQwP5kU6rIC7SbLwT58.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/rH9pV7XodQwP5kU6rIC7SbLwT58.jpg'}, {'title': 'Animals', 'Label': 'Animals', 'OriginalTitle': 'Animals', 'id': '1043411', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1043411&year=2016', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A ghostly voice sings about transience while the camera glides past closed curtains, capturing the expressive, lived-in face of a dozing Val Kilmer. Rick Alverson’s disconcerting stroboscopic video editing makes the dozing body twitch. The inner turmoil of a troubled soul and restless memories rise to the surface.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1043411', 'Popularity': 0.4816, 'Rating': 0.0, 'credit_id': '65b0e1712fe2fa01723ccf0a', 'character': '', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '2016', 'genre': 'Music', 'Premiered': '2016-11-16'}, {'title': 'Mon Clown', 'Label': 'Mon Clown', 'OriginalTitle': 'Mon Clown', 'id': '1038901', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1038901&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'fr', 'plot': "Documentary from French TV channel Canal+ about Marion Cotillard's road to the Oscar for her performance as French singer Édith Piaf in the 2007 film 'La Vie en Rose', also featuring behind-the-scenes footage from the film.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1038901', 'Popularity': 1.1085, 'Rating': 7.0, 'credit_id': '63550fde43250f008259ab8e', 'character': 'Self', 'job': '', 'department': '', 'Votes': 2, 'User_Rating': '', 'year': '2008', 'genre': 'Documentary / TV Movie', 'Premiered': '2008-03-14', 'poster': 'https://image.tmdb.org/t/p/w500/Tiiat9lZD3ZRjoj9EbGefEBLBw.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/Tiiat9lZD3ZRjoj9EbGefEBLBw.jpg', 'original': 'https://image.tmdb.org/t/p/original/Tiiat9lZD3ZRjoj9EbGefEBLBw.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/Tiiat9lZD3ZRjoj9EbGefEBLBw.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/Tiiat9lZD3ZRjoj9EbGefEBLBw.jpg'}, {'title': 'Trudell', 'Label': 'Trudell', 'OriginalTitle': 'Trudell', 'id': '33712', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=33712&year=2005', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A chronicle of legendary Native American poet/activist John Trudell's travels, spoken word performances, and politics.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=33712', 'Popularity': 1.5027, 'Rating': 5.4, 'credit_id': '55b361ed9251417364003e81', 'character': 'Self - Actor, Friend', 'job': '', 'department': '', 'Votes': 14, 'User_Rating': '', 'year': '2005', 'genre': 'Documentary', 'Premiered': '2005-01-20', 'poster': 'https://image.tmdb.org/t/p/w500/wffU99OLWTsIPtKQx3JqnepAOs7.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/wffU99OLWTsIPtKQx3JqnepAOs7.jpg', 'original': 'https://image.tmdb.org/t/p/original/wffU99OLWTsIPtKQx3JqnepAOs7.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/wffU99OLWTsIPtKQx3JqnepAOs7.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/wffU99OLWTsIPtKQx3JqnepAOs7.jpg'}, {'title': 'Knight Rider', 'Label': 'Knight Rider', 'OriginalTitle': 'Knight Rider', 'id': '209379', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=209379&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'When a group of ruthless mercenaries kill a reclusive scientist, his creation, a new model of artificially intelligent supercar, escapes to find his daughter and recruit a ex-soldier to thwart them. Pilot for the reboot of the television series Knight Rider.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=209379', 'Popularity': 2.6434, 'Rating': 6.3, 'credit_id': '6638e23acaa508012bf5cce0', 'character': 'K.I.T.T. (voice)', 'job': '', 'department': '', 'Votes': 66, 'User_Rating': '', 'year': '2008', 'genre': 'Science Fiction / TV Movie', 'Premiered': '2008-02-17', 'poster': 'https://image.tmdb.org/t/p/w500/vlclgMqgiMWJxYTpsaROHPrM6j2.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/vlclgMqgiMWJxYTpsaROHPrM6j2.jpg', 'original': 'https://image.tmdb.org/t/p/original/kP9zR8XjhaJSIBrWnCF4cfHOIkJ.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/vlclgMqgiMWJxYTpsaROHPrM6j2.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/vlclgMqgiMWJxYTpsaROHPrM6j2.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/kP9zR8XjhaJSIBrWnCF4cfHOIkJ.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/kP9zR8XjhaJSIBrWnCF4cfHOIkJ.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/kP9zR8XjhaJSIBrWnCF4cfHOIkJ.jpg'}, {'title': "Dead Man's Bounty", 'Label': "Dead Man's Bounty", 'OriginalTitle': "Dead Man's Bounty", 'id': '51051', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=51051&year=2006', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A mysterious loner rides into a small town carrying the body of a sought-after outlaw. But after he gambles his bounty away in a card game with the sheriff, he must devise a scheme to reclaim the dead man.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=51051', 'Popularity': 0.5275, 'Rating': 3.1, 'credit_id': '571cd61192514151b10017cd', 'character': 'The Wanted Man', 'job': '', 'department': '', 'Votes': 10, 'User_Rating': '', 'year': '2006', 'genre': 'Action / Thriller / Western', 'Premiered': '2006-09-12', 'poster': 'https://image.tmdb.org/t/p/w500/c7qK6yY7cMiL1JGMWDRgvn4Y3EK.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/c7qK6yY7cMiL1JGMWDRgvn4Y3EK.jpg', 'original': 'https://image.tmdb.org/t/p/original/davocs2uZsRNvxR7Vsp0lpo04RQ.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/c7qK6yY7cMiL1JGMWDRgvn4Y3EK.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/c7qK6yY7cMiL1JGMWDRgvn4Y3EK.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/davocs2uZsRNvxR7Vsp0lpo04RQ.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/davocs2uZsRNvxR7Vsp0lpo04RQ.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/davocs2uZsRNvxR7Vsp0lpo04RQ.jpg'}, {'title': 'How to Rob a Bank', 'Label': 'How to Rob a Bank', 'OriginalTitle': 'How to Rob a Bank', 'id': '1291143', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1291143&year=2024', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'In this true-crime documentary, a charismatic rebel in 1990s Seattle pulls off an unprecedented string of bank robberies straight out of the movies.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1291143', 'Popularity': 2.0588, 'Rating': 6.689, 'credit_id': '6662dbe63ec796ab7614f91c', 'character': 'Chris Shiherlis (archive footage)', 'job': '', 'department': '', 'Votes': 63, 'User_Rating': '', 'year': '2024', 'genre': 'Documentary / Crime', 'Premiered': '2024-06-04', 'poster': 'https://image.tmdb.org/t/p/w500/vhBQOgig0bXCXIgHHyO8ipG47J9.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/vhBQOgig0bXCXIgHHyO8ipG47J9.jpg', 'original': 'https://image.tmdb.org/t/p/original/yjf0RWXeZ0FyStOD5e0i0KlnBVE.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/vhBQOgig0bXCXIgHHyO8ipG47J9.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/vhBQOgig0bXCXIgHHyO8ipG47J9.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/yjf0RWXeZ0FyStOD5e0i0KlnBVE.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/yjf0RWXeZ0FyStOD5e0i0KlnBVE.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/yjf0RWXeZ0FyStOD5e0i0KlnBVE.jpg'}, {'title': 'Song to Song', 'Label': 'Song to Song', 'OriginalTitle': 'Song to Song', 'id': '330947', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=330947&year=2017', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'In this modern love story set against the Austin, Texas music scene, two entangled couples — struggling songwriters Faye and BV, and music mogul Cook and the waitress whom he ensnares — chase success through a rock ‘n’ roll landscape of seduction and betrayal.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=330947', 'Popularity': 2.9953, 'Rating': 5.481, 'credit_id': '5787d6cf92514131c7001686', 'character': 'Duane', 'job': '', 'department': '', 'Votes': 912, 'User_Rating': '', 'year': '2017', 'genre': 'Romance / Drama', 'Premiered': '2017-03-17', 'poster': 'https://image.tmdb.org/t/p/w500/itmaNi14GyWguTOywZ0mMzyScW9.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/itmaNi14GyWguTOywZ0mMzyScW9.jpg', 'original': 'https://image.tmdb.org/t/p/original/4fj9pWyIA3I2TxXXfXFRfIPbX0a.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/itmaNi14GyWguTOywZ0mMzyScW9.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/itmaNi14GyWguTOywZ0mMzyScW9.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/4fj9pWyIA3I2TxXXfXFRfIPbX0a.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/4fj9pWyIA3I2TxXXfXFRfIPbX0a.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/4fj9pWyIA3I2TxXXfXFRfIPbX0a.jpg'}, {'title': 'The Making of Bad Lieutenant: Port of Call New Orleans', 'Label': 'The Making of Bad Lieutenant: Port of Call New Orleans', 'OriginalTitle': 'The Making of Bad Lieutenant: Port of Call New Orleans', 'id': '1307665', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1307665&year=2010', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Behind the scenes documentary for Werner Herzog's Bad Lieutenant: Port of Call New Orleans. Features interviews and on-set footage.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1307665', 'Popularity': 1.0372, 'Rating': 10.0, 'credit_id': '66769dc9c83eb83e1eb0932f', 'character': 'Himself', 'job': '', 'department': '', 'Votes': 1, 'User_Rating': '', 'year': '2010', 'genre': 'Documentary', 'Premiered': '2010-04-06', 'poster': 'https://image.tmdb.org/t/p/w500/wLSAFK1bsVvDNucKoW49J3y0SiE.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/wLSAFK1bsVvDNucKoW49J3y0SiE.jpg', 'original': 'https://image.tmdb.org/t/p/original/mzttSUFnP8qneHiI6B55uh0Vg4K.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/wLSAFK1bsVvDNucKoW49J3y0SiE.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/wLSAFK1bsVvDNucKoW49J3y0SiE.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/mzttSUFnP8qneHiI6B55uh0Vg4K.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/mzttSUFnP8qneHiI6B55uh0Vg4K.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/mzttSUFnP8qneHiI6B55uh0Vg4K.jpg'}, {'title': 'The Snowman', 'Label': 'The Snowman', 'OriginalTitle': 'The Snowman', 'id': '372343', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=372343&year=2017', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Detective Harry Hole investigates the disappearance of a woman whose pink scarf is found wrapped around an ominous looking snowman.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=372343', 'Popularity': 5.0356, 'Rating': 5.221, 'credit_id': '57e737f6925141395b00c070', 'character': 'Rafto', 'job': '', 'department': '', 'Votes': 2357, 'User_Rating': '', 'year': '2017', 'genre': 'Crime / Thriller / Mystery / Horror', 'Premiered': '2017-08-24', 'poster': 'https://image.tmdb.org/t/p/w500/mKsQ8KMOk0VBX26Ev0Lj6EmfGJu.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/mKsQ8KMOk0VBX26Ev0Lj6EmfGJu.jpg', 'original': 'https://image.tmdb.org/t/p/original/rfBUlspOpxPavxrhkhvzlBlwfD8.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/mKsQ8KMOk0VBX26Ev0Lj6EmfGJu.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/mKsQ8KMOk0VBX26Ev0Lj6EmfGJu.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/rfBUlspOpxPavxrhkhvzlBlwfD8.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/rfBUlspOpxPavxrhkhvzlBlwfD8.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/rfBUlspOpxPavxrhkhvzlBlwfD8.jpg'}, {'title': 'The Man Who Broke 1,000 Chains', 'Label': 'The Man Who Broke 1,000 Chains', 'OriginalTitle': 'The Man Who Broke 1,000 Chains', 'id': '425479', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=425479&year=1987', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The true story of Robert Elliot Burns, the prisoner who, after being sentenced to a Georgia chain gang, attempted two daring escapes.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=425479', 'Popularity': 1.2741, 'Rating': 6.6, 'credit_id': '582c50dfc3a36872cc007972', 'character': 'Robert Elliot Burns / Elliot Roberts', 'job': '', 'department': '', 'Votes': 7, 'User_Rating': '', 'year': '1987', 'genre': 'Drama / TV Movie', 'Premiered': '1987-10-31', 'poster': 'https://image.tmdb.org/t/p/w500/bqwbrVEdrhnw8xsb3qSDoCWLnUb.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/bqwbrVEdrhnw8xsb3qSDoCWLnUb.jpg', 'original': 'https://image.tmdb.org/t/p/original/kSF1cZkT1bV5RaVDxaOT40T4oX3.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/bqwbrVEdrhnw8xsb3qSDoCWLnUb.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/bqwbrVEdrhnw8xsb3qSDoCWLnUb.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/kSF1cZkT1bV5RaVDxaOT40T4oX3.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/kSF1cZkT1bV5RaVDxaOT40T4oX3.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/kSF1cZkT1bV5RaVDxaOT40T4oX3.jpg'}, {'title': 'Billy the Kid', 'Label': 'Billy the Kid', 'OriginalTitle': 'Billy the Kid', 'id': '291385', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=291385&year=1989', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Gore Vidal's historical novel is brought to life in this television production of Turner Network Television's Billy the Kid.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=291385', 'Popularity': 1.2507, 'Rating': 7.1, 'credit_id': '58af82459251411a54002877', 'character': 'William Bonney', 'job': '', 'department': '', 'Votes': 15, 'User_Rating': '', 'year': '1989', 'genre': 'History / Western / TV Movie', 'Premiered': '1989-05-10', 'poster': 'https://image.tmdb.org/t/p/w500/4X69ZORXruvF7QgxWawiANXLlQ2.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/4X69ZORXruvF7QgxWawiANXLlQ2.jpg', 'original': 'https://image.tmdb.org/t/p/original/qrrNXUz48UErPy9zkoVGB7tbg7D.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/4X69ZORXruvF7QgxWawiANXLlQ2.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/4X69ZORXruvF7QgxWawiANXLlQ2.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/qrrNXUz48UErPy9zkoVGB7tbg7D.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/qrrNXUz48UErPy9zkoVGB7tbg7D.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/qrrNXUz48UErPy9zkoVGB7tbg7D.jpg'}, {'title': 'Cinema Twain', 'Label': 'Cinema Twain', 'OriginalTitle': 'Cinema Twain', 'id': '456735', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=456735&year=2016', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Val Kilmer, master of reinvention, becomes Mark Twain, in a funny, moving, contemporary and reflective performance, based on the life of the man who was Samuel Clemens and on his writings as Mark Twain: his thoughts on politics, his family, his faith and God… Twain shows the greatness of his incomparable wit.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=456735', 'Popularity': 0.8323, 'Rating': 7.0, 'credit_id': '591119be9251414e8903b84d', 'character': 'Mark Twain', 'job': '', 'department': '', 'Votes': 1, 'User_Rating': '', 'year': '2016', 'genre': 'Comedy', 'Premiered': '2016-06-30', 'poster': 'https://image.tmdb.org/t/p/w500/atgYsfIH9uGWre4cznTd456GN4A.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/atgYsfIH9uGWre4cznTd456GN4A.jpg', 'original': 'https://image.tmdb.org/t/p/original/8uPwLzu4EH3N3xRt4ofQMdxHOHO.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/atgYsfIH9uGWre4cznTd456GN4A.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/atgYsfIH9uGWre4cznTd456GN4A.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/8uPwLzu4EH3N3xRt4ofQMdxHOHO.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/8uPwLzu4EH3N3xRt4ofQMdxHOHO.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/8uPwLzu4EH3N3xRt4ofQMdxHOHO.jpg'}, {'title': 'George and the Dragon', 'Label': 'George and the Dragon', 'OriginalTitle': 'George and the Dragon', 'id': '5494', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=5494&year=2004', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "In 12th century England, the handsome and noble knight, George, has left the Crusades behind to follow his dream of a peaceful life on his own piece of land. However, in order to obtain his land from the ruling King Edgaar, he must help find the King's missing daughter, Princess Lunna, a quest which sees George drawn into an unexpected battle with the kingdom's last surviving dragon.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=5494', 'Popularity': 1.6171, 'Rating': 5.5, 'credit_id': '590b23a8c3a36843c30144cb', 'character': 'El Cabillo (uncredited)', 'job': '', 'department': '', 'Votes': 97, 'User_Rating': '', 'year': '2004', 'genre': 'Adventure', 'Premiered': '2004-03-28', 'poster': 'https://image.tmdb.org/t/p/w500/50NxkQexHBoQypzfADEdlxxOlWA.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/50NxkQexHBoQypzfADEdlxxOlWA.jpg', 'original': 'https://image.tmdb.org/t/p/original/lGkxrGlxnUELoZHaRYlXH7eygM0.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/50NxkQexHBoQypzfADEdlxxOlWA.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/50NxkQexHBoQypzfADEdlxxOlWA.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/lGkxrGlxnUELoZHaRYlXH7eygM0.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/lGkxrGlxnUELoZHaRYlXH7eygM0.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/lGkxrGlxnUELoZHaRYlXH7eygM0.jpg'}, {'title': 'Top Gun: Maverick', 'Label': 'Top Gun: Maverick', 'OriginalTitle': 'Top Gun: Maverick', 'id': '361743', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=361743&year=2022', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'After more than thirty years of service as one of the Navy’s top aviators, and dodging the advancement in rank that would ground him, Pete “Maverick” Mitchell finds himself training a detachment of TOP GUN graduates for a specialized mission the likes of which no living pilot has ever seen.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=361743', 'Popularity': 21.6724, 'Rating': 8.152, 'credit_id': '5925e17c9251413b4a01401f', 'character': "Adm. Tom 'Iceman' Kazansky", 'job': '', 'department': '', 'Votes': 10729, 'User_Rating': '', 'year': '2022', 'genre': 'Action / Drama', 'Premiered': '2022-05-21', 'poster': 'https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/62HCnUTziyWcpDaBO2i1DX17ljH.jpg', 'original': 'https://image.tmdb.org/t/p/original/AaV1YIdWKnjAIAOe8UUKBFm327v.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/62HCnUTziyWcpDaBO2i1DX17ljH.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/62HCnUTziyWcpDaBO2i1DX17ljH.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/AaV1YIdWKnjAIAOe8UUKBFm327v.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/AaV1YIdWKnjAIAOe8UUKBFm327v.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/AaV1YIdWKnjAIAOe8UUKBFm327v.jpg'}, {'title': 'Bounty Hunters', 'Label': 'Bounty Hunters', 'OriginalTitle': 'Bounty Hunters', 'id': '462940', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=462940&year=2004', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The first ever documentary film to give the viewer the real inside story on the controversial profession of Bounty Hunting. Narrated by Val Kilmer, the film follows the life of "World Famous Bounty hunter" Leonard Padilla and Robert Dick.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=462940', 'Popularity': 0.5553, 'Rating': 9.3, 'credit_id': '594b8547925141314b00dc30', 'character': 'Himself', 'job': '', 'department': '', 'Votes': 3, 'User_Rating': '', 'year': '2004', 'genre': 'Crime / Documentary', 'Premiered': '2004-10-01', 'poster': 'https://image.tmdb.org/t/p/w500/hJ1rQH5UlzVTkbxohhEW2ec2lUq.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/hJ1rQH5UlzVTkbxohhEW2ec2lUq.jpg', 'original': 'https://image.tmdb.org/t/p/original/hJ1rQH5UlzVTkbxohhEW2ec2lUq.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/hJ1rQH5UlzVTkbxohhEW2ec2lUq.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/hJ1rQH5UlzVTkbxohhEW2ec2lUq.jpg'}, {'title': 'The Super', 'Label': 'The Super', 'OriginalTitle': 'The Super', 'id': '463022', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=463022&year=2018', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A man becomes the superintendent of a large New York City apartment building where people mysteriously go missing.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=463022', 'Popularity': 1.8511, 'Rating': 5.1, 'credit_id': '594c7991c3a36832ca01a759', 'character': 'Walter', 'job': '', 'department': '', 'Votes': 168, 'User_Rating': '', 'year': '2018', 'genre': 'Thriller / Horror', 'Premiered': '2018-11-08', 'poster': 'https://image.tmdb.org/t/p/w500/1No4DWiCA7QiVwz3CghUQ6X8PMJ.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/1No4DWiCA7QiVwz3CghUQ6X8PMJ.jpg', 'original': 'https://image.tmdb.org/t/p/original/1wSYWBqSmy0xCNFD2UWe0PsBu8.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/1No4DWiCA7QiVwz3CghUQ6X8PMJ.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/1No4DWiCA7QiVwz3CghUQ6X8PMJ.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/1wSYWBqSmy0xCNFD2UWe0PsBu8.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/1wSYWBqSmy0xCNFD2UWe0PsBu8.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/1wSYWBqSmy0xCNFD2UWe0PsBu8.jpg'}, {'title': 'A Century of Science Fiction', 'Label': 'A Century of Science Fiction', 'OriginalTitle': 'A Century of Science Fiction', 'id': '367692', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=367692&year=1996', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'American Documentary, narrated by Christopher Lee', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=367692', 'Popularity': 1.5757, 'Rating': 6.9, 'credit_id': '5c9a65130e0a2610e5c222b5', 'character': 'Self', 'job': '', 'department': '', 'Votes': 4, 'User_Rating': '', 'year': '1996', 'genre': 'Documentary', 'Premiered': '1996-01-01', 'poster': 'https://image.tmdb.org/t/p/w500/mEe8z1WHZ6I9VhLiM5qHOOozuUR.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/mEe8z1WHZ6I9VhLiM5qHOOozuUR.jpg', 'original': 'https://image.tmdb.org/t/p/original/mEe8z1WHZ6I9VhLiM5qHOOozuUR.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/mEe8z1WHZ6I9VhLiM5qHOOozuUR.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/mEe8z1WHZ6I9VhLiM5qHOOozuUR.jpg'}, {'title': 'Jay and Silent Bob Reboot', 'Label': 'Jay and Silent Bob Reboot', 'OriginalTitle': 'Jay and Silent Bob Reboot', 'id': '440762', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=440762&year=2019', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Jay and Silent Bob embark on a cross-country mission to stop Hollywood from rebooting a film based on their comic book characters Bluntman and Chronic.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=440762', 'Popularity': 2.6147, 'Rating': 5.666, 'credit_id': '5d31cb876a300b5922ad1c7b', 'character': 'Bluntman', 'job': '', 'department': '', 'Votes': 595, 'User_Rating': '', 'year': '2019', 'genre': 'Comedy / Action / Adventure', 'Premiered': '2019-10-15', 'poster': 'https://image.tmdb.org/t/p/w500/5uGl5lbcpGLTvtLwBMnfRC0Az5u.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/5uGl5lbcpGLTvtLwBMnfRC0Az5u.jpg', 'original': 'https://image.tmdb.org/t/p/original/z7U3MXCHsnIBiYOMXnXZSiapmyc.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/5uGl5lbcpGLTvtLwBMnfRC0Az5u.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/5uGl5lbcpGLTvtLwBMnfRC0Az5u.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/z7U3MXCHsnIBiYOMXnXZSiapmyc.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/z7U3MXCHsnIBiYOMXnXZSiapmyc.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/z7U3MXCHsnIBiYOMXnXZSiapmyc.jpg'}, {'title': 'The Birthday Cake', 'Label': 'The Birthday Cake', 'OriginalTitle': 'The Birthday Cake', 'id': '624481', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=624481&year=2021', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "On the 10th anniversary of his father's death, Giovanni reluctantly accepts the task of bringing a cake to the home of his uncle, a mob boss, for a celebration. Just two hours into the night, Gio's life is forever changed.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=624481', 'Popularity': 1.9301, 'Rating': 5.067, 'credit_id': '5d5ac98f2495ab00172f202c', 'character': 'Uncle Angelo', 'job': '', 'department': '', 'Votes': 60, 'User_Rating': '', 'year': '2021', 'genre': 'Crime / Thriller', 'Premiered': '2021-06-18', 'poster': 'https://image.tmdb.org/t/p/w500/kI3lTv3f24Fzl2kD0sYVCvCOZh2.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/kI3lTv3f24Fzl2kD0sYVCvCOZh2.jpg', 'original': 'https://image.tmdb.org/t/p/original/1eKFWBEGYfAvcMf4Lr8SvmOjaXP.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/kI3lTv3f24Fzl2kD0sYVCvCOZh2.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/kI3lTv3f24Fzl2kD0sYVCvCOZh2.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/1eKFWBEGYfAvcMf4Lr8SvmOjaXP.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/1eKFWBEGYfAvcMf4Lr8SvmOjaXP.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/1eKFWBEGYfAvcMf4Lr8SvmOjaXP.jpg'}, {'title': '1st Born', 'Label': '1st Born', 'OriginalTitle': '1st Born', 'id': '645434', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=645434&year=2019', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Tucker and Hamid are going to be grandfathers for the first time, but only if they can come together long enough to save their first-born grandchild.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=645434', 'Popularity': 0.5974, 'Rating': 5.7, 'credit_id': '5dc154f3f1b5710013ea6440', 'character': 'Biden', 'job': '', 'department': '', 'Votes': 10, 'User_Rating': '', 'year': '2019', 'genre': 'Comedy', 'Premiered': '2019-02-18', 'poster': 'https://image.tmdb.org/t/p/w500/AkBFjCktRSKizuLrSOqAZbmmNzV.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/AkBFjCktRSKizuLrSOqAZbmmNzV.jpg', 'original': 'https://image.tmdb.org/t/p/original/z4Cz2OpTQnlhsA3v3ZUqLy42yeJ.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/AkBFjCktRSKizuLrSOqAZbmmNzV.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/AkBFjCktRSKizuLrSOqAZbmmNzV.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/z4Cz2OpTQnlhsA3v3ZUqLy42yeJ.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/z4Cz2OpTQnlhsA3v3ZUqLy42yeJ.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/z4Cz2OpTQnlhsA3v3ZUqLy42yeJ.jpg'}, {'title': "A Soldier's Revenge", 'Label': "A Soldier's Revenge", 'OriginalTitle': "A Soldier's Revenge", 'id': '695576', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=695576&year=2021', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Haunted by wartime horrors, Civil War soldier-turned-bounty-hunter Frank Connor spends his time post-war polishing off two things: whiskey and fugitives. When two desperate children arrive on his doorstep and enlist his help to find their missing mother, Frank must face his past in order to take down the notorious Major Briggs, with whom he has a score all his own to settle.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=695576', 'Popularity': 1.2083, 'Rating': 5.1, 'credit_id': '5e9e8d9fd05a030019bdfc4b', 'character': 'CJ', 'job': '', 'department': '', 'Votes': 20, 'User_Rating': '', 'year': '2021', 'genre': 'Western', 'Premiered': '2021-03-25', 'poster': 'https://image.tmdb.org/t/p/w500/tJkYXEfM2teq48u3HBcvvjgqIb1.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/tJkYXEfM2teq48u3HBcvvjgqIb1.jpg', 'original': 'https://image.tmdb.org/t/p/original/wVNAjyRdbZgGMOdXrBMDH7L1pEG.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/tJkYXEfM2teq48u3HBcvvjgqIb1.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/tJkYXEfM2teq48u3HBcvvjgqIb1.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/wVNAjyRdbZgGMOdXrBMDH7L1pEG.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/wVNAjyRdbZgGMOdXrBMDH7L1pEG.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/wVNAjyRdbZgGMOdXrBMDH7L1pEG.jpg'}, {'title': 'Paydirt', 'Label': 'Paydirt', 'OriginalTitle': 'Paydirt', 'id': '696002', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=696002&year=2020', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A parolee teams up with his old crew determined to find a buried bag of cash stolen a decade ago from a DEA bust gone bad, while being tracked by a retired Sheriff.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=696002', 'Popularity': 1.4186, 'Rating': 5.7, 'credit_id': '5ea0428ebe4b360021591795', 'character': 'Sheriff Tucker', 'job': '', 'department': '', 'Votes': 75, 'User_Rating': '', 'year': '2020', 'genre': 'Action / Crime / Thriller', 'Premiered': '2020-08-07', 'poster': 'https://image.tmdb.org/t/p/w500/jAGGV80ZO10YcmUJXK7YSBh1yvK.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/jAGGV80ZO10YcmUJXK7YSBh1yvK.jpg', 'original': 'https://image.tmdb.org/t/p/original/3kS42EIs7QL35ML2WNxpqCKg16S.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/jAGGV80ZO10YcmUJXK7YSBh1yvK.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/jAGGV80ZO10YcmUJXK7YSBh1yvK.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/3kS42EIs7QL35ML2WNxpqCKg16S.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/3kS42EIs7QL35ML2WNxpqCKg16S.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/3kS42EIs7QL35ML2WNxpqCKg16S.jpg'}, {'title': 'Willow: The Making of an Adventure', 'Label': 'Willow: The Making of an Adventure', 'OriginalTitle': 'Willow: The Making of an Adventure', 'id': '697921', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=697921&year=1988', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A behind-the-scenes documentary on the making of the film Willow (1988). Included are interviews with cast and crew and scenes of the actual filming of the production itself.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=697921', 'Popularity': 1.3121, 'Rating': 6.8, 'credit_id': '5ea790bd07291c001eea6c9a', 'character': 'Self / Madmartigan', 'job': '', 'department': '', 'Votes': 6, 'User_Rating': '', 'year': '1988', 'genre': 'TV Movie / Documentary', 'Premiered': '1988-04-26', 'poster': 'https://image.tmdb.org/t/p/w500/AktdAcMAXkFqEIcfKTLapjxzzXk.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/AktdAcMAXkFqEIcfKTLapjxzzXk.jpg', 'original': 'https://image.tmdb.org/t/p/original/AktdAcMAXkFqEIcfKTLapjxzzXk.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/AktdAcMAXkFqEIcfKTLapjxzzXk.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/AktdAcMAXkFqEIcfKTLapjxzzXk.jpg'}, {'title': 'Twixt: A Documentary', 'Label': 'Twixt: A Documentary', 'OriginalTitle': 'Twixt: A Documentary', 'id': '240139', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=240139&year=2013', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The making of Francis Ford Coppola\'s "Twixt," directed by his granddaughter Gia.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=240139', 'Popularity': 0.8232, 'Rating': 0.0, 'credit_id': '5ed2271421c4ca001fde6836', 'character': 'Self', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '2013', 'genre': 'Documentary', 'Premiered': '2013-07-23', 'poster': 'https://image.tmdb.org/t/p/w500/f5llU3rlt4XFfWI9shgmw8YIkvY.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/f5llU3rlt4XFfWI9shgmw8YIkvY.jpg', 'original': 'https://image.tmdb.org/t/p/original/f5llU3rlt4XFfWI9shgmw8YIkvY.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/f5llU3rlt4XFfWI9shgmw8YIkvY.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/f5llU3rlt4XFfWI9shgmw8YIkvY.jpg'}, {'title': 'The Doors: The Road of Excess', 'Label': 'The Doors: The Road of Excess', 'OriginalTitle': 'The Doors: The Road of Excess', 'id': '717639', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=717639&year=1997', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Interviews with friends of the late Jim Morrison and several people involved with the making of the film The Doors (1991) by Oliver Stone, delving into what Morrison meant to everyone including themselves.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=717639', 'Popularity': 0.8812, 'Rating': 0.0, 'credit_id': '608f9234871b340029c4045f', 'character': 'Self', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '1997', 'genre': 'Documentary', 'Premiered': '1997-08-14'}, {'title': 'The Prince of Egypt: From Dream to Screen', 'Label': 'The Prince of Egypt: From Dream to Screen', 'OriginalTitle': 'The Prince of Egypt: From Dream to Screen', 'id': '703402', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=703402&year=1999', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The making of The Prince of Egypt (1998).', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=703402', 'Popularity': 1.5246, 'Rating': 6.6, 'credit_id': '60b7fbc06905fb00408799ae', 'character': 'Self (archive footage)', 'job': '', 'department': '', 'Votes': 17, 'User_Rating': '', 'year': '1999', 'genre': 'Documentary', 'Premiered': '1999-09-14', 'poster': 'https://image.tmdb.org/t/p/w500/5fABzD3Ci8KuQcxW8mB3RxedLOU.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/5fABzD3Ci8KuQcxW8mB3RxedLOU.jpg', 'original': 'https://image.tmdb.org/t/p/original/5fABzD3Ci8KuQcxW8mB3RxedLOU.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/5fABzD3Ci8KuQcxW8mB3RxedLOU.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/5fABzD3Ci8KuQcxW8mB3RxedLOU.jpg'}, {'title': 'Val', 'Label': 'Val', 'OriginalTitle': 'Val', 'id': '834027', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=834027&year=2021', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'For over 40 years Val Kilmer, one of Hollywood’s most mercurial and/or misunderstood actors has been documenting his own life and craft through film and video. He has amassed thousands of hours of footage, from 16mm home movies made with his brothers, to time spent in iconic roles for blockbuster movies like Top Gun, The Doors, Tombstone, and Batman Forever. This raw, wildly original and unflinching documentary reveals a life lived to extremes and a heart-filled, sometimes hilarious look at what it means to be an artist and a complex man.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=834027', 'Popularity': 2.7819, 'Rating': 7.215, 'credit_id': '60afc6d88ee49c006dc37a0b', 'character': 'Self', 'job': '', 'department': '', 'Votes': 221, 'User_Rating': '', 'year': '2021', 'genre': 'Documentary', 'Premiered': '2021-07-23', 'poster': 'https://image.tmdb.org/t/p/w500/vWJKmfmjpkFeTbUGep6t7w5TexA.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/vWJKmfmjpkFeTbUGep6t7w5TexA.jpg', 'original': 'https://image.tmdb.org/t/p/original/gV2wSIlNMIUxEArKYrTF2NX4tjb.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/vWJKmfmjpkFeTbUGep6t7w5TexA.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/vWJKmfmjpkFeTbUGep6t7w5TexA.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/gV2wSIlNMIUxEArKYrTF2NX4tjb.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/gV2wSIlNMIUxEArKYrTF2NX4tjb.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/gV2wSIlNMIUxEArKYrTF2NX4tjb.jpg'}, {'title': "Lost Soul: The Doomed Journey of Richard Stanley's Island of Dr. Moreau", 'Label': "Lost Soul: The Doomed Journey of Richard Stanley's Island of Dr. Moreau", 'OriginalTitle': "Lost Soul: The Doomed Journey of Richard Stanley's Island of Dr. Moreau", 'id': '279992', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=279992&year=2014', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'The story of the insane scandals related to the remake of “Island of Dr. Moreau” —originally a novel by H. G. Wells—, which was brought to the big screen in 1996. How director Richard Stanley spent four years developing the project just to find an abrupt end to his work while leading actor Marlon Brando pulled the strings in the shadows. Now for the first time, the living key players recount what really happened and why it all went so spectacularly wrong.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=279992', 'Popularity': 2.1472, 'Rating': 6.7, 'credit_id': '6118e93a2dc44e005c5de32d', 'character': 'Self (archive footage)', 'job': '', 'department': '', 'Votes': 120, 'User_Rating': '', 'year': '2014', 'genre': 'Documentary', 'Premiered': '2014-08-24', 'poster': 'https://image.tmdb.org/t/p/w500/rySKp5esmRPVDMm33mr4szxR6IU.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/rySKp5esmRPVDMm33mr4szxR6IU.jpg', 'original': 'https://image.tmdb.org/t/p/original/37QX7fTizptsUhtUqXasqkNpWX8.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/rySKp5esmRPVDMm33mr4szxR6IU.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/rySKp5esmRPVDMm33mr4szxR6IU.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/37QX7fTizptsUhtUqXasqkNpWX8.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/37QX7fTizptsUhtUqXasqkNpWX8.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/37QX7fTizptsUhtUqXasqkNpWX8.jpg'}, {'title': 'Quentin Tarantino: From a Movie Buff to a Hollywood Legend', 'Label': 'Quentin Tarantino: From a Movie Buff to a Hollywood Legend', 'OriginalTitle': 'Quentin Tarantino: From a Movie Buff to a Hollywood Legend', 'id': '986824', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=986824&year=2021', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Who has ever compared Reservoir Dogs? What are “Open Road” and “New World Disorder”? Why is Harvey Keitel a fairy and how did we all almost become diehard fans of Paul Calderon? Here’s a story about Quentin Tarantino. The director who needs no introduction.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=986824', 'Popularity': 2.8546, 'Rating': 5.0, 'credit_id': '66dce08ed01e5099309661b5', 'character': 'Self (archive footage)', 'job': '', 'department': '', 'Votes': 2, 'User_Rating': '', 'year': '2021', 'genre': 'Documentary', 'Premiered': '2021-01-02'}, {'title': 'The Lotus Community Workshop', 'Label': 'The Lotus Community Workshop', 'OriginalTitle': 'The Lotus Community Workshop', 'id': '1385003', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1385003&year=2012', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A former actor-turned-self-help guru holds a motivational workshop in a skating rink, lives in a mansion and rides BMX bikes with his girlfriend.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1385003', 'Popularity': 0.5938, 'Rating': 0.0, 'credit_id': '672f4c76b8d71b75d6db8f6b', 'character': 'Val Kilmer', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '2012', 'genre': 'Drama / Comedy', 'Premiered': '2012-04-20', 'poster': 'https://image.tmdb.org/t/p/w500/5NtBScBBTU54yEZGLvdyFqREBAw.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/5NtBScBBTU54yEZGLvdyFqREBAw.jpg', 'original': 'https://image.tmdb.org/t/p/original/5NtBScBBTU54yEZGLvdyFqREBAw.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/5NtBScBBTU54yEZGLvdyFqREBAw.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/5NtBScBBTU54yEZGLvdyFqREBAw.jpg'}, {'title': 'The Roadie', 'Label': 'The Roadie', 'OriginalTitle': 'The Roadie', 'id': '919072', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=919072&year=2012', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Tenacious D search for a new roadie when they find one of the most amazing Roadies that has ever toured the roads (Danny McBride)', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=919072', 'Popularity': 1.1612, 'Rating': 6.0, 'credit_id': '675bc8ef4b5280ff0c1bf86c', 'character': '', 'job': '', 'department': '', 'Votes': 1, 'User_Rating': '', 'year': '2012', 'genre': 'Music / Comedy', 'Premiered': '2012-05-09', 'poster': 'https://image.tmdb.org/t/p/w500/ytj4Ecsc8fmlH2RrT0L8021qR4y.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/ytj4Ecsc8fmlH2RrT0L8021qR4y.jpg', 'original': 'https://image.tmdb.org/t/p/original/ytj4Ecsc8fmlH2RrT0L8021qR4y.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/ytj4Ecsc8fmlH2RrT0L8021qR4y.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/ytj4Ecsc8fmlH2RrT0L8021qR4y.jpg'}, {'title': 'Shadows of the Bat: The Cinematic Saga of the Dark Knight', 'Label': 'Shadows of the Bat: The Cinematic Saga of the Dark Knight', 'OriginalTitle': 'Shadows of the Bat: The Cinematic Saga of the Dark Knight', 'id': '1406348', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1406348&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'A 6 part documentary of making of Batman franchise.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1406348', 'Popularity': 1.7078, 'Rating': 0.0, 'credit_id': '6768490a2347d3957890c096', 'character': 'Self', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '2008', 'genre': 'Documentary', 'Premiered': '2008-10-18', 'poster': 'https://image.tmdb.org/t/p/w500/bcwMNsbInmW4PlNb8SIVE07A5NO.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/bcwMNsbInmW4PlNb8SIVE07A5NO.jpg', 'original': 'https://image.tmdb.org/t/p/original/bcwMNsbInmW4PlNb8SIVE07A5NO.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/bcwMNsbInmW4PlNb8SIVE07A5NO.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/bcwMNsbInmW4PlNb8SIVE07A5NO.jpg'}, {'title': "The Making of 'Heat'", 'Label': "The Making of 'Heat'", 'OriginalTitle': "The Making of 'Heat'", 'id': '1006951', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1006951&year=2005', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Behind the scenes documentary on the classic Michael Mann heist film.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1006951', 'Popularity': 1.4027, 'Rating': 5.0, 'credit_id': '67f86da8cce7690230ad4b36', 'character': 'Self', 'job': '', 'department': '', 'Votes': 3, 'User_Rating': '', 'year': '2005', 'genre': 'Documentary', 'Premiered': '2005-02-22', 'poster': 'https://image.tmdb.org/t/p/w500/mkCNIItHw0LNbJusi7NwsXHtQdA.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/mkCNIItHw0LNbJusi7NwsXHtQdA.jpg', 'original': 'https://image.tmdb.org/t/p/original/mkCNIItHw0LNbJusi7NwsXHtQdA.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/mkCNIItHw0LNbJusi7NwsXHtQdA.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/mkCNIItHw0LNbJusi7NwsXHtQdA.jpg'}, {'title': 'Unconquered: Allan Houser and the Legacy of One Apache Family', 'Label': 'Unconquered: Allan Houser and the Legacy of One Apache Family', 'OriginalTitle': 'Unconquered: Allan Houser and the Legacy of One Apache Family', 'id': '1464122', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1464122&year=2008', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'In decades past, Native American artists who wanted to sell to mainstream collectors had little choice but to create predictable, Hollywood-style western scenes. Then came a generation of painters and sculptors led by Allan Houser (or Haozous), a Chiricahua Apache artist with no interest in stereotyped imagery and a belief that his own rich heritage was compatible with modernist ideas and techniques. Narrated by actor Val Kilmer and originally commissioned as part of an exhibit of Houser’s work at the Oklahoma History Center, this program depicts the artist’s tribal ancestry, his rise to regional and national acclaim, and the continuing success of his sons as they expand upon and depart from their father’s achievements. Key works are documented, as is Houser’s tenure at the Santa Fe–based Institute of American Indian Arts.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1464122', 'Popularity': 0.7131, 'Rating': 0.0, 'credit_id': '67fc2774aacf7cfb26996398', 'character': 'Narrator (voice)', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '2008', 'genre': 'Documentary / History', 'Premiered': '2008-10-24', 'poster': 'https://image.tmdb.org/t/p/w500/2J5DPrRqaAgC03QhNIlwXMKe0v0.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/2J5DPrRqaAgC03QhNIlwXMKe0v0.jpg', 'original': 'https://image.tmdb.org/t/p/original/2J5DPrRqaAgC03QhNIlwXMKe0v0.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/2J5DPrRqaAgC03QhNIlwXMKe0v0.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/2J5DPrRqaAgC03QhNIlwXMKe0v0.jpg'}, {'title': 'Biography: Val Kilmer', 'Label': 'Biography: Val Kilmer', 'OriginalTitle': 'Biography: Val Kilmer', 'id': '1476870', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1476870&year=2004', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A&E's Biography of Val Kilmer.", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1476870', 'Popularity': 1.7133, 'Rating': 0.0, 'credit_id': '681abc264800dd8b529f02e3', 'character': 'Self', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '2004', 'genre': 'Documentary / TV Movie', 'Premiered': '2004-11-17', 'poster': 'https://image.tmdb.org/t/p/w500/o3aSGzuDHpsVPtyIwVZ0y6kHPkX.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/o3aSGzuDHpsVPtyIwVZ0y6kHPkX.jpg', 'original': 'https://image.tmdb.org/t/p/original/o3aSGzuDHpsVPtyIwVZ0y6kHPkX.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/o3aSGzuDHpsVPtyIwVZ0y6kHPkX.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/o3aSGzuDHpsVPtyIwVZ0y6kHPkX.jpg'}, {'title': 'Africa Unbottled', 'Label': 'Africa Unbottled', 'OriginalTitle': 'Africa Unbottled', 'id': '1477471', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1477471&year=1998', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': 'Hosted by Val Kilmer, the documentary follows playwright Nicholas Ellenbogen as he travels to remote communities in six different African countries. In each community, the residents have taken an holistic and somewhat controversial approach to managed wildlife care.', 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1477471', 'Popularity': 0.4368, 'Rating': 0.0, 'credit_id': '681c46408783b3db17c1da80', 'character': 'Self / Narrator', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '1998', 'genre': 'Documentary / TV Movie', 'Premiered': '1998-04-19'}, {'title': 'Three Days', 'Label': 'Three Days', 'OriginalTitle': 'Three Days', 'id': '287319', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=287319&year=1999', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "Three Days is a feature film exploring the on-and-off-tour lives of Jane's Addiction. Set predominately on their 1997 'Relapse Tour', this docu-drama weaves audiences throughout the band's legacy in a colorful, fast-paced orgy of gritty backstage drama and rare musical performances", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=287319', 'Popularity': 1.2203, 'Rating': 6.0, 'credit_id': '681dc29b17ad996a4863bca5', 'character': 'Self', 'job': '', 'department': '', 'Votes': 1, 'User_Rating': '', 'year': '1999', 'genre': 'Music / Documentary', 'Premiered': '1999-01-23', 'poster': 'https://image.tmdb.org/t/p/w500/dOJPkYD8H15kZoBVKVP8egUjScH.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/dOJPkYD8H15kZoBVKVP8egUjScH.jpg', 'original': 'https://image.tmdb.org/t/p/original/dOJPkYD8H15kZoBVKVP8egUjScH.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/dOJPkYD8H15kZoBVKVP8egUjScH.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/dOJPkYD8H15kZoBVKVP8egUjScH.jpg'}, {'title': "The Making of 'Tombstone'", 'Label': "The Making of 'Tombstone'", 'OriginalTitle': "The Making of 'Tombstone'", 'id': '1598745', 'imdb_id': '', 'path': 'plugin://script.xtreme_vod?info=xtreme_vod&&id=1598745&year=2002', 'full_url': '', 'stream_id': '', 'media_type': 'movie', 'mediatype': 'movie', 'country': 'en', 'plot': "A Documentary covering the making of the 1993 Western 'Tombstone' featuring cast and crew", 'Trailer': 'plugin://script.xtreme_vod?info=playtrailer&&id=1598745', 'Popularity': 1.3461, 'Rating': 0.0, 'credit_id': '69402e872e2d25fd1c5485ce', 'character': 'Self', 'job': '', 'department': '', 'Votes': 0, 'User_Rating': '', 'year': '2002', 'genre': 'Documentary', 'Premiered': '2002-01-01', 'poster': 'https://image.tmdb.org/t/p/w500/kzP4b9mj9f1B5r1nm3eJ7RAoxbf.jpg', 'poster_original': 'https://image.tmdb.org/t/p/original/kzP4b9mj9f1B5r1nm3eJ7RAoxbf.jpg', 'original': 'https://image.tmdb.org/t/p/original/hp0PwwdliIe003qLza54vUKtF7H.jpg', 'poster_small': 'https://image.tmdb.org/t/p/w342/kzP4b9mj9f1B5r1nm3eJ7RAoxbf.jpg', 'thumb': 'https://image.tmdb.org/t/p/w342/kzP4b9mj9f1B5r1nm3eJ7RAoxbf.jpg', 'fanart': 'https://image.tmdb.org/t/p/w1280/hp0PwwdliIe003qLza54vUKtF7H.jpg', 'fanart_original': 'https://image.tmdb.org/t/p/original/hp0PwwdliIe003qLza54vUKtF7H.jpg', 'fanart_small': 'https://image.tmdb.org/t/p/w780/hp0PwwdliIe003qLza54vUKtF7H.jpg'}]
			#for i in test_list:
			#	Utils.tools_log(i)
			#	imdb_id = get_imdb_id_from_movie_id(movie_id=i['id'])
			#	Utils.tools_log(imdb_id)
			Utils.tools_log(len(test_list))
			Utils.tools_log(len(filter_vod(test_list)))
			

		if info == 'trakt_refresh':
			from resources.lib.trakt_api import refresh_token
			refresh_token()
			Utils.hide_busy()
			return

		if info == 'login_trakt':
			from resources.lib.trakt_api import login_trakt
			login_trakt()
			Utils.hide_busy()
			return

		elif info == 'imdb_list':
			limit = params.get('limit', 0)
			list_name = str(params['list_name'])
			try:
				list_script = str(params['script'])
			except:
				list_script = 'True'
			list_str = str(params['list'])
			Utils.show_busy()
			if 'ls' in str(list_str):

				from resources.lib.TheMovieDB import get_imdb_list_ids
				from resources.lib.TheMovieDB import get_imdb_watchlist_items
				movies = get_imdb_list_ids(list_str,limit=limit)
				if list_script == 'False':
					return get_imdb_watchlist_items(movies=movies,limit=limit,cache_days=1)
				wm.window_stack_empty()
				wm.open_video_list(mode='imdb2', listitems=[], search_str=movies, filter_label=list_name)
			elif 'ur' in str(list_str):
				from resources.lib.TheMovieDB import get_imdb_watchlist_ids
				movies = get_imdb_watchlist_ids(list_str,limit=limit,cache_days=1)
				if list_script == 'False':
					from resources.lib.TheMovieDB import get_imdb_watchlist_items
					return get_imdb_watchlist_items(movies=movies,limit=limit,cache_days=1)
				wm.window_stack_empty()
				wm.open_video_list(mode='imdb2', listitems=[], search_str=movies, filter_label=list_name)
			return

		if info == 'setup_iptv_simple_settings':
			from xtream2m3u_run import setup_iptv_simple_settings
			Utils.show_busy()
			setup_iptv_simple_settings()
			Utils.hide_busy()
			return

		if info == 'output_curr_channels_pastebin':
			from xtream2m3u_run import output_curr_channels_pastebin
			url = output_curr_channels_pastebin()
			dialog = xbmcgui.Dialog()
			dialog.ok('PasteBin Channel List + EPG Group List', url)
			Utils.tools_log(url)
			Utils.hide_busy()
			return

		if info == 'output_lists_pastebin':
			from xtream2m3u_run import output_lists_pastebin
			url = output_lists_pastebin()
			dialog = xbmcgui.Dialog()
			dialog.ok('PasteBin Channel List + EPG Group List', url)
			Utils.tools_log(url)
			Utils.hide_busy()
			return

		if info == 'save_channel_order':
			from xtream2m3u_run import save_channel_order
			dialog = xbmcgui.Dialog()
			url = dialog.input('Enter Channel Order list Pastebin URL', 'https://pastebin.com/',  type=xbmcgui.INPUT_ALPHANUM)
			Utils.show_busy()
			if url != '' and len(url ) > len('https://pastebin.com/'):
				save_channel_order(url)
			Utils.hide_busy()
			return

		if info == 'save_allowed_groups':
			from xtream2m3u_run import save_allowed_groups
			dialog = xbmcgui.Dialog()
			url = dialog.input('Enter Allowed Groups list Pastebin URL', 'https://pastebin.com/',  type=xbmcgui.INPUT_ALPHANUM)
			Utils.show_busy()
			if url != '' and len(url ) > len('https://pastebin.com/'):
				save_allowed_groups(url)
			Utils.hide_busy()
			return

		if info == 'save_exclude_channels':
			from xtream2m3u_run import save_exclude_channels
			dialog = xbmcgui.Dialog()
			url = dialog.input('Enter Exclude Channels list Pastebin URL', 'https://pastebin.com/',  type=xbmcgui.INPUT_ALPHANUM)
			Utils.show_busy()
			if url != '' and len(url ) > len('https://pastebin.com/'):
				save_exclude_channels(url)
			Utils.hide_busy()
			return

		if info == 'delete_db_expired':
			Utils.db_delete_expired(Utils.db_con)
			Utils.hide_busy()
			return

		if info == 'clear_db':
			table_name = params.get('table_name', False)
			Utils.clear_db(Utils.db_con,table_name)
			Utils.hide_busy()
			return

		if info == 'getplayingfile':
			xbmc.log(str(xbmc.Player().getPlayingFile())+'===>OPENINFO', level=xbmc.LOGINFO)
			Utils.hide_busy()
			return

		if info == 'get_trakt_playback':
			from resources.lib import TheMovieDB
			trakt_type = params.get('trakt_type')
			TheMovieDB.get_trakt_playback(trakt_type)
			return

		if info == 'display_dialog':
			next_ep_url = params.get('next_ep_url')
			title = unquote_plus(params.get('title'))
			thumb = params.get('thumb')
			rating = params.get('rating')
			show = params.get('show')
			season = params.get('season')
			episode = params.get('episode')
			year = params.get('year')
			from resources.player import PlayerDialogs
			PlayerDialogs().display_dialog(str(next_ep_url), str(title), str(thumb), str(rating), str(show), str(season), str(episode), str(year))

		elif info == 'xtream2m3u_run':
			Utils.show_busy()
			Utils.hide_busy()
			#from traceback import format_exc
			#from resources.lib.xtream2m3u_run import app as flask_app
			from xtream2m3u_run import start
			#Utils.tools_log('STARTING__SERVER')
			#flask_app.run(debug=False, host='0.0.0.0')
			start()
			Utils.hide_busy()
			return
			#import os
			#Utils.tools_log(os.getcwd())
			#from resources.lib.xtream2m3u_run import generate_m3u
			#generate_m3u()
			#exit()
			#from resources.lib.xtream2m3u_run import app as flask_app
			#from multiprocessing import Process
			#import socket
			#socket.setdefaulttimeout(120) # seconds
			#server = Process(target=flask_app.run(debug=False, host='0.0.0.0'))
			#server.start()
			##flask_app.run(debug=False, host='0.0.0.0')


		elif info == 'allmovies2':
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_watched&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_watched&trakt_type=tv&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_coll&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_coll&trakt_type=tv&script=True)'
			Utils.show_busy()
			media_type = 'movie'
			if info == 'allmovies2':
				from resources.lib.TheMovieDB import get_vod_allmovies
				search_str = get_vod_allmovies()
				filter_label = 'VOD Movies'

				if keep_stack == None or keep_stack == False:
					wm.window_stack_empty()
				return wm.open_video_list(mode='allmovies2', listitems=[], search_str=search_str, media_type=media_type, filter_label=filter_label)

		elif info == 'alltvshows2' or info == 'alltv2':
			Utils.show_busy()
			#log(addon_ID())
			media_type = 'tv'
			if info == 'alltvshows2' or info == 'alltv2':
				from resources.lib.TheMovieDB import get_vod_alltv
				search_str = get_vod_alltv()
				filter_label = 'VOD TV'
				if keep_stack == None or keep_stack == False:
					wm.window_stack_empty()
				return wm.open_video_list(mode='alltvshows2', listitems=[], search_str=search_str, media_type=media_type, filter_label=filter_label)


		elif info == 'calendar_eps':
			search_str = 'Trakt Episodes/Movies in progress'
			from resources.lib.library import trakt_calendar_eps
			#type = 'movie'
			movies = trakt_calendar_eps()
			wm.window_stack_empty()
			trakt_label = 'Trakt Calendar Episodes'
			return wm.open_video_list(mode='trakt', listitems=[], search_str=movies, media_type='tv', filter_label=trakt_label)

		elif info == 'ep_movie_progress':
			search_str = 'Trakt Episodes/Movies in progress'
			from resources.lib.library import trakt_eps_movies_in_progress
			#type = 'movie'
			movies = trakt_eps_movies_in_progress()
			wm.window_stack_empty()
			trakt_label = 'Trakt Episodes/Movies in progress'
			return wm.open_video_list(mode='trakt', listitems=[], search_str=movies, media_type='movie', filter_label=trakt_label)

		elif info == 'trakt_watched':
			#kodi-send --action='RunPlugin(plugin://script.extendedinfo/?info=trakt_watched&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://script.extendedinfo/?info=trakt_watched&trakt_type=tv&script=True)'
			trakt_type = str(params['trakt_type'])
			Utils.show_busy()
			try: trakt_token = xbmcaddon.Addon(addon_ID()).getSetting('trakt_token')
			except: trakt_token = None
			if not trakt_token:
				Utils.hide_busy()
				return
			trakt_script = 'True'
			if info == 'trakt_watched' and trakt_type == 'movie':
				from resources.lib.library import trakt_watched_movies
				movies = trakt_watched_movies()
				trakt_label = 'Trakt Watched Movies'
			elif info == 'trakt_watched' and trakt_type == 'tv':
				from resources.lib.library import trakt_watched_tv_shows
				movies = trakt_watched_tv_shows()
				trakt_label = 'Trakt Watched Shows'

			if keep_stack == None or keep_stack == False:
				wm.window_stack_empty()
			return wm.open_video_list(mode='trakt', listitems=[], search_str=movies, media_type=trakt_type, filter_label=trakt_label)

		elif info == 'search_title':
			search_str = params.get('search_text')
			wm.window_stack_empty()
			Utils.tools_log(search_str)
			return wm.open_video_list(search_str=search_str, mode='search')

		elif info == 'search_menu':
			search_str = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='search')


		elif info == 'setmagnet_list':
			Utils.show_busy()
			new_location = xbmcgui.Dialog().browse(0, "Select Magnet Path Location", "video", defaultt=Utils.ADDON_DATA_PATH)
			new_location = os.path.join(new_location, 'magnet_list.txt')
			xbmcaddon.Addon(addon_ID()).setSetting('magnet_list', new_location)
			Utils.hide_busy()
			

		elif info == 'downloader_progress':
			Utils.hide_busy()
			curr_percent = xbmcgui.Window(10000).getProperty('curr_percent')
			percent_done = xbmcgui.Window(10000).getProperty('percent_done')
			seconds_remaining = xbmcgui.Window(10000).getProperty('seconds_remaining')
			minutes_remaining = xbmcgui.Window(10000).getProperty('minutes_remaining')
			hours_remaining = xbmcgui.Window(10000).getProperty('hours_remaining')
			num_lines_remaining = xbmcgui.Window(10000).getProperty('num_lines_remaining')
			msg = 'File_num_lines_remaining = %s || percent_done = %s || hours_remaining = %s ' % (str(num_lines_remaining),str(percent_done),str(hours_remaining))
			xbmcgui.Dialog().notification(heading='downloader_progress', message=msg, icon=xbmcaddon.Addon().getAddonInfo('icon'), time=5000, sound=True)
			xbmc.log(str(msg), level=xbmc.LOGINFO)

		elif info == 'run_downloader':
			Utils.hide_busy()
			import vod_main
			stop_downloader = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list').replace('magnet_list.txt','stop_downloader')
			if os.path.exists(stop_downloader):
				os.remove(stop_downloader)
			magnet_list = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list')
			download_path = xbmcaddon.Addon(addon_ID()).getSetting('download_path')
			xbmc.log(str('run_downloader___')+'run_downloader===>OPENINFO', level=xbmc.LOGINFO)
			return vod_main.run_downloader(magnet_list, download_path)

		elif info == 'stop_downloader':
			Utils.hide_busy()
			#filename = "stop_downloader"
			stop_downloader = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list').replace('magnet_list.txt','stop_downloader')
			open(stop_downloader, 'w')
			xbmc.log(str('stop_downloader__')+'stop_downloader===>OPENINFO', level=xbmc.LOGINFO)

		elif info == 'manage_download_list':
			magnet_list = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list')
			from tools import read_all_text
			lines = read_all_text(magnet_list).split('\n')
			curr_percent = xbmcgui.Window(10000).getProperty('curr_percent')
			percent_done = xbmcgui.Window(10000).getProperty('percent_done')
			seconds_remaining = xbmcgui.Window(10000).getProperty('seconds_remaining')
			minutes_remaining = xbmcgui.Window(10000).getProperty('minutes_remaining')
			hours_remaining = xbmcgui.Window(10000).getProperty('hours_remaining')
			num_lines_remaining = xbmcgui.Window(10000).getProperty('num_lines_remaining')
			msg = 'File_num_lines_remaining = %s || percent_done = %s || hours_remaining = %s ' % (str(num_lines_remaining),str(percent_done),str(hours_remaining))
			xbmcgui.Dialog().notification(heading='downloader_progress', message=msg, icon=xbmcaddon.Addon().getAddonInfo('icon'), time=5000, sound=True)
			labels = []
			for line in lines:
				try: new_line = eval(line)
				except: continue
				labels.append(str('%s | %s | %s' % (new_line['download_type'].upper(), unquote(new_line['file_name']), unquote(new_line['release_title']))))
			indexes = []
			indexes = xbmcgui.Dialog().multiselect(heading='Select Lines to Delete',options=labels)
			#xbmc.log(str(indexes)+'indexes===>OPENINFO', level=xbmc.LOGINFO)
			if indexes == None:
				Utils.hide_busy()
				return
			if len(indexes) == 0:
				Utils.hide_busy()
				return
			file1 = open(magnet_list, "w")
			file1.write("\n")
			file1.close()
			idx = 0
			for line in lines:
				try: 
					new_line = eval(line)
				except: 
					continue
				if idx in indexes:
					idx = idx + 1
					continue
					#xbmc.log(str(line)+'indexes===>OPENINFO', level=xbmc.LOGINFO)
				else:
					xbmc.log(str(str('%s | %s | %s' % (new_line['download_type'].upper(), unquote(new_line['file_name']), unquote(new_line['release_title']))))+str(idx+1)+'_KEEP_DOWNLOAD===>OPENINFO', level=xbmc.LOGINFO)
					file1 = open(magnet_list, "a") 
					file1.write(str(line))
					file1.write("\n")
					file1.close()
					idx = idx + 1
			Utils.hide_busy()


		elif info == 'reopen_window':
			return reopen_window()

		elif info == 'play_test_call_pop_stack':
			log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			return wm.pop_stack()


		elif info == 'play_test_pop_stack':
			play_test_pop_stack()
			return


		elif info == 'setup_trakt_watched':
			Utils.show_busy()
			from resources.lib import library
			library.trakt_watched_tv_shows_full()
			xbmc.log(str('trakt_watched_tv_shows_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			library.trakt_watched_movies_full()
			xbmc.log(str('trakt_watched_movies_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			Utils.hide_busy()

		elif info == 'open_settings':
			xbmc.executebuiltin('Addon.OpenSettings(%s)' % addon_ID())
			Utils.hide_busy()

		elif info == 'search_string':
			search_str = params['str']
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='search')



		elif info == 'VOD_infodialog' or info == str(addon_ID_short()) + 'dialog':
			resolve_url(params.get('handle'))
			if xbmc.getCondVisibility('System.HasActiveModalDialog | System.HasModalDialog'):
				container_id = ''
			else:
				container_id = xbmc.getInfoLabel('Container(%s).ListItem.label' % xbmc.getInfoLabel('System.CurrentControlID'))
			dbid = xbmc.getInfoLabel('%sListItem.DBID' % container_id)
			if not dbid:
				dbid = xbmc.getInfoLabel('%sListItem.Property(dbid)' % container_id)
			db_type = xbmc.getInfoLabel('%sListItem.DBType' % container_id)
			if db_type == 'movie':
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info='+str(addon_ID_short())+',dbid=%s,id=%s,imdb_id=%s,name=%s)' % (dbid, xbmc.getInfoLabel('ListItem.Property(id)'), xbmc.getInfoLabel('ListItem.IMDBNumber'), xbmc.getInfoLabel('ListItem.Title')))
			elif db_type == 'tvshow':
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=extendedtvinfo,dbid=%s,id=%s,tvdb_id=%s,name=%s)' % (dbid, xbmc.getInfoLabel('ListItem.Property(id)'), xbmc.getInfoLabel('ListItem.Property(tvdb_id)'), xbmc.getInfoLabel('ListItem.Title')))
			elif db_type == 'season':
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=seasoninfo,tvshow=%s,season=%s)' % (xbmc.getInfoLabel('ListItem.TVShowTitle'), xbmc.getInfoLabel('ListItem.Season')))
			elif db_type == 'episode':
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=extendedepisodeinfo,tvshow=%s,season=%s,episode=%s)' % (xbmc.getInfoLabel('ListItem.TVShowTitle'), xbmc.getInfoLabel('ListItem.Season'), xbmc.getInfoLabel('ListItem.Episode')))
			elif db_type in ['actor', 'director']:
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=extendedactorinfo,name=%s)' % xbmc.getInfoLabel('ListItem.Label'))
			else:
				Utils.notify('Error', 'Could not find valid content type')

		elif info == 'VOD_info' or info == str(addon_ID_short()):
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			if not params.get('id'):
				from resources.lib.TheMovieDB import get_movie_info
				#response = get_tmdb_data('search/%s?query=%s&language=en-US&include_adult=%s&' % ('movie', params.get('name'), xbmcaddon.Addon().getSetting('include_adults')), 30)
				#params['id'] = response['results'][0]['id']
				if not params.get('id') and not params.get('dbid') and (not params.get('imdb_id') or not 'tt' in str(params.get('imdb_id'))):
					movie = get_movie_info(movie_label=params.get('name'), year=params.get('year'))
					if movie and movie.get('id'):
						params['id'] = movie.get('id')
					elif not movie:
						xbmcgui.Window(10000).clearProperty('infodialogs.active')
						Utils.hide_busy()
						return
			wm.window_stack_empty()
			wm.open_movie_info(movie_id=params.get('id'), dbid=params.get('dbid'), imdb_id=params.get('imdb_id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')


		elif info == 'slideshow':
			resolve_url(params.get('handle'))
			window_id = xbmcgui.getCurrentwindow_id()
			window = xbmcgui.Window(window_id)
			itemlist = window.getFocus()
			num_items = itemlist.getSelectedPosition()
			for i in range(0, num_items):
				Utils.notify(item.getProperty('Image'))

		elif info == 'youtubevideo':
			from resources.lib.VideoPlayer import PLAYER
			resolve_url(params.get('handle'))
			xbmc.executebuiltin('Dialog.Close(all,true)')
			PLAYER.playtube(params.get('id', ''))

		elif info == 'playtrailer':
			from resources.lib import TheMovieDB
			from resources.lib import local_db
			resolve_url(params.get('handle'))
			if params.get('id'):
				movie_id = params['id']
			elif int(params.get('dbid', -1)) > 0:
				movie_id = local_db.get_imdb_id_from_db(media_type='movie', dbid=params['dbid'])
			elif params.get('imdb_id'):
				movie_id = TheMovieDB.get_movie_tmdb_id(params['imdb_id'])
			else:
				movie_id = ''
			if movie_id:
				TheMovieDB.play_movie_trailer_fullscreen(movie_id)

		elif info == 'playtvtrailer' or info == 'tvtrailer':
			from resources.lib import local_db
			from resources.lib import TheMovieDB
			resolve_url(params.get('handle'))
			if params.get('id'):
				tvshow_id = params['id']
			elif int(params.get('dbid', -1)) > 0:
				tvshow_id = local_db.get_imdb_id_from_db(media_type='show', dbid=params['dbid'])
			elif params.get('tvdb_id'):
				tvshow_id = TheMovieDB.get_show_tmdb_id(params['tvdb_id'])
			else:
				tvshow_id = ''
			if tvshow_id:

				TheMovieDB.play_tv_trailer_fullscreen(tvshow_id)

		elif info == 'play_vod_player':
			from resources.lib.VideoPlayer import PLAYER
			#kodi-send --action="RunScript(script.xtreme_vod,info=prepare_play_VOD_movie,type=tv,show_title=Star Trek: Enterprise,show_season=4,show_episode=20,tmdb=314)"
			#kodi-send --action="RunScript(script.extendedinfo,info=prepare_play_VOD_movie,type=movie,movie_year=,movie_title=Elf,tmdb=)"
			xbmcgui.Window(10000).setProperty('script.xtreme_vod.ResolvedUrl', 'suppress_reopen_window')
			if params.get('type') == 'tv':
				PLAYER.prepare_play_VOD_episode(tmdb = params.get('tmdb'), series_id=None, search_str = None,episode=params.get('show_episode'), season=params.get('show_season'), window=False)
			elif params.get('type') == 'movie':
				PLAYER.prepare_play_VOD_movie(tmdb = params.get('tmdb'), title = params.get('movie_title'), stream_id=None, search_str = None, window=False)
				#movie_year = params.get('movie_year')



		elif info == 'deletecache':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			xbmcgui.Window(10000).clearProperty('xtreme_vod_running')
			for rel_path in os.listdir(Utils.ADDON_DATA_PATH):
				path = os.path.join(Utils.ADDON_DATA_PATH, rel_path)
				try:
					if os.path.isdir(path):
						shutil.rmtree(path)
				except Exception as e:
					Utils.log(e)
			Utils.notify('Cache deleted')
			Utils.hide_busy()

		elif info == 'auto_clean_cache':
			#info=auto_clean_cache&days=10
			days = params.get('days')
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			xbmcgui.Window(10000).clearProperty('xtreme_vod_running')
			auto_clean_cache(days=days)
			Utils.notify('Cache deleted')
			Utils.hide_busy()

		elif info == 'setDownloadLocation':
			Utils.show_busy()
			new_location = xbmcgui.Dialog().browse(0, "Select Download Location", "video", defaultt=Utils.ADDON_DATA_PATH)
			xbmcaddon.Addon(addon_ID()).setSetting('DOWNLOAD_FOLDER', new_location)
			xbmcaddon.Addon(addon_ID()).setSetting('download_path', new_location)
			Utils.hide_busy()

		elif info == 'custom_favourites':
			Utils.show_busy()
			custom_favourites()
			Utils.hide_busy()

		elif info == 'setup_favourites':
			Utils.show_busy()
			setup_favourites()
			Utils.hide_busy()

		elif info == 'patch_tmdb_helper':
			Utils.show_busy()
			patch_tmdbh()
			Utils.hide_busy()


		elif info == 'setup_players':
			import os
			Utils.show_busy()
			tmdb_players_path = os.path.join(Utils.ADDON_DATA_PATH.replace('script.xtreme_vod','plugin.video.themoviedb.helper'),'players')
			player_path_in = xbmcvfs.translatePath(os.path.join(Utils.ADDON_PATH,'direct.xtreme_vod_player.json'))
			player_path_out = xbmcvfs.translatePath(os.path.join(tmdb_players_path,'direct.xtreme_vod_player.json'))
			
			import shutil
			if not xbmcvfs.exists(player_path_out):
				shutil.copyfile(player_path_in, player_path_out)
				Utils.tools_log({'player_path_in': player_path_in, 'player_path_out': player_path_out})

			Utils.hide_busy()

		elif info == 'xml_startup_process':
			from xtream2m3u_run import xml_startup_process
			xml_startup_process()


		elif info == 'iptv_simple_enable':
			Utils.addon_disable_reable(addonid = 'pvr.iptvsimple' , enabled=True)

	return 



def do_patch(patch_file_path, patch_lines, log_addon_name, start_line, end_line):
	file_path = patch_file_path
	if not xbmcvfs.exists(file_path):
		Utils.tools_log('NO_FILE!!!',file_path)
		return 
	Utils.tools_log(file_path,log_addon_name)
	file1 = open(file_path, 'r')
	lines = file1.readlines()
	new_file = ''
	update_flag = False
	line_update = patch_lines
	keep_update = False
	end_line_match = False
	for idx, line in enumerate(lines):
		if '## PATCH' in str(line):
			update_flag = False
			log_message = 'ALREADY_PATCHED_%s_' % (log_addon_name)
			Utils.tools_log(log_message)
			break

		if start_line in str(line):
			new_file = new_file + line_update
			update_flag = True
			keep_update = True
		elif update_flag == True and keep_update == True:
			if end_line in str(line):
				keep_update = False
				end_line_match = True
		elif keep_update == False:
			new_file = new_file + line
	file1.close()
	if update_flag and end_line_match == True:
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()
		log_message = '%s_PATCH_%s' % (file_path,log_addon_name)
		Utils.tools_log(log_message)
		#Utils.notify('Success', log_message)
	elif update_flag and end_line_match == False:
		log_message = 'NO_PATCH_%s_PATCH_%s__%s' % (file_path,log_addon_name,'END_LINE_NOT_FOUND')
		Utils.tools_log(log_message)
		#Utils.notify('Error', log_message)
	return 

def custom_favourites():
	dialog = xbmcgui.Dialog()
	url = dialog.input('Custom Favourite eg imdb_list,list=ls594490332,list_name=tv_movies', 'RunScript(script.xtreme_vod,info=',  type=xbmcgui.INPUT_ALPHANUM)
	if url == '' or url == '-1':
		return
	if not 'RunScript(script.xtreme_vod,info=' in str(url):
		file_path = 'RunScript(script.xtreme_vod,info=%s)' % (str(url))
	else:
		file_path = url + ')'
	
	if file_path[-2:] == '))':
		file_path = file_path[:-2] + ')'
	fave_name = dialog.input('FAVOURITE NAME', '',  type=xbmcgui.INPUT_ALPHANUM)
	if url == '' or url == '-1':
		fave_name = 'Custom Favourite'
	fav1_list = []
	fav1_list.append('	<favourite name="%s" thumb="special://home/addons/script.xtreme_vod/icon.png">%s</favourite>' % (str(fave_name),str(file_path)))

	file_path = xbmcvfs.translatePath('special://userdata/favourites.xml')
	file1 = open(file_path, 'r')
	lines = file1.readlines()
	new_file = ''
	update_list = []
	for j in fav1_list:
		curr_test = j.split('RunScript(')[1].split(')</favourite>')[0]
		if curr_test in str(lines):
			continue
		else:
			update_list.append(j)
	for idx, line in enumerate(lines):
		if line == '</favourites>\n' or idx == len(lines) - 1:
			for j in update_list:
				new_file = new_file + j + '\n'
			new_file = new_file + line
		else:
			new_file = new_file + line
	file1.close()
	if len(update_list) > 0:
		Utils.tools_log('custom_favourites')
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()
	Utils.notify('DONE', 'Restart Kodi to take effect')
	return

def setup_favourites():
	file_path = xbmcvfs.translatePath('special://userdata/favourites.xml')
	fav1_list = []
	fav1_list.append('	<favourite name="VOD Movies" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=allmovies2)</favourite>')
	fav1_list.append('	<favourite name="VOD TV" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=alltv2)</favourite>')
	fav1_list.append('	<favourite name="Trakt Watched TV" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=trakt_watched,trakt_type=tv)</favourite>')
	fav1_list.append('	<favourite name="Trakt Watched Movies" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=trakt_watched,trakt_type=movie)</favourite>')
	fav1_list.append('	<favourite name="Eps_Movies Watching" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=ep_movie_progress)</favourite>')
	fav1_list.append('	<favourite name="Reopen Last" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=reopen_window)</favourite>')

	file1 = open(file_path, 'r')
	lines = file1.readlines()
	new_file = ''
	update_list = []
	for j in fav1_list:
		curr_test = j.split('RunScript(')[1].split(')</favourite>')[0]
		if curr_test in str(lines):
			continue
		else:
			update_list.append(j)
	for idx, line in enumerate(lines):
		if line == '</favourites>\n' or idx == len(lines) - 1:
			for j in update_list:
				new_file = new_file + j + '\n'
			new_file = new_file + line
		else:
			new_file = new_file + line
	file1.close()
	if len(update_list) > 0:
		Utils.tools_log('setup_favourites')
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()
	return


def patch_tmdbh():
	from pathlib import Path
	touch_file = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib') , 'PATCH')
	if os.path.exists(touch_file):
		Utils.tools_log('TMDBH_already_patched')
		return 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player') , 'players.py')
	if not os.path.exists(file_path):
		file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'lib','player') , 'players.py')
	line_update = '''            for idx, i in enumerate(players_list): ## PATCH
                if 'auto_cloud' in str(i).lower() and self.tmdb_type != 'movie': ## PATCH
                    auto_var = idx ## PATCH
                    break ## PATCH
                if 'Auto_Torr_Scrape' in str(i) and self.tmdb_type == 'movie': ## PATCH
                    auto_var = idx ## PATCH
                    break ## PATCH
            #return Dialog().select(header, players, useDetails=detailed) ## PATCH
            #return Dialog().select(header, players, autoclose=30000, preselect=auto_var, useDetails=detailed) ## PATCH
            return Dialog().select(header, players, autoclose=30000, preselect=auto_var, useDetails=detailed) ## PATCH
'''
	first_line = '            for idx, i in enumerate(players_list): '
	last_line = 'return Dialog().select(header, players, useDetails=detailed)'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player') , 'select.py')
	line_update = '''    def select_player(players_list, header=None, detailed=True, index=False, players=None):
        """ Select from a list of players """
        if 'episode' in str(players[0]['mode']):
            db_type = 'episode'
        else:
            db_type = 'movie'
        for idx, i in enumerate(players): ## PATCH
            if 'auto_cloud' in str(i['name']).lower() and db_type != 'movie': ## PATCH
                auto_var = idx ## PATCH
                break ## PATCH
            if 'Auto_Torr_Scrape' in str(i['name']) and db_type == 'movie': ## PATCH
                auto_var = idx ## PATCH
                break ## PATCH
        x = Dialog().select(header or get_localized(32042), [i.listitem for i in players_list],useDetails=detailed, autoclose=30000, preselect=auto_var)
        return x if index or x == -1 else players_list[x].posx

    def get_player(self, x):
        player = self.players_list[x]
        player['idx'] = x
        return player

    def select(self, header=None, detailed=True):
        """ Select a player from the list """
        x = self.select_player(self.players_generated_list, header=header, detailed=detailed, players=self.players)
        return {} if x == -1 else self.get_player(x)
'''
	first_line = '    def select_player(players_list, header=None, detailed=True, index=False):'
	last_line = '        return {} if x == -1 else self.get_player(x)'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 


	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player','dialog') , 'standard.py')
	line_update = '''    def select_player(players_list, header=None, detailed=True, index=False, players=None):
        """ Select from a list of players """
        import xbmc
        #xbmc.log(str([i.listitem for i in players_list])+' ===select_player', level=xbmc.LOGINFO)
        players = [i.__dict__ for i in players]
        if 'episode' in str(players[0]['mode']):
            db_type = 'episode'
        else:
            db_type = 'movie'
        for idx, i in enumerate(players): ## PATCH
            if 'auto_cloud' in str(i['meta']['name']).lower() and db_type != 'movie': ## PATCH
                auto_var = idx ## PATCH
                header = str(i['item']['name']) + ' - ' + str(i['item']['title']) + ' - ' + str(i['item']['firstaired'])
                break ## PATCH
            if 'Auto_Torr_Scrape' in str(i['meta']['name']) and db_type == 'movie': ## PATCH
                auto_var = idx ## PATCH
                header = str(i['item']['name']) + ' - ' + str(i['item']['year'])
                break ## PATCH
        x = Dialog().select(header or get_localized(32042), [i.listitem for i in players_list],useDetails=detailed, autoclose=30000, preselect=auto_var)
        return x if index or x == -1 else players_list[x].posx

    def get_player(self, x):
        return self.players_list[x]

    def select(self, header=None, detailed=True):
        """ Select a player from the list """
        x = self.select_player(self.players_generated_list, header=header, detailed=detailed, players=self.players)
        return {} if x == -1 else self.get_player(x)
'''
	first_line = '    def select_player(players_list, header=None, detailed=True, index=False):'
	last_line = '        return {} if x == -1 else self.get_player(x)'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 


	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script','method') , 'maintenance.py')
	line_update = '''    def vacuum(self, force=False):  ##PATCH
        import time
        if not force and self.is_next_vacuum == False:
            return
        if time.time() < self.next_vacuum:
            return
        self.set_next_vacuum()
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        with TimerFunc('Vacuuming databases:', inline=True):
            ItemDetailsDatabase().execute_sql("VACUUM")
            FindQueriesDatabase().execute_sql("VACUUM")

    def delete_legacy_folders(self, force=False): ##PATCH
'''
	first_line = '    def vacuum(self, force=False):'
	last_line = '    def delete_legacy_folders(self, force=False):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api','trakt') , 'authenticator.py')
	line_update = '''    def poller(self): ## PATCH
        import xbmc
        while True:
            xbmc.log(str(self.user_code)+'===>PHIL', level=xbmc.LOGINFO)
            if self.xbmc_monitor.abortRequested(): ## PATCH
'''
	first_line = '    def poller(self):'
	last_line = '            if self.xbmc_monitor.abortRequested():'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	Path(touch_file).touch()
	return

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script','method') , 'trakt.py')
	line_update = '''def authenticate_trakt(**kwargs): ## PATCH
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI(force=True)
    invalidate_trakt_sync('all', notification=False)

def authorize_trakt(**kwargs):
    import xbmc
    from tmdbhelper.lib.addon.logger import kodi_log
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.api.trakt.token import TraktStoredAccessToken
    trakt_api = TraktAPI(force=False)
    TraktStoredAccessToken(trakt_api).winprop_traktusertoken = ''
    refresh_token = TraktStoredAccessToken(trakt_api).refresh_token
    response = trakt_api.set_authorisation_token(refresh_token)
    if response != {}:
        xbmc.log(str('Trakt authenticated successfully!')+'===>PHIL', level=xbmc.LOGINFO)
    from tmdbhelper.lib.files.futils import json_dumps as data_dumps
    trakt_api.user_token.value = data_dumps(response)
    from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler
    USER_TOKEN = TokenHandler('trakt_token', store_as='setting')
    TraktStoredAccessToken(trakt_api).winprop_traktusertoken = USER_TOKEN.value
    TraktStoredAccessToken(trakt_api).confirm_authorization()
    return

def revoke_trakt(**kwargs): ## PATCH
'''
	first_line = 'def authenticate_trakt(**kwargs):'
	last_line = 'def revoke_trakt(**kwargs):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script') , 'router.py')
	line_update = '''        'authenticate_trakt': ## PATCH
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'authenticate_trakt')(**kwargs),
        'authorize_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'authorize_trakt')(**kwargs),
        'revoke_trakt': ## PATCH
'''
	first_line = "        'authenticate_trakt':"
	last_line = "        'revoke_trakt':" 
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','monitor') , 'player.py')
	line_update = '''    def onAVStarted(self):  ## PATCH
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onPlayBackStarted(self):
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onAVChange(self):
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onPlayBackEnded(self):  ## PATCH
'''
	first_line = '    def onAVStarted(self):'
	last_line = '    def onPlayBackEnded(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 


	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api', 'trakt') , 'api.py')
	line_update = '''    def access_token(self):   ## PATCH
        #if not self.authenticator.access_token:
        #    return
        #if not self.authenticator.trakt_stored_access_token.has_valid_token:
        #    self.refresh_authenticator()
        #return self.authenticator.access_token
        if not self.authenticator.trakt_stored_access_token.has_valid_token:
            self.refresh_authenticator()
        from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler
        from tmdbhelper.lib.files.futils import json_loads as data_loads
        USER_TOKEN = TokenHandler('trakt_token', store_as='setting')
        try: access_token = data_loads(USER_TOKEN.value)['access_token']
        except: return None
        if access_token != self.authenticator.access_token:
            #self.authenticator.access_token = access_token
            from tmdbhelper.lib.api.trakt.token import TraktStoredAccessToken
            TraktStoredAccessToken(self).on_success()
            self.refresh_authenticator()
        return access_token

    @cached_property
    def authenticator(self):  ## PATCH
'''
	first_line = '    def access_token(self):'
	last_line = '    def authenticator(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api', 'trakt') , 'token.py')
	line_update = '''    def update_stored_authorization(self):  ## PATCH
        test_user_token = self.winprop_traktusertoken
        self.trakt_api.user_token.value = self.winprop_traktusertoken = data_dumps(self.stored_authorization)
        if test_user_token != self.trakt_api.user_token.value and len(test_user_token) > 4:
            self.trakt_api.user_token.value = data_dumps(test_user_token)
            self.stored_authorization = data_dumps(test_user_token)
            self.winprop_traktusertoken = data_dumps(test_user_token)

    @property
    def winprop_traktusertoken(self):  ## PATCH
'''
	first_line = '    def update_stored_authorization(self):'
	last_line = '    def winprop_traktusertoken(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	Path(touch_file).touch()
	return


def play_test_pop_stack():
	import json
	tmdbhelper_flag = False
	reopen_play_fail = xbmcaddon.Addon(addon_ID()).getSetting('reopen_play_fail')
	xbmcgui.Window(10000).setProperty('script.xtreme_vod_started', 'True')
	xbmc.sleep(3000)
	if reopen_play_fail == 'false':
		return
	Utils.tools_log(str('start...')+'play_test_pop_stack')
	home_count = 0
	for i in range(1, int((145 * 1000)/1000)):
		window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
		window_id = json.loads(window_id)
		xbmc.sleep(1000)
		window_id2 = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
		window_id2 = json.loads(window_id2)
		#Utils.tools_log(str(window_id)+str(i)+'')
		if (window_id['result']['currentwindow']['label'].lower() in ['home','notification'] or window_id['result']['currentwindow']['id'] in [10000,10107]) and window_id2 == window_id:
			home_count = home_count + 1
			if home_count > 10:
				Utils.tools_log(str('\n\n\n\nwm.pop_stack()......')+'1play_test_pop_stack')
				log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
				return wm.pop_stack()
		if (window_id['result']['currentwindow']['label'].lower() in ['busydialognocancel'] or window_id['result']['currentwindow']['id'] in [10160]) and window_id2 == window_id:
			error_flag = get_log_error_flag(mode='Exception')
			if error_flag:
				xbmc.executebuiltin('Dialog.Close(all,true)')
				Utils.tools_log(str('\n\n\n\nm.pop_stack()......')+'2play_test_pop_stack')
				#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
				log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				return wm.pop_stack()
		if xbmc.Player().isPlaying() or xbmc.getCondVisibility('Window.IsActive(12005)'):
			Utils.tools_log(str('\n\n\n\nPlayback_Success.......')+'play_test_pop_stack')
			return

		if tmdbhelper_flag == True and window_id != window_id2:
			xbmc.sleep(500)
			error_flag = get_log_error_flag(mode='tmdb_helper')
			if error_flag:
				Utils.tools_log(str('\n\n\n\ntmdb_helper_error_flag.......SLEEP......')+'play_test_pop_stack')
				xbmc.sleep(7500)

		if window_id['result']['currentwindow']['label'] == 'Select dialog' or window_id['result']['currentwindow']['id'] == 12000:
			if tmdbhelper_flag == False:
				Utils.hide_busy()
			tmdbhelper_flag = True
		elif tmdbhelper_flag and ( xbmc.Player().isPlaying() or ( window_id['result']['currentwindow']['label'].lower() == 'fullscreenvideo' or window_id['result']['currentwindow']['id'] == 12005 and window_id2 == window_id and i > 4 ) ):
			Utils.tools_log(str('\n\n\n\nPlayback_Success.......')+'play_test_pop_stack')
			return
		elif tmdbhelper_flag and (window_id['result']['currentwindow']['label'].lower() in ['home','notification'] or window_id['result']['currentwindow']['id'] in [10000,10107]) and window_id2 == window_id and i > 4:
			#Utils.tools_log(str(window_id)+str(i)+'')
			if xbmc.Player().isPlaying():
				Utils.tools_log(str('Playback_Success')+'play_test_pop_stack')
				return
			else:
				error_flag = get_log_error_flag(mode='seren')
				if error_flag == False:
					Utils.tools_log(str('\n\n\n\nwm.pop_stack()......')+'3play_test_pop_stack')
					log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
					return wm.pop_stack()
				elif error_flag == True:
					Utils.tools_log(str('\n\n\n\nseren_error_flag.......SLEEP......')+'play_test_pop_stack')
					xbmc.sleep(2500)
	Utils.tools_log(str('return......')+'play_test_pop_stack')
	return 

def follow(thefile):
	while True:
		line = thefile.readline()
		if not line or not line.endswith('\n'):
			time.sleep(0.1)
			continue
		yield line

def follow2():
	logfn = xbmcvfs.translatePath(r'special://logpath\kodi.log')
	with open(logfn, 'r') as f:
		f.seek(0, 2)		   # seek @ EOF
		fsize = f.tell()		# Get Size
		f.seek(max(fsize - 9024, 0), 0)  # Set pos @ last n chars
		lines = f.readlines()	   # Read to end
	line = lines[-6:]
	return str(line)

def get_log_error_flag(mode=None):
	"""
	Retrieves dimensions and framerate information from XBMC.log
	Will likely fail if XBMC in debug mode - could be remedied by increasing the number of lines read
	Props: http://stackoverflow.com/questions/260273/most-efficient-way-to-search-the-last-x-lines-of-a-file-in-python
	@return: dict() object with the following keys:
								'pwidth' (int)
								'pheight' (int)
								'par' (float)
								'dwidth' (int)
								'dheight' (int)
								'dar' (float)
								'fps' (float)
	@rtype: dict()
	"""
	logfn = xbmcvfs.translatePath(r'special://logpath\kodi.log')
	#logfn = '/home/osmc/.kodi/temp/kodi.log'
	xbmc.sleep(250)  # found originally that it wasn't written yet
	with open(logfn, 'r') as f:
		f.seek(0, 2)		   # seek @ EOF
		fsize = f.tell()		# Get Size
		f.seek(max(fsize - 9024, 0), 0)  # Set pos @ last n chars
		lines = f.readlines()	   # Read to end
	lines = lines[-15:]	# Get last 10 lines
	#xbmc.log(str(lines)+'===>OPENINFO', level=xbmc.LOGINFO)
	ret = None
	error_flag = False
	if mode == 'Exception':
		if 'The following content is not available on this app' in str(lines):
			error_flag = True
			return error_flag
	if mode == 'tmdb_helper':
		if 'lib.player - playing' in str(lines) and 'plugin://' in str(lines) and 'plugin.video.themoviedb.helper/plugin.py): script successfully run' in str(lines):
			error_flag = True
			return error_flag
		if 'TORRENTS_FOUND' in str(lines) and '===>A4K_Wrapper' in str(lines):
			error_flag = True
			return error_flag
	if mode == 'seren':
		if 'script successfully run' in str(lines) and '.seren_downloader' in str(lines):
			return error_flag
		if 'Exited Keep Alive' in str(lines) and 'SEREN' in str(lines):
			error_flag = True
			return error_flag
	return error_flag

def resolve_url(handle):
	import xbmcplugin
	if handle:
		xbmcplugin.setResolvedUrl(handle=int(handle), succeeded=False, listitem=xbmcgui.ListItem())

def reopen_window():
	while xbmc.Player().isPlaying():
		xbmc.sleep(500)
	wm.window_stack_empty()
	return wm.open_video_list(search_str='', mode='reopen_window')

def auto_clean_cache(days=None):
	Utils.tools_log('STARTING===>auto_clean_cache')
	try:
		Utils.db_delete_expired(connection=Utils.db_con)
	except:
		xbmc.sleep(2*1000)
		try:
			Utils.tools_log('EXCEPTION__1_auto_clean_cache')
			Utils.db_delete_expired(connection=Utils.db_con)
		except:
			Utils.tools_log('EXCEPTION__2_auto_clean_cache')
			pass
	Utils.tools_log('FINISH===>auto_clean_cache')
	#Utils.db_con.close()
	#auto_clean_cache_seren_downloader(days=30)



def select_pvr_client():
	import xbmc
	import xbmcgui
	import json
	"""
	Presents a selection dialog of installed PVR clients.
	Returns the selected addon ID, or None if cancelled.
	"""
	# JSON-RPC request to get all PVR client addons
	request = {
		"jsonrpc": "2.0",
		"method": "Addons.GetAddons",
		"params": {"enabled": True },
		"id": 1
	}
	
	response_json = xbmc.executeJSONRPC(json.dumps(request))
	response = json.loads(response_json)
	# Extract the list of PVR addons
	#Utils.tools_log(response)
	pvr_addons = response.get("result", {}).get("addons", [])
	
	if not pvr_addons:
		xbmcgui.Dialog().notification("PVR Clients", "No PVR clients installed", xbmcgui.NOTIFICATION_ERROR)
		return None
	
	# Prepare the list of names and IDs for the dialog
	#names = [addon["name"] for addon in pvr_addons]
	addon_ids = [addon["addonid"] for addon in pvr_addons if "pvr." in addon["addonid"]]
	
	if len(addon_ids) == 1:
		return addon_ids[0]

	# Show selection dialog
	dialog = xbmcgui.Dialog()
	selected_index = dialog.select("Select PVR Client", addon_ids)
	
	if selected_index == -1:
		# User cancelled
		return None
	
	# Return the addon ID corresponding to the selected name
	return addon_ids[selected_index]


def reset_stuff():
	import xbmc
	import xbmcgui
	xbmcgui.Dialog().notification("Starting","Starting")
	xbmc.executebuiltin('Dialog.Close(all,true)')
	xbmc.sleep(500)
	xbmc.executebuiltin('ActivateWindow(Home)')
	xbmc.sleep(500)
	xbmc.executebuiltin('ActivateWindow(pvrsettings)')
	xbmc.sleep(500)
	xbmc.executebuiltin('Action(right)')
	window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
	control = window.getControl(window.getFocusId())
	label = control.getLabel()
	x = 0
	while label != 'Clear data' and x < 25:
		xbmc.executebuiltin('Action(down)')
		xbmc.sleep(500)
		control = window.getControl(window.getFocusId())
		label = control.getLabel()
		if label == 'Clear data' or x >= 25:
			break
		x = x +1
	xbmc.executebuiltin('Action(select)')
	unique_labels = []
	curr_label = xbmc.getInfoLabel("ListItem.Label")
	x = 0
	while not curr_label in unique_labels:
		xbmc.sleep(500)
		curr_label = xbmc.getInfoLabel("ListItem.Label")
		if not curr_label == 'Channels, Groups, Guide, Providers':
			xbmc.executebuiltin('Action(select)')
			unique_labels.append(curr_label)
		if curr_label == 'Channels, Groups, Guide, Providers':
			unique_labels.append(curr_label)
		xbmc.sleep(500)
		xbmc.executebuiltin('Action(down)')
		xbmc.sleep(500)
		curr_label = xbmc.getInfoLabel("ListItem.Label")
	xbmc.sleep(500)
	xbmc.executebuiltin('SetFocus(5)')
	xbmc.sleep(500)
	#xbmc.executebuiltin('SetFocus(7)')#CANCEL
	xbmc.executebuiltin('Action(select)')
	xbmc.sleep(500)
	xbmc.executebuiltin('SetFocus(11)')
	xbmc.sleep(500)
	#xbmc.executebuiltin('SetFocus(10)')#NO
	xbmc.executebuiltin('Action(select)')
	xbmc.executebuiltin('Dialog.Close(all,true)')
	Utils.show_busy()
	xbmc.executebuiltin("ActivateWindow(Home)")
	Utils.addon_disable_reable(addonid = Utils.pvr_client , enabled=False)
	
	guide_out = os.path.join(Utils.ADDON_DATA_PATH, 'guide.xml')
	m3u_out = os.path.join(Utils.ADDON_DATA_PATH, 'LiveStream.m3u')
	if os.path.exists(m3u_out):
		os.remove(m3u_out)
	if os.path.exists(guide_out):
		os.remove(guide_out)
	from xtream2m3u_run import generate_m3u
	from xtream2m3u_run import generate_xmltv
	generate_m3u()
	generate_xmltv()
	Utils.addon_disable_reable(addonid = Utils.pvr_client , enabled=True)
	xbmcgui.Dialog().notification("FIN","FIN")