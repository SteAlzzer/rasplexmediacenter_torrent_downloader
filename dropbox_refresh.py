#!/usr/bin/env python3

import sys
import os
import dropbox

DROPBOX_TOKEN = 'UnvKF8jf57AAAAAAAAAACUb0cmdcJk8ga4Y_VN3-B8qolM7CO1Jh10wDri7Aw9zw' #rasplex
# DROPBOX_TOKEN = 'iIk7xrg4TUsAAAAAAAAKE761j2JlHWCNsdBPY0a6-YB13Sv1dRCL3GG0icpw8r-r'
DROPBOX_FOLDER = '/Users/SteAlzzer/Desktop/drop_text/'

def list_folder_dropbox(dbx, path):
    rv = {}
    result = dbx.files_list_folder(path=path, recursive=False)

    for entry in result.entries:
        rv[entry.path_display] = entry
        if not isinstance(entry, dropbox.files.FileMetadata): # if entry is folder
            tmp_res = list_folder_dropbox(dbx, entry.path_display)
            rv.update(tmp_res)
    return rv

def print_tree_of_entries(dict_of_entries, show_type=True, only_files=False):
    for item in dict_of_entries:
        if show_type:
            if isinstance(dict_of_entries[item], dropbox.files.FileMetadata):
                print('[f]', end='')
            else:
                print('[d]', end='')
        if only_files:
            if isinstance(dict_of_entries[item], dropbox.files.FileMetadata):
                print(item)
        else:
            print(item)

def list_folder_local(path):
    files = []

    if not os.path.exists(path):
        return []

    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(dirname, filename))
    return files

def sync_local_folder(dbx, local_folder, selective_sync=[]):
    dropbox_files = list_folder_dropbox(dbx, '')
    local_files = list_folder_local(local_folder)
    if local_files == []:
        print(u'[dropbox_refresh.py] >> Dropbox folder is not created. Doing sync...')
        for file in dropbox_files:
            if isinstance(dropbox_files[file], dropbox.files.FileMetadata):
                print(u'[dropbox_refresh.py] >> Downloading {}...'.format(file))
                print(dropbox_files[file])
                input()
                download_file_to_file(dbx, file, local_folder)
    else:
        pass            

def get_mtime_local(file):
    return os.path.getmtime(file)


def download_file(dbx, filepath):
    try:
        md, res = dbx.files_download(filepath)
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None
    data = res.content
    print(len(data), 'bytes; md:', md)
    return data

def download_file_to_file(dbx, dropbox_filepath, local_dir):
    local_file = os.path.join(local_dir, dropbox_filepath.strip('/'))
    local_file_dir = os.path.dirname(local_file)
    if not os.path.exists(local_dir):
        os.makedirs(local_file_dir)

    try:
        # md, res = dbx.files_download_to_file(local_file, dropbox_filepath)
        md, res = dbx.files_download(dropbox_filepath)
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None

    try:
        with open(local_file, 'wb') as lf:
            lf.write(res.content)
    except:
        print('Unexpected filesystem behaviour')

    return res.content

if __name__ == '__main__':
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    # Check that the access token is valid
    try:
        (dbx.users_get_current_account())
    except AuthError as err:
        sys.exit("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")

    # result = list_folder_dropbox(dbx, '')

    # print_tree_of_entries(result, show_type=False, only_files=True)
    sync_local_folder(dbx, local_folder=DROPBOX_FOLDER)
    # list_folder_local(DROPBOX_FOLDER)





