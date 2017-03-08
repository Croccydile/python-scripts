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
	for key, value in video.items():
		if key in ('title',
			'extractor',
			'protocol',
			'description',
			'id',
			'format',
			'uploader',
			'upload_date',
			'view_count',
			'like_count',
			'dislike_count',
			'duration',):
			write_string ('%s%-20s%s: %s\n' % (bcolors.WARNING, key, bcolors.ENDC, value))

def youtubedl_printehelp():
	print ('youtubedl-python-wrapper.py')
	print ('  Required options:')
	print ('	-u / --url <url>')
	print ('	-d / --destination <destination folder>')
	print ('	-r / --reslimit <resolution limit>')
	print ('	-t / --toolpath <tool folder containing ffmpeg.exe, etc>')
	print ('  Other options:')
	print ('	-f / --formatext <desired source format extension>')
	print ('	-l / --listformats <list available source formats>')
#	print ('	-h / --help <this help, duh!>')
	print ('')
	input ('Press enter to continue')
	return

# Make sure the template has the preceeding / or \
youtubedl_video_template = '/%(extractor)s - %(uploader)s - %(upload_date)s - %(title)s - %(height)sp - %(id)s.%(ext)s'
youtubedl_playlist_template = '/%(uploader)s/%(extractor)s - %(uploader)s - %(upload_date)s - %(title)s - %(height)sp - %(id)s.%(ext)s'

def youtubedl_setops(reslimit, formatext, destfolder):
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

	# Set requested extensions
	if formatext in ("mp4"):
		videoext = 'mp4'
		audioext = 'm4a'
	elif formatext in ("webm"):
		videoext = 'webm'
		audioext = 'webm'
		
	try:
		videoext
	except NameError:
		newformat = 'bestvideo[height<=' + reslimit + ']+bestaudio/best[height<=' + reslimit + ']'
	else:
		newformat = 'bestvideo[height<=' + reslimit + '][ext=' + videoext + ']+bestaudio[ext=' + audioext + ']/best[ext=' + formatext + ']/best'
		
	print ('Setting format: %s' % newformat)
	options['format'] = newformat

	#input ('Press enter to continue...')
	
	#if config in ("mp4"):
	#	print ('Setting mp4 specific config values')
	#	newformat = 'bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best'
	#elif config in ("webm"):
	#	print ('Setting webm specific config values')
	#	newformat = 'bestvideo[height<=1440][ext=webm]+bestaudio[ext=webm]/best'
	#if config in ("mp4_480p"):
	#	print ('Setting mp4 480p specific config values')
	#	newformat = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best'
	#elif config in ("unrestricted"):
	#	print ('Setting UNRESTRICTED specific config values')
	#	newformat = 'bestvideo+bestaudio/best'
	#else:
	#	# Default setting
	#	print ('Setting DEFAULT config values')
	#	newformat = 'bestvideo[height<=1440]+bestaudio/best[height<=1440]'
	
	return options


def main(argv):

	print (argv)
	try:
		options, remainder = getopt.getopt(argv, 'hlf:u:d:r:t:', ['help',
			'listformats',
			'formatext=',
			'url=', 
			'destination=',
			'reslimit=',
			'toolpath=',])
	except getopt.GetoptError:
		print ('getopt.GetoptError exception!')
		
		youtubedl_printehelp()
		sys.exit(2)

	print ('OPTIONS   :', options)
	print ('REMAINING :', remainder)
		
	for opt, arg in options:
		if opt in ("-h", "--help"):
			youtubedl_printehelp()
			sys.exit()
		elif opt in ("-l", "--listformats"):
			listformats = 'true'
		elif opt in ("-f", "--formatext"):
			formatext = arg
		elif opt in ("-u", "--url"):
			inputurl = arg
		elif opt in ("-d", "--destination"):
			destfolder = arg
		elif opt in ("-r", "--reslimit"):
			reslimit = arg
		elif opt in ("-t", "--toolpath"):
			toolpath = arg
	try: 
		inputurl
	except NameError:
		print ('This wrapper script requires a url specified...')
		print ('')
		youtubedl_printehelp()
		sys.exit(2)

	print ('Input URL is:', inputurl)

	try: 
		destfolder
	except NameError:
		print ('This wrapper script requires a destination folder specified...')
		print ('')
		youtubedl_printehelp()
		sys.exit(2)

	print ('Destination folder is:', destfolder)

	try:
		toolpath
	except NameError:
		print ('This wrapper script requires a folder where tools are stored...')
		print ('')
		youtubedl_printehelp()
		sys.exit(2)
	else:
		os.chdir(toolpath)
	
	try:
		formatext
	except NameError:
		# Just make the routine not care if not specified
		formatext = 'default'

	try: 
		reslimit
	except NameError:
		# Assume 1080p if no resolution was specified
		print ('No reslimit specified, defaulting to 1080p height limit')
		reslimit = '1080'

	youtubedl_opts = youtubedl_setops(reslimit, formatext, destfolder)

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

	print ('Preparing YoutubeDL object')
	ydl = youtube_dl.YoutubeDL(youtubedl_opts)
	ydl.add_default_info_extractors()

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
			# Just a single video

			# Spam out some of the info returned
			youtubedl_writeinfo(result)
			# Along with the available formats
			ydl.list_formats(result)
		
			# Now actually download
			# ydl.params['simulate'] = 'true'
			result = ydl.download([inputurl])
			print ('Result given is %s' % result)
			#for key, value in result.items() :
			#	write_string ("key: %s value: %s\n" % (key, value))
			if (result > 0):
				print ('Uh oh! Something went wrong somewhere...')
				input('Press Enter to continue...')
			
			sys.exit(result)

if __name__ == "__main__":
#	try:
	main(sys.argv[1:])
#	except Exception:
#		print ('Global exception occured...')
#		input ('Press Enter to continue...')
#		sys.exit(2)
