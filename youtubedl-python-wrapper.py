#!/usr/bin/env python
# coding: utf-8

# Cutely see http://stackoverflow.com/questions/18054500/how-to-use-youtube-dl-from-a-python-program
# https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L129-L279
# https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl

# Make sure we implicitly import write_string from youtube_dl/utils.py
# Because windows console handling UTF8 strings is retarded
from youtube_dl import write_string
# For making the external download args friendly
from youtube_dl import compat_shlex_split

import youtube_dl
import sys, os, getopt

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
class youtubedl_logger(object):
	def debug(self, msg):
		write_string('DEBUG: %s\n' % msg)
		# string_for_output = msg.encode('utf8', 'replace')

	def warning(self, msg):
		write_string('WARN: %s\n' % msg)

	def error(self, msg):
		write_string('ERROR: %s\n' % msg)

def youtubedl_hook(progress):
	return
	if progress['status'] == 'finished':
		print ('Done downloading, now converting ...')
	# write_string ('HOOK: %s\n' % progress['downloaded_bytes'])
	for key, value in progress.items() :
		print (key)

def youtubedl_writeinfo(video):
	write_string (bcolors.OKBLUE + 'Title' + bcolors.ENDC + '       : %s\n' % (video['title']))
	write_string (bcolors.OKBLUE + 'Description' + bcolors.ENDC + ' : %s\n' % (video['description']))
	write_string (bcolors.OKBLUE + 'ID' + bcolors.ENDC + '          : %s\n' % (video['id']))
	write_string (bcolors.OKBLUE + 'Format' + bcolors.ENDC + '      : %s\n' % (video['format']))
	write_string (bcolors.OKBLUE + 'Uploader' + bcolors.ENDC + '    : %s\n' % (video['uploader']))
	write_string (bcolors.OKBLUE + 'Upload date' + bcolors.ENDC + ' : %s\n' % (video['upload_date']))
	write_string (bcolors.OKBLUE + 'Views' + bcolors.ENDC + '       : %s\n' % (video['view_count']))
	write_string (bcolors.OKBLUE + 'Likes' + bcolors.ENDC + '       : %s\n' % (video['like_count']))
	write_string (bcolors.OKBLUE + 'Dislikes' + bcolors.ENDC + '    : %s\n' % (video['dislike_count']))
	write_string (bcolors.OKBLUE + 'Duration' + bcolors.ENDC + '    : %s secs\n' % (video['duration']))	

# Make sure the template has the preceeding / or \
youtubedl_video_template = '/%(extractor)s - %(uploader)s - %(upload_date)s - %(title)s - best - %(id)s.%(ext)s'
youtubedl_playlist_template = '/%(uploader)s/%(extractor)s - %(uploader)s - %(upload_date)s - %(title)s - best - %(id)s.%(ext)s'

def youtubedl_setops(config, destfolder):
	postprocessors = []
	postprocessors.append({
		'key': 'FFmpegEmbedSubtitle',
	})
	external_downloader_args = compat_shlex_split('--download-result=full --summary-interval=0 --max-connection-per-server 2 --retry-wait=5')
	#print (external_downloader_args)
	#sys.exit()

	options = {
		# We want youtube-dl to handle output
		'verbose': 'true',
		'nooverwrites': 'true',
		'ignoreerrors': 'true',
		'continuedl': 'true',
		'no_check_certificate': 'true',
		'skip_unavailable_fragments': 'true',
		'consoletitle': 'true',
		'updatetime': 'false',
		# Only the video is downloaded in a video + playlist
		'noplaylist': 'true',
		'addmetadata': 'true',
		'writedescription': 'true',
		'xattrs': 'true',
		'writesubtitles': 'true',
		'allsubtitles': 'true',
		'embedsubtitles': 'true',
		'fixup': 'warn',
		#'writeannotations': 'true',
		
		'postprocessors': postprocessors,
		'external_downloader': 'aria2c.exe',
		'external_downloader_args': external_downloader_args,
		'outtmpl': destfolder + youtubedl_video_template,
		
		# We want to handle our own output
		#'verbose': 'false',
		#'quiet': 'true',

		'logger': youtubedl_logger(),
		'progress_hooks': [youtubedl_hook],
	}
	
	print ('Setting outtmpl: %s' % options['outtmpl'])
	#sys.exit()
	
	if config in ("mp4"):
		print ('Setting mp4 specific config values')
		newformat = 'bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best'
	elif config in ("webm"):
		print ('Setting webm specific config values')
		newformat = 'bestvideo[height<=1440][ext=webm]+bestaudio[ext=webm]/best'
	if config in ("mp4_480p"):
		print ('Setting mp4 480p specific config values')
		newformat = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best'
	elif config in ("unrestricted"):
		print ('Setting UNRESTRICTED specific config values')
		newformat = 'bestvideo+bestaudio/best'
	else:
		# Default setting
		print ('Setting DEFAULT config values')
		newformat = 'bestvideo[height<=1440]+bestaudio/best[height<=1440]'

	print ('Setting format: %s' % newformat)
	options['format'] = newformat

	return options


