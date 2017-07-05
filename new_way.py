#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time

FOLDERS_MAP_STRUCTURE = {
    'TV Shows': '/media/library/Downloads/TV Shows/',
    'Films': '/media/library/Downloads/Films/',
    'Music': '/media/library/Downloads/Music/',
    'Games': '/media/library/Downloads/Games/',
    'Others': '/media/library/Downloads/Torrents_Downloads/'
    # todo: add auto_detection of new folders in Dropbox
}

DROPBOX_SCRIPT = 'dropbox.sh'
DROPBOX_LOCAL_FOLDER = '/media/Dropbox/'
DROPBOX_TORRENT_FOLDER = 'sharefolder/Torrents/'
DROPBOX_LOCAL_FILE_LIST = {}
DROPBOX_LOCAL_FILE_LIST_BACKUP = '~/.dropboxlocalfilelist.tbox'

TMP_FILE = '/tmp/tbox.tmp'

DELAY = 60 * 2  # 2 min


def list_folder(folder):
    files = []
    for root, dirname, filenames in os.walk(folder):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            files.append(filepath)
    return files


def dropbox_check_new_files():
    print('Скачиваем файлы с dropbox')
    dropbox_download_files()
    new_files = []
    for file in list_folder(DROPBOX_LOCAL_FOLDER):
        rel_file = os.path.relpath(file, DROPBOX_LOCAL_FOLDER)
        if rel_file not in DROPBOX_LOCAL_FILE_LIST:
            print('Обнаружен новый файл', rel_file)
            new_files.append(file)
            continue
        else:
            if os.path.getsize(file) is not DROPBOX_LOCAL_FILE_LIST[rel_file]['size'] or os.path.getmtime(file) is not DROPBOX_LOCAL_FILE_LIST[rel_file]['mtime']:
                print('Метаданные файла изменились', file, os.path.getsize(file), os.path.getmtime(file))
                new_files.append(file)
                continue

    return new_files


def dropbox_download_files():
    command = '"{}"" -s download / "{}"'.format(DROPBOX_SCRIPT, DROPBOX_LOCAL_FOLDER)
    os.system(command)


def dropbox_move_file(source_file, dest_file):
    print('Перемещаем файл в dropbox', source_file, dest_file)
    source_file_rel = os.path.relpath(source_file, DROPBOX_LOCAL_FOLDER)
    dest_file_rel = os.path.relpath(dest_file, DROPBOX_LOCAL_FOLDER)

    command = '"{}" move "{}" "{}"'.format(DROPBOX_SCRIPT, source_file_rel, dest_file_rel)
    print('Выполняем команду', command)
    os.system(command)


def dropbox_update_local_filelist(file_to_update):
    print('Обновим список отмониторенных файлов')
    rel_file = os.path.relpath(file_to_update, DROPBOX_LOCAL_FOLDER)
    if rel_file not in DROPBOX_LOCAL_FILE_LIST:
        print('Такого файла раньше не было!', rel_file)
        DROPBOX_LOCAL_FILE_LIST[rel_file] = {}
    DROPBOX_LOCAL_FOLDER[rel_file]['size'] = os.path.getsize(file_to_update)
    DROPBOX_LOCAL_FOLDER[rel_file]['mtime'] = os.path.getmtime(file_to_update)


def dropbox_save_local_filelist():
    print('Сохраним мониторинг файлов в файл')
    with open(DROPBOX_LOCAL_FILE_LIST_BACKUP, 'w') as bkp:
        for key, value in DROPBOX_LOCAL_FILE_LIST.items():
            line = '"{}":{};{};\n'.format(key, value['size'], value['mtime'])
            bkp.write(line)


def dropbox_load_local_filelist():
    print('Загружаем сохраненный перечень файлов')
    if not os.path.isfile(DROPBOX_LOCAL_FILE_LIST_BACKUP):
        print('Файла не существует!')
        return

    for line in open(DROPBOX_LOCAL_FILE_LIST_BACKUP):
        key, value = line.split(':')
        size, mtime, _ = value.split(';')
        DROPBOX_LOCAL_FILE_LIST[key] = {'size': size, 'mtime': mtime}


def torrent_get_real_filename(torrent_file):
    # todo: change ">>" for PIPES
    print('Получаем нормальное имя для файла', torrent_file)
    command = 'transmission-show "{}" | grep -oP "^Name:\s?\K.*" >> "{}"'.format(torrent_file, TMP_FILE)
    os.system(command)
    print('Выполнили команду')
    with open(TMP_FILE) as f:
        real_name = f.readline().strip() + '.torrent'
        torrent_dir = os.path.split(torrent_file)[0]
        real_fullname = os.path.join(torrent_dir, real_name)
    remove_tmp_file()
    print('Получили имя файла', real_fullname)
    return real_fullname


def torrent_check_daemon():
    pass


def remove_tmp_file(tries=10):
    print('Удаляем временный файл', tries)
    try:
        if os.path.isfile(TMP_FILE):
            os.remove(TMP_FILE)
            print('Удалили!')
    except:
        if tries:
            time.sleep(1)
            remove_tmp_file(tries - 1)
        else:
            print('Unable to remove tmp_file!')
            exit(-1)


def torrent_add_file(torrent_file, dest_folder):
    command = 'transmission-remote -n "tr:tr" --add "{}" -w "{}"'.format(torrent_file, dest_folder)
    print('Добавляем файл в торрент командой', command)
    os.system(command)


def is_file_torrent(file):
    # todo: get some real shit
    return os.path.splitext[1] is '.torrent'


def is_file_cmd(file):
    return False


def rename_file(orig_file, dest_file):
    print('Переименовываем файл', orig_file, dest_file)
    os.rename(orig_file, dest_file)


def get_dest_path_for_torrent_file(torrent_file):
    print('Получаем пункт назначения для файла')
    dropbox_torrent_folder_path = os.path.join(DROPBOX_LOCAL_FOLDER, DROPBOX_TORRENT_FOLDER)
    torrent_file_rel = os.path.join(torrent_file, dropbox_torrent_folder_path)
    print('Относительный путь для файла:', torrent_file_rel)
    for folder_name in FOLDERS_MAP_STRUCTURE.keys():
        if folder_name in torrent_file_rel:
            print('Вот что нашли', FOLDERS_MAP_STRUCTURE[folder_name])
            return FOLDERS_MAP_STRUCTURE[folder_name]


def main_cycle():
    print('Запукаем оновной цикл')
    while True:
        new_files = dropbox_check_new_files()

        if new_files:
            for file in new_files:
                if is_file_torrent(file):
                    original_file = torrent_get_real_filename(file)
                    rename_file(file, original_file)
                    dropbox_move_file(file, original_file)
                    dest_path = get_dest_path_for_torrent_file(file)
                    if not dest_path:
                        print('! Strange: for {} releated folder not found'.format(file))
                        dest_path = FOLDERS_MAP_STRUCTURE['Others']
                    torrent_add_file(original_file, dest_path)
                elif is_file_cmd(file):
                    pass

                dropbox_update_local_filelist(file)
            dropbox_save_local_filelist()
        print('Подождём')
        time.sleep(DELAY)


def main():
    print('Запускаемся')
    remove_tmp_file()
    torrent_check_daemon()
    dropbox_load_local_filelist()
    main_cycle()


if __name__ == '__main__':
    main()
