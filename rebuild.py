#!/usr/bin/env python3

from pathlib import Path
from mako.template import Template
import urllib.parse # for escaping urls
import subprocess

#Read potentially sensitive data from configs
with open('font_awesome_kit_url.txt', 'r') as fp:
	FONTAWESOMEKITURL = fp.read().strip()
with open('root_dir.txt', 'r') as fp:
	ROOT_DIR = fp.read().strip()

# Keep track of all paths and their sizes,
# so that we don't compute disk usage multiple times.
PATH_SIZES = {}

def size(path):
	global PATH_SIZES

	if path not in PATH_SIZES:
		PATH_SIZES[path] = subprocess.check_output(['du','-sh',path]).decode('utf-8').split()[0]

	return PATH_SIZES[path]

def archive_path(path):
	for ext in ['.zip', '.tar.xz', '.tar.gz']:
		item = Path(path + ext)
		if item.is_file():
			return item.name
	return ''

def make_html(directory, root_dir):
	global FONTAWESOMEKITURL

	dir = Path(directory)

	next = ''
	prev = ''
	if directory != root_dir:
		#Find immediate siblings of this directory
		found_this = False
		for file in sorted(dir.parent.iterdir(), key=lambda d: d.name.lower()):
			if found_this:
				if file.is_dir():
					next = urllib.parse.quote('../' + file.name)
					break
			else:
				if file.name == dir.name:
					found_this = True
				elif file.is_dir():
					prev = urllib.parse.quote('../' + file.name)

	#Generate config for all items in this directory
	files = [
		dict(
			url = urllib.parse.quote(file.name),
			name = file.name,
			size = size(file.as_posix()),
			is_dir = file.is_dir(),
			is_video = True if file.suffix in ['.mp4', '.webm'] else False,
			archive = urllib.parse.quote(archive_path(file.as_posix())),
		)
		for file in sorted(dir.iterdir(), key=lambda d: d.name.lower())
		]

	#Generate config for this directory
	template = Template(filename = 'directory.html')
	return template.render(
		files = files,
		name = dir.name.title(),
		prev_sibling = prev,
		next_sibling = next,
		fontAwesomeKitURL = FONTAWESOMEKITURL,
		title = 'Directory Listing of ' + directory,
		total_size = size(directory),
		has_parent = directory != root_dir,
	)

# Get a list of all directories to make indexes for
print(f'Scanning all directories under {ROOT_DIR}... ', end='', flush=True)
p = Path(ROOT_DIR)
dirs = [ROOT_DIR] + [x.as_posix() for x in p.glob('**/*') if x.is_dir()]
print('Done.', flush=True)

# Generate index files
index = 1
total = len(dirs)
old_msg = ''
print(f'Generating indexes for {total} directories... ', end='', flush=True)
for dir in dirs:
	path = dir + '/index.html'

	with open(path, 'w') as fp:
		fp.write(make_html(dir, ROOT_DIR))

	msg =  f'[{index}/{total}]'
	print(('\b'*len(old_msg)) + msg, end='', flush=True)
	old_msg = msg
	index += 1
print()

# Copy stylesheet to root dir
subprocess.run(['cp', 'styles.css', ROOT_DIR])

# Copy favicon to root dir
subprocess.run(['cp', 'favicon.ico', ROOT_DIR])
