import os
import glob
import sys
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Subliminal'))
import tools 
import os
from guessit import guessit
from subliminal import refiners, Video, region, Episode
from subliminal.matches import guess_matches
from subliminal.score import get_scores
import operator
cache_file = 'cachefile.dbm'
region.configure('dogpile.cache.dbm', arguments={'filename': cache_file},replace_existing_backend=True)

file_list = [
	r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x15 - 11001001.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x16 - Too Short a Season.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x17 - When the Bough Breaks.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x18 - Home Soil.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x19 - Coming of Age.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x20 - Heart of Glory.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x21 - Arsenal of Freedom.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x22 - Symbiosis.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x23 - Skin of Evil.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x24 - We'll Always Have Paris.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x25 - Conspiracy.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x26 - The Neutral Zone.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x01-1x02 - Encounter at Farpoint.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x03 - The Naked Now.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x04 - Code of Honor.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x05 - The Last Outpost.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x06 - Where No One Has Gone Before.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x07 - Lonely Among Us.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x08 - Justice.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x09 - The Battle.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x10 - Hide and Q.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x11 - Haven.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x12 - The Big Goodbye.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x13 - Datalore.avi"
	,r"B:\Shared Videos\TV - Completed-Cancelled\Star Trek The Next Generation\Season 1\Star Trek TNG - 1x14 - Angel One.avi"
	]

def compute_score(matches, video):
	#guess = guessit(test_filename)
	#video_test = Video.fromguess(test_filename, guess)
	#matches = guess_matches(video_test, guess)
	scores = get_scores(video)
	#if 'hash' in matches:
	#	logger.debug('Keeping only hash match')
	#	matches &= {'hash'}

	if isinstance(video, Episode):
		if 'title' in matches:
			matches.add('episode')
		if 'series_imdb_id' in matches:
			matches |= {'series', 'year', 'country'}
		if 'imdb_id' in matches:
			matches |= {'series', 'year', 'country', 'season', 'episode'}
		if 'series_tmdb_id' in matches:
			matches |= {'series', 'year', 'country'}
		if 'tmdb_id' in matches:
			matches |= {'series', 'year', 'country', 'season', 'episode'}
		if 'series_tvdb_id' in matches:
			matches |= {'series', 'year', 'country'}
		if 'tvdb_id' in matches:
			matches |= {'series', 'year', 'country', 'season', 'episode'}
	elif isinstance(video, Movie):  # pragma: no branch
		if 'imdb_id' in matches:
			matches |= {'title', 'year', 'country'}
		if 'tmdb_id' in matches:
			matches |= {'title', 'year', 'country'}

	score = int(sum(scores.get(match, 0) for match in matches))
	max_score = scores['hash']
	if not (0 <= score <= max_score):  # pragma: no cover
		logger.info('Clip score between 0 and %d: %d', max_score, score)
		score = int(clip(score, 0, max_score))
	return score, matches

test_fake_filename = 'Star Trek The Next Generation - S01e03 - The Naked Now'
test_guess = guessit(test_fake_filename)
video_test = Video.fromguess(test_fake_filename, test_guess)
video_test1 = refiners.tmdb.refine(video_test, apikey='2cfb516815547f7a9fb865409fe94da2')


#test_fake_filename = 'Star Trek The Next Generation - S01e03 - The Naked Now'
#test_guess = guessit(test_fake_filename)
#video_test = Video.fromguess(test_fake_filename, test_guess)
#video_test2 = refiners.tmdb.refine(video_test, apikey='2cfb516815547f7a9fb865409fe94da2')


#test_fake_filename = 'Star Trek The Next Generation - S01e04 - The Naked Now'
#test_guess = guessit(test_fake_filename)
#video_test = Video.fromguess(test_fake_filename, test_guess)
#video_test3 = refiners.tmdb.refine(video_test, apikey='2cfb516815547f7a9fb865409fe94da2')
#test_matches = guess_matches(video_test, test_guess)


