"""Slow-ass disks waker

Copyright (c) 2021 Mathieu BARBE-GAYET
All Rights Reserved.
Released under the MIT license

"""
import os

local_cache = {}
remote_cache = {}


def get_folder_content(path):
    return os.listdir(path)


def build_cache(path, file_list):
    cache = {}
    stat_names = ["st_mode", "st_ino", "st_dev", "st_nlink", "st_uid", "st_gid", "st_size", "st_atime", "st_mtime", "st_ctime"]
    # Get the attributes of each file, then stores the couple (file name : dictionary_of_the_file_attributes) in the cache
    for file in file_list:
        current_file_stats = os.stat(path+file)
        stats_dict = {}
        i = 0
        for value in current_file_stats:
            stats_dict[stat_names[i]] = value
            i += 1
        cache[file] = stats_dict
    return cache


def wake_disks(vol_letter):
    pass


def copy_to_folder(file, folder):
    pass


def create_links():
    pass


def synchronized():
    pass


def main():
    """The main function
    0/ If the cached list of remote folder's content is empty, get the list
    1/ Checks on event triggering or at fixed intervals if the local folder has the same content as the remote one.
        The comparison will be done on a cached list of the remote folder's content.
    2/ If some files are missing in the remote folder, copy it to the remote one
    3/ Then, create a link from the remote file to the local folder
    4/ Delete the original file from the local folder
    """
    local_path = "C:/users/Dope/Downloads/"
    remote_path = "D:/Downloads/"
    # Initializes and fill a set of file names for both a local and remote dir
    local_file_list = set([])
    remote_file_list = set([])
    local_file_list.update(get_folder_content(local_path))
    remote_file_list.update(get_folder_content(remote_path))
    # Builds some kind of log listing each file and it's attributes
    remote_cache.update(build_cache(remote_path, remote_file_list))
    print("remote: ", remote_cache)

    local_cache.update((build_cache(local_path, local_file_list)))
    print("local: ", local_cache)


if __name__ == '__main__':
    main()
