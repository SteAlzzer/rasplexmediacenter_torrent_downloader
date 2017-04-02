import os
import sys
from argparse import ArgumentParser

import config


def _remove_tmp_file():
    if os.path.exists(config.TMP_FILE):
        os.remove(config.TMP_FILE)


def get_torrent_destionation_path(torrent_file_path):
    dropbox_path = os.path.abspath(os.path.realpath(config.DROPBOX_TORRENT_FOLDER_PATH))
    for folder_name, full_dest_path in config.DROPBOX_FOLDER_MAP.items():
        full_path_folder = os.path.join(dropbox_path, folder_name)
        if full_dest_path in torrent_file_path:
            return os.path.abspath(os.path.realpath(full_dest_path))


def get_torrent_name(torrent_path):
    _remove_tmp_file()
    cmd = '{0} "{1}" >> "{2}"'.format(config.TR_SHOW, torrent_path, config.TMP_FILE)
    os.system(cmd)

    torrent_name = ''
    for line in open(config.TMP_FILE):
        if config.SEARCH_FOR_NAME in line:
            torrent_name = line.split(config.SEARCH_FOR_NAME)[1].strip().rstrip('\r\n')
            break
    _remove_tmp_file()
    return torrent_name

def dropbox_move(file_1, file_2):
    path_1 = os.path.abspath(os.path.realpath(file_1))
    path_2 = os.path.abspath(os.path.realpath(file_2))
    path_1_split = path_1.split('/')
    path_2_split = path_2.split('/')
    path_1_pos = path_1_split.index(config.SEARCH_FOR_DROPBOX)
    path_2_pos = path_2_split.index(config.SEARCH_FOR_DROPBOX)
    new_path_1 = os.path.join(*path_1_split[path_1_pos+1:])
    new_path_2 = os.path.join(*path_2_split[path_2_pos+1:])
    
    cmd = 'dropbox.sh move "{0}" "{1}"'.format(new_path_1, new_path_2)
    os.system(cmd)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('action', choices=['get_name', 'dropbox_move', 'get_dest_path'])
    parser.add_argument('file', nargs='*')
    args = parser.parse_args()
    
    if args.action == 'get_name':
        if not args.file:
            print('Filepath needed')
            sys.exit(-1)
        torrent_file_path = os.path.abspath(os.path.realpath(*args.file))
        filename = get_torrent_name(torrent_file_path)
        print('{}.torrent'.format(filename.replace(' ', '_')))
        sys.exit(0)

    elif args.action == 'dropbox_move':
        if len(args.file) != 2:
            print('Must be two `file` args passed')
            sys.exit(-1)

        dropbox_move(*args.file)
        sys.exit(0)

    elif args.action == 'get_dest_path':
        if not args.file:
            print('Must be one torrent file')
            sys.exit(-1)

        torrent_file_path = os.path.abspath(os.path.realpath(*args.file))
        print(get_torrent_destionation_path(torrent_file_path))
        sys.exit(0)