import os


DROPBOX_SCRIPT = 'dropbox.sh'
DROPBOX_LOCAL_FOLDER = '/media/Dropbox/'
DROPBOX_LOCAL_FILE_LIST = {}

TRANSMISSION_SHOW = 'transmission-show'
TMP_FILE = '/tmp/tbox.tmp'

DELAY = 60*2  # 2 min

def list_folder(folder):
	files = []
	for root, dirname, filenames in os.walk(folder):
		for filename in filenames:
			filepath = os.path.join(root, filename)
			files.append(filepath)
	return files


def dropbox_check_new_files():
	dropbox_download_files()
	new_files = []
	for file in list_folder(DROPBOX_LOCAL_FOLDER):
		rel_file = os.path.relpath(file, DROPBOX_LOCAL_FOLDER)
		if rel_file not in DROPBOX_LOCAL_FILE_LIST:
			new_files.append(file)
			continue
		else:
			if os.path.getsize(file) is not DROPBOX_LOCAL_FILE_LIST[rel_file]['size'] or
			   os.path.getmtime(file) is not DROPBOX_LOCAL_FILE_LIST[rel_file]['mtime']:
				new_files.append(file)
				continue

	return new_files

def dropbox_download_files():
	command = '"{}"" -s download / "{}"'.format(DROPBOX_SCRIPT, DROPBOX_LOCAL_FOLDER)
	os.system(command)


def dropbox_upload_file(dropbox_folder, local_file, dest_file):
	pass


def dropbox_move_file(source_file, dest_file):
	source_file_rel = os.path.relpath(source_file, DROPBOX_LOCAL_FOLDER)	
	dest_file_rel = os.path.relpath(dest_file, DROPBOX_LOCAL_FOLDER)

	command = '"{}" move "{}" "{}"'.format(DROPBOX_SCRIPT, source_file_rel, dest_file_rel)
	os.system(command)

def dropbox_update_local_filelist(dropbox_files_list, files_to_update):
	pass


def torrent_get_real_filename(torrent_file):
	# todo: change ">>" for PIPES
	command = '"{}" "{}" | grep -oP "^Name:\s?\K.*" >> "{}"'.format(TRANSMISSION_SHOW, torrent_file, TMP_FILE)
	os.system(command)
	with open(TMP_FILE) as f:
		real_name = f.readline().strip()
	remove_tmp_file()
	return real_name


def remove_tmp_file(tries=10):
	try:
		os.remove(TMP_FILE)
	except:
		if tries:
			time.sleep(1)
			remove_tmp_file(tries-1)
		else:
			print('Unable to remove tmp_file!')
			exit(-1)


def torrent_add_file(torrent_file, dest_folder):
	pass


def is_file_torrent(file):
	# todo: get some real shit
	return os.path.splitext[1] is '.torrent'


def is_file_cmd(file):
	return False


def rename_file(orig_file, dest_file):
	os.rename(orig_file, dest_file)


def get_dest_path_for_torrent_file(torrent_file):
	pass


def main_cycle():
	while True:
		new_files = dropbox_check_new_files(dropbox_folder, dropbox_files_list):

		if new_files:
			for file in new_files:
				if is_file_torrent(file):
					original_file = torrent_get_real_filename(file)
					rename_file(file, original_file)
					dropbox_move_file(file, original_file)
					dest_path = get_dest_path_for_torrent_file(original_file)
					torrent_add_file(original_file, dest_path)
				elif is_file_cmd(file):
					pass

				dropbox_update_local_filelist(dropbox_files_list, file)

		sleep(DELAY)

def main():
	remove_tmp_file()
	main_cycle()

if __name__ == '__main__':
	main()