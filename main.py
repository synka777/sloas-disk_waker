"""Slow-ass disks waker

Copyright (c) 2021 Mathieu BARBE-GAYET
All Rights Reserved.
Released under the MIT license

"""
import os
import shutil

local_cache = {}
remote_cache = {}


def get_folder_content(path):
    return os.listdir(path)


def build_cache(path, file_list):
    cache = {}
    stat_names = ["st_mode", "st_ino", "st_dev", "st_nlink", "st_uid", "st_gid", "st_size", "st_atime", "st_mtime",
                  "st_ctime"]
    # Get the attributes of each file, then stores the couple (file name : dictionary_of_the_file_attributes) in the cache
    for file in file_list:
        current_file_stats = os.stat(path + file)
        stats_dict = {}
        i = 0
        for value in current_file_stats:
            stats_dict[stat_names[i]] = value
            i += 1
        cache[file] = stats_dict
    return cache


def remove_from_cache(cache, files_list):
    return [cache.pop(file, None) for file in files_list]


def get_files_waiting_for_a_symlink(local, remote):
    return {file: remote[file] for file in set(remote) - set(local)}


def get_file_list_to_copy(local, remote):
    return {file: local[file] for file in set(local) - set(remote)}


def mk_link_to_local(list_to_process, local_path, remote_path):
    for file in list_to_process:
        os.symlink(remote_path+file, local_path+file)


def copy_to_remote(file_list_to_copy, local_path, remote_path):
    for file in file_list_to_copy:
        try:
            shutil.copy(local_path+file, remote_path+file)
            if os.path.exists(remote_path+file):
                os.remove(local_path+file)

        except Exception as e:
            print("Copy: Error when parsing ", file, ": ", e)


def wake_disks(vol_letter):
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

    #
    # 0/ Check if the list is empty not done for now
    #

    # Initializes and fills a set of file names for both a local and remote dir
    local_file_list = set([])
    remote_file_list = set([])
    local_file_list.update(get_folder_content(local_path))
    remote_file_list.update(get_folder_content(remote_path))
    # Builds some kind of log listing each file and it's attributes
    remote_cache.update(build_cache(remote_path, remote_file_list))
    # print("remote: ", remote_cache)

    local_cache.update((build_cache(local_path, local_file_list)))
    # print("local: ", local_cache)

    #
    # 1/ Manually started: check the difference between a local folder and it's remote counterpart
    #

    # if local len > remote len, copy local file to remote
    # else if local len < remote len, create a link in the local folder

    files_to_copy = {}
    files_to_copy = get_file_list_to_copy(local_cache, remote_cache)

    #
    # 2/ Copy the missing files to the remote directory
    # - then removes the original file
    #
    copy_to_remote(files_to_copy, local_path, remote_path)
    # Updates the local cache to include the newly copied files to the list of files that need a symlink in 3/
    # Removes the deleted files from the local cache list
    remote_cache.update(files_to_copy)
    remove_from_cache(local_cache, files_to_copy)

    #
    # 3/ Create a link to the local folder
    #
    waiting_for_a_symlink = {}
    waiting_for_a_symlink = get_files_waiting_for_a_symlink(local_cache, remote_cache)
    mk_link_to_local(waiting_for_a_symlink, local_path, remote_path)


if __name__ == '__main__':
    main()