curr_score = []
curr_score2 = []
curr_score3 = []
for i in file_list:
	guess = guessit(i)
	video = Video.fromguess(i, guess)
	try:video = refiners.tmdb.refine(video, apikey='2cfb516815547f7a9fb865409fe94da2')
	except: pass
	#print(video.__dict__)
	matches = guess_matches(video_test1, guess)
	#matches2 = guess_matches(video_test2, guess)
	#matches3 = guess_matches(video_test3, guess)
	#scores = get_scores(video)
	#if isinstance(video, Episode):
	#	if 'title' in matches:
	#		matches.add('episode')
	#	if 'series_imdb_id' in matches:
	#		matches |= {'series', 'year', 'country'}
	#	if 'imdb_id' in matches:
	#		matches |= {'series', 'year', 'country', 'season', 'episode'}
	#	if 'series_tmdb_id' in matches:
	#		matches |= {'series', 'year', 'country'}
	#	if 'tmdb_id' in matches:
	#		matches |= {'series', 'year', 'country', 'season', 'episode'}
	#	if 'series_tvdb_id' in matches:
	#		matches |= {'series', 'year', 'country'}
	#	if 'tvdb_id' in matches:
	#		matches |= {'series', 'year', 'country', 'season', 'episode'}

	#	score = int(sum(scores.get(match, 0) for match in matches))
	#	max_score = scores['hash']
	#	if not (0 <= score <= max_score):  # pragma: no cover
	#		logger.info('Clip score between 0 and %d: %d', max_score, score)
	#		score = int(clip(score, 0, max_score))
	#	print(score)
	#curr_score = compute_score(matches, video)
	#curr_score2 = compute_score(matches2, video)
	#curr_score3 = compute_score(matches3, video)
	
	curr_score.append((video.name,video_test1.name,compute_score(matches, video)))
	#curr_score2.append((video.name,video_test2.name,compute_score(matches2, video)))
	#curr_score3.append((video.name,video_test3.name,compute_score(matches3, video)))
	
	
	#print(curr_score, curr_score2, curr_score3, video)
print(sorted(curr_score,key=operator.itemgetter(1),reverse=True)[0])
#print(sorted(curr_score2,key=operator.itemgetter(1),reverse=True)[0])
#print(sorted(curr_score3,key=operator.itemgetter(1),reverse=True)[0])
#guess = guessit('Breaking.Bad.S01E02')
#video_source = Video.fromguess('Breaking.Bad.S01E02', guess)

#print(video_source)
exit()
from subliminal.video import Episode
test_ep = Episode
test_ep.series_tmdb_id = 4087
print(test_ep.__dict__)
video = Video.fromguess(test_ep)
test_ep = refiners.tmdb.refine(test_ep, apikey='2cfb516815547f7a9fb865409fe94da2')
print(test_ep.__dict__)
from subliminal.refiners.tmdb import get_series_metadata

# Fetch TMDb metadata for the series (including episode metadata)
def fetch_tmdb_metadata(series_name):
	# Use TMDb to get metadata for the series (including season, episode count, etc.)
	metadata = get_series_metadata(series_name)
	return metadata

# Use GuessIt to extract metadata from the file name
def guess_file_metadata(file_name):
	return guessit(file_name)

# Create a MatchTree for the file and return the guessed metadata
from guessit.matchtree import MatchTree

def process_file_with_matchtree(file_name):
	# Create a MatchTree for the file
	match_tree = MatchTree(file_name)
	
	# Access the guessed properties (season, episode, etc.)
	matched_info = match_tree.matched()
	
	return matched_info

# Compare the TMDb metadata with files from the list
def compare_tmdb_with_files(tmdb_metadata, file_list):
	best_match = None
	best_score = 0
	
	# Iterate through each file and compare the metadata
	for file in file_list:
		file_metadata = process_file_with_matchtree(file)
		
		# Simple matching logic: compare season and episode
		if file_metadata.get('season') == tmdb_metadata.get('season') and file_metadata.get('episode') == tmdb_metadata.get('episode'):
			# You can extend the logic to compare title, year, etc.
			score = 100  # Assign a score for an exact match (adjustable)
			
			# If score is higher than the current best, update the best match
			if score > best_score:
				best_score = score
				best_match = file
	
	return best_match

# Example Usage
if __name__ == "__main__":
	# List of episode files in the folder (modify as per your folder structure)
	file_list = [
		"Breaking.Bad.S01E01.Pilot.2008.720p.HDTV.mkv",
		"Breaking.Bad.S01E02.2008.1080p.BDRip.mkv",
		"Breaking.Bad.S01E03.2008.720p.HDTV.mkv"
	]
	
	# Fetch TMDb metadata for the series "Breaking Bad"
	tmdb_metadata = fetch_tmdb_metadata("Breaking Bad")
	
	# For example, assume we're matching episode 1 from season 1 (this would come from TMDb metadata)
	episode_metadata = {'season': 1, 'episode': 1}  # Example metadata from TMDb
	
	# Compare the metadata against the files in the list
	best_match = compare_tmdb_with_files(episode_metadata, file_list)
	
	print(f"Best matching file: {best_match}")
