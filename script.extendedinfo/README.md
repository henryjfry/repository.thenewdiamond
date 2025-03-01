# repository.thenewdiamond - Updated by henryjfry.github.io - Translated to French by TheNewMatrix01
## **Introducing the new and improved Diamond Info!! (aka OpenInfo (Metalliq clone based on Orignal & Extended Info mod ))**

**Diamond Info (aka OpenInfo)**



​		***Dev: Henryjfry and co assist TheNewMatrix01***



The New Diamond Info is a fork of the old Diamond Info which in turn was a fork of the OpenInfo Script.  Currently the addonid is:  script.diamoninfo/script.extendedinfo
WARNING: If you install the extendedinfo variant this will replace any existing copy of script.extendedinfo on your system.
This is by design, so that it has full compatibility with any pre-existing implementations of OpenInfo Script in skins and other add-ons. **YOU HAVE BEEN WARNED !!!** . **Its best to turn OFF auto updates** for Diamond Info / Extended info mod / script / etc . to prevent any repos that have forks from overwriting Diamond Info . You can always force updates when you want updates .

 

This add-on is like the ultimate information and browsing tool. You can search and browse movies, TV shows, related content, cast & crew, and even similar or related media like fanart and trailers. Once you've found something you like, you can use the “Play” and/or “Add to library” features to add to your Trakt collection and sync this to your library.

The New DiamondInfo uses TMDBHelper to play files and requires TMDBHelper be authorized in Trakt.
If Library Auto sync is enabled in the settings it will create STRM files in the addon userdata folder under "TVShows" and "Movies" or in a root directory of your choosing.  And it will sync the items in your trakt collection at startup and after a period of hours as set in the settings (default 8 hours). When it Syncs your library it will attempt to download all the relevant art available at TMDB and Fanart.TV for the movie or show and populate missing information for episodes like plots, episode thumbnails and episode airdates often missing when an episode first becomes available. It will also add new episodes in your trakt calendar to your collection so your collection is always fully up to date.

The TVShows and Movies folder sources can be setup from the settings and a library sync can be triggered from the settings.
Individual shows and movies can then be added to your collection and library from the information screens, which adds the item to your trakt collection and then triggers the collection_sync.
(Therefore if you have not yet run a full sync adding a single show/movie will take as long as it takes for all the shows/movies in your collection to be created as STRM files and download the artwork).

The TMDBHelper context menu can be triggered from the information screens so the TMDBHelper trakt management options for an item can be used.  This can be set to be the default action for the "settings" button on the information screens in the settings.
And additionally the show/movie can be browsed in tmdbhelper from the information screens.

