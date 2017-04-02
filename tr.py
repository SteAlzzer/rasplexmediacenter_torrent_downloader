import os
import sys
from argparse import ArgumentParser

SEARCH_FOR_NAME = 'Name:'
SEARCH_FOR_DROPBOX = 'Dropbox'
TR_SHOW = 'transmission-show'
TMP_FILE = '/tmp/tr_tmp.log'


def _remove_tmp_file():
    if os.path.exists(TMP_FILE):
        os.remove(TMP_FILE)


def get_torrent_name(torrent_path):
    _remove_tmp_file()
    cmd = '{0} "{1}" >> "{2}"'.format(TR_SHOW, torrent_path, TMP_FILE)
    os.system(cmd)

    torrent_name = ''
    for line in open(TMP_FILE):
        if SEARCH_FOR_NAME in line:
            torrent_name = line.split(SEARCH_FOR_NAME)[1].strip().rstrip('\r\n')
            break
    _remove_tmp_file()
    return torrent_name


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('action', choices=['get_name', 'dropbox_move'])
    parser.add_argument('file', nargs='*')
    args = parser.parse_args()
    
    if args.action == 'get_name':
        if not args.file:
            print('Filepath needed')
            sys.exit(-1)
        torrent_file_path = os.path.abspath(os.path.realpath(args.file[0]))
        filename = get_torrent_name(torrent_file_path)
        print('{}.torrent'.format(filename.replace(' ', '_')))
        sys.exit(0)

    if args.action == 'dropbox_move':
        if len(args.file) != 2:
            print('Must be two `file` args passed')
            sys.exit(-1)

        path_1 = os.path.abspath(os.path.realpath(args.file[0]))
        path_2 = os.path.abspath(os.path.realpath(args.file[1]))
        path_1_split = path_1.split('/')
        path_2_split = path_2.split('/')
        path_1_pos = path_1_split.index(SEARCH_FOR_DROPBOX)
        path_2_pos = path_2_split.index(SEARCH_FOR_DROPBOX)
        new_path_1 = os.path.join(*path_1_split[path_1_pos+1:])
        new_path_2 = os.path.join(*path_2_split[path_2_pos+1:])
        
        cmd = 'dropbox.sh move "{0}" "{1}"'.format(new_path_1, new_path_2)
        os.system(cmd)
        sys.exit(0)
