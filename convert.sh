#!/usr/bin/env bash

ext=mp4

read root_dir < root_dir.txt

find "$root_dir" -type f -not -name '*.html' -not -name '*.css' -not -name '*.mp4' -not -name '*.webm' -not -name '*.zip' -not -name '*.ico' | while read file
do
	[ -e "${file%.*}.$ext" ] && continue
	[ ! -e "$file" ] && continue

	echo "Creating: '${file%.*}.$ext'"
	pv "$file" | ffmpeg -i pipe:0 -v warning "temp.$ext" -nostdin -y
	mv "temp.$ext" "${file%.*}.$ext"
	rm "$file"
done