There are new context menu items available in various locations, so you can play from the videolist, from the recommended sections in the info screens, search the people/movies from the context menu on their poster/image. Play the season from the tvshowinfo screen, play the episode from the seasoninfo screen so you dont need to go into an episode before a play button can be accessed.
Additionally there are new play options "Play Kodi Next Episode" (play the next episode for the show after the last episode watched as recorded in your DB), "Play Trakt Next Episode" (play the next episode for the show as returned by trakt progrss (ie newest episode of the show), "Play Trakt Next Episode (Rewatch)" (play the next episode of the show after the last episode watched for a show you are rewatching).


There has also been added functionality for Trakt and IMDB lists.  By default the Trakt Lists and IMDB lists are sourced from:

https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/imdb_list.json
https://bit.ly/2WABGMg

https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/trakt_list.json
https://bit.ly/3jCkXkw

And the url can be changed in the settings, if the custom url setting is disabled in the settings it will use "imdb_list.json" and "trakt_list.json" in the addon folder:
"~/.kodi/addons/script.extendedinfo"

If you wish to create your own lists of lists see the two JSON files in the addon folder or look at one of the lists at the urls above for the list format.

These list items will then be available to the plugin and the UI so you can browse trakt/imdb lists (however only shows/movies will be returned)


If this addon is pulled up though addons>Video Addons > Diamond Info it will be displayed in the typical kodi directory script listings view. 
And if pulled up though Addons > Program addons > Diamond Info it will be in the Diamond Info fancy UI view
 

*Special Netflix theme with auto-trailer playback can be enabled in settings ! warning this is heavy and not recommended for low power devices like firesticks or mii box *


WARNING !!!!!!!!!!!!!!!!!!! READ BELOW

Because Diamond Info *replaces* OpenInfo Script, this maintains compatibility with any existing implementations in skins or other add-ons. **If you have have auto-updates turned on and this repository installed**, Diamond Info Script **will be updated** to Diamond Info, including the downloading of any applicable dependencies. If you **DO NOT** want Diamond Info, either disable updates for Diamond Info Script from its add-on information screen, or disable auto-updates from:

Settings -> System -> Add-ons -> Updates

 

The recommended setting is “Notify, but don't install updates”.

If you need to reverse the update, and go back to Diamond Info Script, disable updates as above, and force “update” Diamond Info to the version on the official Kodi Repository.



***Instructions for adding this repo\***:



·     Go to the Kodi file manager.

·     Click on "Add source"

·     The path for the source is [TheNewMatrix01/TheNewDiamond: TheNewDiamond       (github.com)/](https://henryjfry.github.io/repository.thenewdiamond/index.html) (Give it the name "TheNewMatrix").

·     Go to "Add-ons"

·     In Add-ons, install an addon from zip. When it asks for the location, select "TheNewMatrix", and install [https://henryjfry.github.io/repository.thenewdiamond/script.extendedinfo-1.30.zip) (or whatever version is higher )

·     Go back to Add-ons install, but this time, select "Install from repository"

·     Select the "TheNewMatrix"

·     Go into the "Video add-ons" section in the repo, and you'll find Diamond Info

·     Go into the Program add-ons" section in the repo, and you'll find Diamond Info

 

***EDIT: if it was not already clear , i'm not the developer I take no credit for any code here . Just passing it along !



BONUS ! , if you would like to point a Shortcut / category widget to open info search use this custom action

RunScript(script.extendedinfo,info=search_menu)

Plugin Routes (open in kodis default addon pages):

plugin://script.extendedinfo/?info=libraryallmovies
plugin://script.extendedinfo/?info=libraryalltvshows
plugin://script.extendedinfo/?info=popularmovies
plugin://script.extendedinfo/?info=topratedmovies
plugin://script.extendedinfo/?info=incinemamovies
plugin://script.extendedinfo/?info=upcomingmovies
plugin://script.extendedinfo/?info=populartvshows
plugin://script.extendedinfo/?info=topratedtvshows
plugin://script.extendedinfo/?info=onairtvshows
plugin://script.extendedinfo/?info=airingtodaytvshows
plugin://script.extendedinfo/?info=studio&studio=Studio Name

Script Routes (open in the fancy UI):

#UI all movies
plugin://script.extendedinfo/?info=allmovies

#UI all tv shows
plugin://script.extendedinfo/?info=alltvshows

#Text entry dialog + UI with search results
plugin://script.extendedinfo/?info=search_menu

#UI Trakt watched TV (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_watched&trakt_type=tv

#UI Trakt watched Movies (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_watched&trakt_type=movie

#UI Trakt collection movie (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_coll&trakt_type=movie

#UI Trakt collection TV (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_coll&trakt_type=tv


#UI Trakt list with name of list and user id and trakt list slug from list url and sort rank and sort order asc (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_list&trakt_type="trakt_type"&trakt_list_name="trakt_list_name"&trakt_user_id="trakt_user_id"&takt_list_slug="takt_list_slug"&trakt_sort_by=rank&sort_order=asc

#UI Trakt list with name of list and user id and trakt list slug from list url and sort listed_at and sort order desc (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_list&trakt_type="trakt_type"&trakt_list_name="trakt_list_name"&trakt_user_id="trakt_user_id"&takt_list_slug="takt_list_slug"&trakt_sort_by=listed_at&sort_order=desc	(&script=False)

#UI IMDB list with "ls999999" imdb list number (+ plugin with &script=False)
imdb_list&list=ls9999999

#UI with a search to return all movies and tvshows for the given results
search_string&str=Search Term

#UI with a search to return all movies and tvshows for the given person
search_person&person=Person Name

Extended info dialogs (for skins??)

RunScript(script.extendedinfo,info=diamondinfo,dbid=%s,id=%s,imdb_id=%s,name=%s)
RunScript(script.extendedinfo,info=extendedtvinfo,dbid=%s,id=%s,tvdb_id=%s,name=%s)
RunScript(script.extendedinfo,info=seasoninfo,tvshow=%s,season=%s)
RunScript(script.extendedinfo,info=extendedepisodeinfo,tvshow=%s,season=%s,episode=%s)
RunScript(script.extendedinfo,info=extendedactorinfo,name=%s)



############################################################################################



# repository.thenewdiamond - Mis à jour par henryjfry.github.io - Traduit en Français par TheNewMatrix01

## **Voici Diamond Info nouveau et amélioré!! (alias OpenInfo (Metalliq clone basé sur l'orignal & Extended Info mod ))**

**Diamond Info (alias OpenInfo)**

Le nouveau Diamond Info est un dérivé du vieux Diamond Info  qui lui aussi était un dérivé  du script OpenInfo.  Maintenant le "Addon ID" est script.extendedinfo.

Donc, veuillez noter que dorénavant ceci vas remplacer toutes les copies  existantes  du script.extendedinfo de votre système.
Ce script est complètement compatible avec les implémentations pré-existantes du script OpenInfo dans les skns et les addiciels. **Vous êtes maintenant avertis!!!  Il est préférable de mettre à OFF les mises à jour automatiques !!!** .  Pour Diamond Info / Extended info mod / script / etc... afin de prévenir que d'autres repo qui seraient un dérivé de notre travail, viennent écraser cet additiel par un autre. Vous pouvez  toujours forcer les mises à jour, quand cela vous plaise.

 

Cet addiciel est une source d'information ultime et aussi un outil de navigation. Vous pouvez effectuer des recherches et naviguer pour des films, émissions de télé, voir leurs contenu associés, voir les acteurs et aussi voir des fanart et des bandes annonces. OLorsque vous avez faites votre choix, vous pouvez faire "Jouer" et ou "Ajouter" et ou "Ajouter à la librairie" et vous avez aussi la possibilité de faire des ajouts dans votre collection TrakT et effectuer une synchronisation à cette librairie.

Le Nouveau Diamond Info utilise TMDBHelper pour faire 'Jouer" vos choix et  TMDBHelper doit nécessairement être authorisé avec Trakt.

Si l'option Library Auto synch est activée, dans la configuration de Diamond Info, l'addiciel vas commencer à créer des fichiers STRM dans le répertoire de l'addiciel Diamond Info  dans le répertoire userdata , l'addicielvas créer deux répertoires "TVShows" et "Movies"ou bien dans le répertoire de votre choix.  De plus, il y aura aussi une synchronisation des items dans votre collection de TrakT lors du démarrge et aussi aprèsune période en heures que vous aurez à définir dans l'addiciel, par défaut, la configaration définie est de 8 heures. Lorsque la synchronistion s'effectue dans votre librairie, l'addiciel vas tenter de télécharger les fichiers d'ordre graphiques qui proviennent du site TMDB et Fanart.TV pour les films et les émissions de télé en afin de comblerles informations manquantespour les épisodes, un résumé du film ou d'une émission, des images représentant les épisodes, les dates pour le visionnement, surtout lorsqu'une épisode deviens disponible. L'addiciel vas aussi ajouter des nouveaux épisodes dans votre calendrier TrakT  à votre collection afin que votre collection demeurent toujours à jour.

Les répertoires TVShows et Movies peuvent être persnnalisés et la synchronisation de la librarie peux être déclenchée dans la configuration de Diamond info.
(Si vous n'avez pas lancé une synchronisation complète (full synch), le fait d'ajouter un simple film ou émission de tété, le temps requis vas prendre, plus de temps que vous croyez, car l'addiciel vas parcourir tous les émissions de télé / films pour populervotre collectionques a été crée en fichiers  STRM fichiers et en téléchargeant les fichiers graphiques).

Le menu contextuel  du TMDBHelper peux être déclenché depuis l'écran de demande d'information de TMDBHelper trakt management options pour un item choisis.  Ceci peux ête définie par une action par défaut de la configuration voir bouton  "settings" de l'écran information dans la section settings.
Il est à souligner que les émissions de télé / films peuvent être navigable depuis l'écrand information de tmdbhelper.

Il y a un nouveau menu contextuel items qui est disponible dans plusieurs endroits, vous pouvez faire jouer depuis une videolist depuis une section recommandée dans l'écran info, lors d'une recherche de personne/film du menu contextuel ou depuis les affiches de poster de films.  Faire jouer la saison d'une émisssion de télé, jouer une épisode depuis l'écran affichan la saison, afin que vous n'avez pas à aller épisode avant que le bouton jouer puisse être accessible.

De plus, il y a un nouveau bouton "Play Kodi Next Episode" (joue l'épisode suivante pour l'émission concernant la dernièere émission jouée ou tant que enregistreé and votre DB ), "Play Trakt Next Episode" (joue l'épisode suivante pour lémission suivante retournée par la progression de TrakT (ie épisode la plus récente d,une émission de télé), "Play Trakt Next Episode (visionner à nouveau)" (joue l'épisode suivante d'une émission de télé après la dernièere  épisode visionnée d'une émission que vous revisionne play).


Il y a aussi une nouvelle fonctionnalitée qui a été ajoutée pour for Trakt et IMDB lists.  Par défaut Trakt Lists et IMDB lists sont des sources de ces deux fichiers en exemple:

https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/imdb_list.json
https://bit.ly/2WABGMg

https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/trakt_list.json
https://bit.ly/3jCkXkw

Les urls peuvent être personnalisés à votre goût,   IPour activer l'utilisation do vos listes personnelles json vous devez désactiver dans la configuration de custom url setting et ensuite vous pourrez utiliser vos listes personnelles "imdb_list.json" et "trakt_list.json" in the addon folder:
"~/.kodi/addons/script.extendedinfo"

Si vous désirez créer vos propres list pour  les deux two fichiers JSON files dans le répertoire de l'addiciel,  vous pouvezz vous inspirer des listes en exemples ci-dessus.

La liste des items seras disponible quand les extensiions et les interfaces usagers seront disponibles  afin que vous puissiez naviguer avec des listes  trakt/imdb lists (mais seulment des listes d'émission de télé et de films seront retournées).




Si cet addiciel est invoqué via  addons>programs > Diamond Info iil vas afficher le script typique de Kodi et si cet addiciel est invoqué via Addons > Video addons > Diamond Info il vas afficher une vue beaucoup plus graphique  dans Diamond Info.

**Le thème spécial Netflix  avec lecture de la bande annonve automatique peux être activé dans la configurationcan  ! Avertissement ce thème n'est pas recommandé pour des sytème ayant une puissance modeste firesticks ou mii box **





**WARNING !!!!!!!!!!!!!!!!!!! READ BELOW**



Du fait que Diamond Info *remplace le script de OpenInfo, il en vas tout de m^me que la comptabilité devrais être la même pour tous les systèmes et les skins. **Si vous avez laissé la configuration auto-updates (mises à jour automatiques) activée**, Diamond Info Script **seras mis à jour** to Diamond Info, inclus le téléchargement des dépendences de façon automatique. Si vous **Ne désirez pas**  Diamond Info, soit que vous désactivez les mises àa jour pour Diamond Info Script à partir de l'écran add-on information, ou désactiver la mise à jour automatique  de:

Settings -> System -> Add-ons -> Updates

 

Nous recommendons de laisser activé “Notify, but don't install updates”.

si vous désirez revenir à la configuration d'origine avant cette mise à jour, revenez dans Diamond Info Script, désactivez uppdates tel que décris ci-haut, et forcez  “update” Diamond Info à la version précédante que vous désirez,  dans le repo official Kodi.





***Instructions for adding this repo\***:

·     Go to the Kodi file manager.

·     Click on "Add source"

·     The path for the source is [TheNewMatrix01/TheNewDiamond: TheNewDiamond       (github.com)/](https://henryjfry.github.io/repository.thenewdiamond/index.html) (Give it the name "TheNewMatrix").

·     Go to "Add-ons"

·     In Add-ons, install an addon from zip. When it asks for the location, select "TheNewMatrix", and install [https://henryjfry.github.io/repository.thenewdiamond/script.extendedinfo-1.30.zip) (or whatever version is higher )

·     Go back to Add-ons install, but this time, select "Install from repository"

·     Select the "TheNewMatrix"

·     Go into the "Video add-ons" section in the repo, and you'll find Diamond Info

·     Go into the Program add-ons" section in the repo, and you'll find Diamond Info

 



BONUS ! , si vous voulez créer des raccourcis a Shortcut / category widget pour ouvrir l'écran info search utilisez ces actions



RunScript(script.extendedinfo,info=search_menu)

Plugin Routes (open in kodis default addon pages):

plugin://script.extendedinfo/?info=libraryallmovies
plugin://script.extendedinfo/?info=libraryalltvshows
plugin://script.extendedinfo/?info=popularmovies
plugin://script.extendedinfo/?info=topratedmovies
plugin://script.extendedinfo/?info=incinemamovies
plugin://script.extendedinfo/?info=upcomingmovies
plugin://script.extendedinfo/?info=populartvshows
plugin://script.extendedinfo/?info=topratedtvshows
plugin://script.extendedinfo/?info=onairtvshows
plugin://script.extendedinfo/?info=airingtodaytvshows
plugin://script.extendedinfo/?info=studio&studio=Studio Name

Script Routes (open in the fancy UI):

#UI all movies
plugin://script.extendedinfo/?info=allmovies

#UI all tv shows
plugin://script.extendedinfo/?info=alltvshows

#Text entry dialog + UI with search results
plugin://script.extendedinfo/?info=search_menu

#UI Trakt watched TV (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_watched&trakt_type=tv

#UI Trakt watched Movies (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_watched&trakt_type=movie

#UI Trakt collection movie (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_coll&trakt_type=movie

#UI Trakt collection TV (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_coll&trakt_type=tv


#UI Trakt list with name of list and user id and trakt list slug from list url and sort rank and sort order asc (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_list&trakt_type="trakt_type"&trakt_list_name="trakt_list_name"&trakt_user_id="trakt_user_id"&takt_list_slug="takt_list_slug"&trakt_sort_by=rank&sort_order=asc

#UI Trakt list with name of list and user id and trakt list slug from list url and sort listed_at and sort order desc (+ plugin with &script=False)
plugin://script.extendedinfo/?info=trakt_list&trakt_type="trakt_type"&trakt_list_name="trakt_list_name"&trakt_user_id="trakt_user_id"&takt_list_slug="takt_list_slug"&trakt_sort_by=listed_at&sort_order=desc	(&script=False)

#UI IMDB list with "ls999999" imdb list number (+ plugin with &script=False)
imdb_list&list=ls9999999

#UI with a search to return all movies and tvshows for the given results
search_string&str=Search Term

#UI with a search to return all movies and tvshows for the given person
search_person&person=Person Name

Extended info dialogs (for skins??)

RunScript(script.extendedinfo,info=diamondinfo,dbid=%s,id=%s,imdb_id=%s,name=%s)
RunScript(script.extendedinfo,info=extendedtvinfo,dbid=%s,id=%s,tvdb_id=%s,name=%s)
RunScript(script.extendedinfo,info=seasoninfo,tvshow=%s,season=%s)
RunScript(script.extendedinfo,info=extendedepisodeinfo,tvshow=%s,season=%s,episode=%s)
RunScript(script.extendedinfo,info=extendedactorinfo,name=%s)