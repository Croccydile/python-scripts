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
	print ('')
	print ('youtubedl-python-wrapper.py')
	print ('  Required options:')
	print ('	-u / --url <url>')
	print ('	-d / --destination <destination folder>')
	print ('	-t / --toolpath <tool folder containing ffmpeg.exe, etc>')
	print ('  Other options:')
	print ('	-r / --reslimit <resolution limit> Defaults to 1080p')
	print ('	-f / --formatext <desired source format extension>')
	print ('	-l / --listformats <list available source formats and exit>')
	print ('	-p / --postprocess <attempt post processing like embed subs>')
#	print ('	-h / --help <this help, duh!>')
	print ('')
	input ('Press enter to continue')
	return

# Make sure the template has the preceeding / or \
youtubedl_video_template = '/%(extractor)s - %(uploader)s - %(upload_date)s - %(title)s - %(height)sp - %(id)s.%(ext)s'
youtubedl_playlist_template = '/%(uploader)s/%(extractor)s - %(uploader)s - %(upload_date)s - %(title)s - %(height)sp - %(id)s.%(ext)s'

def youtubedl_setops(localopts_dict):
	external_downloader_args = compat_shlex_split('--download-result=full --summary-interval=0 --max-connection-per-server 2 --retry-wait=5')

	try:
		localopts_dict['inputurl']
	except KeyError:
		print ('This wrapper script requires a url specified...')
		youtubedl_printehelp()
		sys.exit(2)

	try: 
		localopts_dict['destfolder']
	except KeyError:
		print ('This wrapper script requires a destination folder specified...')
		youtubedl_printehelp()
		sys.exit(2)

	try:
		localopts_dict['toolpath']
	except KeyError:
		print ('This wrapper script requires a folder where tools are stored...')
		youtubedl_printehelp()
		sys.exit(2)
	else:
		os.chdir(localopts_dict['toolpath'])

	try: 
		localopts_dict['reslimit']
	except KeyError:
		# Assume 1080p if no resolution was specified
		print ('No reslimit specified, defaulting to 1080p height limit')
		localopts_dict['reslimit'] = '1080'
				
	print ('Input URL is:', localopts_dict['inputurl'])
	
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
		# This part is important on playlists, otherwise it wastes too much time
		# gathering information ahead of time that we probably do not want
		'extract_flat': 'in_playlist',
		#'writeannotations': 'true',
		
		'external_downloader': 'aria2c.exe',
		'external_downloader_args': external_downloader_args,
		'outtmpl': localopts_dict['destfolder'] + youtubedl_video_template,
		
		# We want to handle our own output
		#'verbose': 'false',
		#'quiet': 'true',

		'logger': youtubedl_logger(),
		'progress_hooks': [youtubedl_hook],
	}
	
	try:
		localopts_dict['postprocess']
	except KeyError:
		pass
	else:
		postprocessors = []
		postprocessors.append({
			'key': 'FFmpegEmbedSubtitle',
		})
		options['postprocessors'] = postprocessors
		
	print ('Setting outtmpl: %s' % options['outtmpl'])
	#sys.exit()
		
	try:
		videoext
	except NameError:
		newformat = ('bestvideo[height<=' 
			+ localopts_dict['reslimit'] 
			+ ']+bestaudio/best[height<=' 
			+ localopts_dict['reslimit'] 
			+ ']')
	else:
		newformat = ('bestvideo[height<=' 
			+ localopts_dict['reslimit'] 
			+ '][ext=' + localopts_dict['videoext'] 
			+ ']+bestaudio[ext=' 
			+ localopts_dict['audioext'] 
			+ ']/best[ext=' 
			+ localopts_dict['videoext'] 
			+ ']/best[height<='
			+ localopts_dict['reslimit']
			+ ']')
					
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

	# print (argv)
	try:
		options, remainder = getopt.getopt(argv, 'hlpf:u:d:r:t:', ['help',
			'listformats',
			'postprocess',
			'formatext=',
			'url=', 
			'destination=',
			'reslimit=',
			'toolpath=',])
	except getopt.GetoptError:
		print ('getopt.GetoptError exception!')

		print ('  Commandline debug:')
		print ('    OPTIONS   :', options)
		print ('    REMAINING :', remainder)
		
		youtubedl_printehelp()
		sys.exit(2)

	localopts = dict()
	for opt, arg in options:
		if opt in ("-h", "--help"):
			youtubedl_printehelp()
			sys.exit()
		elif opt in ("-l", "--listformats"):
			localopts['listformats'] = 'true'
		elif opt in ("-p", "--postprocess"):
			localopts['postprocess'] = 'true'
		elif opt in ("-f", "--formatext"):
			if arg in ('mp4'):
				localopts['videoext'] = 'mp4'
				localopts['audioext'] = 'm4a'
			elif arg in ('webm'):
				localopts['videoext'] = 'webm'
				localopts['audioext'] = 'webm'
		elif opt in ("-u", "--url"):
			localopts['inputurl'] = arg
		elif opt in ("-d", "--destination"):
			localopts['destfolder'] = arg
		elif opt in ("-r", "--reslimit"):
			localopts['reslimit'] = arg
		elif opt in ("-t", "--toolpath"):
			localopts['toolpath'] = arg

	youtubedl_opts = youtubedl_setops(localopts)

	print ('Preparing YoutubeDL object')
	ydl = youtube_dl.YoutubeDL(youtubedl_opts)
	ydl.add_default_info_extractors()

	try:
		localopts['listformats']
	except KeyError:
		pass
	else:
		print ('Will attempt to list formats...')
		ydl = youtube_dl.YoutubeDL({'listformats': 'true'})
		result = ydl.extract_info(
			inputurl,
			download=False # We just want to extract the info
		)
		input ('Press enter to continue...')
		sys.exit()

	with ydl:
		print ('Grabbing video/playlist information...')
		result = ydl.extract_info(
			localopts['inputurl'],
			download=False # We just want to extract the info
		)

		if 'entries' in result:
			# Change output template to reflect playlists
			ydl.params['outtmpl'] = localopts['destfolder'] + youtubedl_playlist_template

			# Special handling for playlists (channel leeching)
			# ydl.params['simulate'] = 'true'
			for video in result['entries']:
				# Spam out some of the info returned
				#youtubedl_writeinfo(result)
				#print (video)
				# Along with the available formats
				#ydl.list_formats(result)
				#print('Video #%d: %s' % (video['playlist_index'], video['title']))
	
				print('Playlist video: %s' % (video['title']))
				result = ydl.extract_info(
					video['url'],
					download=False # We just want to extract the info
				)
				# Spam out some of the info returned
				youtubedl_writeinfo(result)
				result = ydl.download([video['url']])
				print ('Result given is %s' % result)
				if (result > 0):
					print ('Uh oh! Something went wrong somewhere...')
					input('Press enter to continue...')
					sys.exit(result)

		else:
			# Just a single video

			# Spam out some of the info returned
			youtubedl_writeinfo(result)
			# Along with the available formats
			ydl.list_formats(result)
		
			# Now actually download
			# ydl.params['simulate'] = 'true'
			result = ydl.download([localopts['inputurl']])
			print ('Result given is %s' % result)
			#for key, value in result.items() :
			#	write_string ("key: %s value: %s\n" % (key, value))
			if (result > 0):
				print ('Uh oh! Something went wrong somewhere...')
				input('Press enter to continue...')
			
			sys.exit(result)

if __name__ == "__main__":
#	try:
	main(sys.argv[1:])
#	except Exception as non_cuddle_exception:
#		print (non_cuddle_exception)
#		print ('This should not happen')