def main(argv):

	try:
		opts, args = getopt.getopt(argv,"hld:u:c:t:",["inputurl=", "dlconfig="])
	except getopt.GetoptError:
		print ('youtubedl-wrapper.py -u <url> -c <config type>')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print ('youtubedl-wrapper.py -u <url> -c <config type>')
			sys.exit()
		elif opt in ("-l", "--listformats"):
			listformats = 'true'
		elif opt in ("-d", "--destination"):
			destfolder = arg
		elif opt in ("-u", "--url"):
			inputurl = arg
		elif opt in ("-c", "--config"):
			dlconfig = arg
		elif opt in ("-t", "--toolpath"):
			toolpath = arg
	try: 
		inputurl
	except NameError:
		print ('This wrapper script requires a url specified...')
		sys.exit(2)

	print ('Input URL is:', inputurl)

	try: 
		destfolder
	except NameError:
		print ('This wrapper script requires a destination folder specified...')
		sys.exit(2)

	print ('Destination folder is:', destfolder)

	try: 
		dlconfig
	except NameError:
		# Force  downloader config to be specified
		print ('This wrapper script requires a downloader config specified...')
		sys.exit(2)
	else:
		youtubedl_opts = youtubedl_setops(dlconfig, destfolder)

	try:
		toolpath
	except NameError:
		print ('This wrapper script requires a folder where tools are stored...')
		sys.exit(2)
	else:
		os.chdir(toolpath)

	try:
		listformats
	except NameError:
		pass
	else:
		print ('Will attempt to list formats...')
		ydl = youtube_dl.YoutubeDL({'listformats': 'true'})
		result = ydl.extract_info(
			inputurl,
			download=False # We just want to extract the info
		)
		sys.exit()

	#print ('Config type is:', dlconfig)

	youtubedl_opts
	ydl = youtube_dl.YoutubeDL(youtubedl_opts)

	with ydl:
		print ('Grabbing video/playlist information...')
		result = ydl.extract_info(
			inputurl,
			download=False # We just want to extract the info
		)

		if 'entries' in result:
			# Change output template to reflect playlists
			ydl.params['outtmpl'] = destfolder + youtubedl_playlist_template
			# Special handling for playlists
			for video in result['entries']:
				print('Video #%d: %s' % (video['playlist_index'], video['title']))

		else:
			# Just a video
			youtubedl_writeinfo(result)
		
			# Now actually download
			# ydl.params['simulate'] = 'true'
			result = ydl.download([inputurl])
			print ('Result given is %s' % result)
			#for key, value in result.items() :
			#	write_string ("key: %s value: %s\n" % (key, value))
			if (result > 0):
				print ('Uh oh! Something went wrong somewhere...')
				input("Press Enter to continue...")
			
			sys.exit(result)

if __name__ == "__main__":
    main(sys.argv[1:])

