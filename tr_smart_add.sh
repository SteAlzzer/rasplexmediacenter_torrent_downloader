#!/bin/sh
#TMP_DIR="/tmp/transmission_temp/"

# Getting the torrent-file name via transmission-show #
new_torrent_name=`python3 /home/pi/scripts/transmission/tr.py "$1"`

torrent_folder_path=`readlink -f $1`
torrent_folder_path=`dirname $torrent_folder_path`

new_torrent_name=$torrent_folder_path'/'$new_torrent_name

mv $1 $new_torrent_name


transmission-remote -n "tr:tr" --add "$new_torrent_name" -w "$2"

#dropbox.sh move $1 $new_torrent_name
