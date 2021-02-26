"""Slow-ass disks waker

Copyright (c) 2021 Mathieu BARBE-GAYET
All Rights Reserved.
Released under the MIT license

"""
import os
import shutil

local_files_cache = {}
remote_files_cache = {}
exclusion_list = {}


def get_files(path):
    """Lists a given folder's files, without symlinks

    :param path: String referring to the path that needs it's content to be listed
    :return: A list of files only, symlinks not included
    """
    return [file for file in os.listdir(path) if not os.path.islink(path + file)]


def get_all_elements(path):
    """Lists a given folder's files, symlinks included

    :param path: String referring to the path that needs it's content to be listed
    :return: A list of all files contained in the directory
    """
    # return [file for file in os.listdir(path)]
    files_names_cache = {}
    i = 0
    for file in os.listdir(path):
        if file not in exclusion_list:
            files_names_cache[i] = file
            i += 1
    return files_names_cache


def build_cache(path, file_list):
    """Builds a file cache to avoid browsing a given folder each time we need to know it's content

    :param path: Base folder where the files contained in the list are actually stored
    :param file_list: List of files
    :return: A dictionary containing a file name and another directory containing each file's attributes
    """
    cache = {}
    stat_names = ["st_mode", "st_ino", "st_dev", "st_nlink", "st_uid", "st_gid", "st_size", "st_atime", "st_mtime",
                  "st_ctime"]
    # Get the attributes of each file, then stores the couple (file name : dictionary_of_the_file_attributes) in the cache
    for file in file_list:
        # If the file is not in the exclusion list we add it to the cache and return it
        if file not in exclusion_list:
            current_file_stats = os.stat(path + file)
            stats_dict = {}
            i = 0
            for value in current_file_stats:
                stats_dict[stat_names[i]] = value
                i += 1
            cache[file] = stats_dict
    return cache


def remove_from_cache(cache, files_list):
    """Removes a file list from a given cache

    :param cache: Dictionary of a folder's contents
    :param files_list: A file list to remove
    :return: An updated dictionary cache
    """
    return [cache.pop(file, None) for file in files_list]


def get_files_waiting_for_a_symlink(local, remote):
    """Does the difference between two caches to determine which files will need a symlink to be created locally

    :param local: A local cache containing a file list
    :param remote: A remote cache containing a file list
    :return: The difference between the two caches
    """
    return {file: remote[file] for file in set(remote) - set(local.values())}


def rename_duplicates(local_path, local, remote):
    """This function will avoid to override different files that have the same file name.
    Will search for duplicates file names in the local and remote folder;
    If a file name is found in both folders, we first check if the last modification date is the same or not.
    If both dates are not the same, we rename the local file to avoid the remote one to be overridden.
    Else if the last modification date and the file size are the same, we are sure the files are the same so
    we can delete the local copy of the file.

    :param local_path: Base folder where the files contained in the local list are actually stored
    :param local: A local cache containing a file list
    :param remote: A remote cache containing a file list
    :return: A boolean that will be used later to know if we need to create an up-to-date local cache or not
    """
    need_to_rebuild_cache = False
    for local_file in local:
        if local_file in remote:
            print("Duplicate found! : ", local_file)
            absolute_path_to_local_file = str(local_path) + str(local_file)
            local_file_last_edit = local[local_file]['st_mtime']
            remote_file_last_edit = remote[local_file]['st_mtime']
            # If the files don't have the same last edition date, we try to rename the local one to avoid a file override
            if local_file_last_edit != remote_file_last_edit:
                try:
                    split = (local_file.split("."))
                    file_name = ".".join(split[0:-1])
                    file_type = split[-1]
                    absolute_path_after_rename = str(local_path)+file_name+'.'+str(local[local_file]['st_mtime'])+"."+file_type
                    os.rename(r''+absolute_path_to_local_file, r''+absolute_path_after_rename)
                except Exception as e:
                    # If for some reason we can't rename the file, we put it on the exclusion list
                    try:
                        print("Rename file: Error when parsing ", local_file, ": ", e)
                        exclusion_list.update(local_file)
                        need_to_rebuild_cache = True
                    except Exception as e:
                        print("Add to exclusion list: Error when parsing ", local_file, ": ", e)
            else:
                local_file_size = local[local_file]['st_size']
                remote_file_size = remote[local_file]['st_size']
                # Else if both files have the same size and last modification date, we remove the local copy
                # as we are sure both files are the same
                if (remote_file_last_edit == local_file_last_edit) and (remote_file_size == local_file_size):
                    os.remove(absolute_path_to_local_file)
                # Else, nothing happens the file stays where it is for now
    return need_to_rebuild_cache


def delete_orphan_links(local_path, local, remote):
    """Checks if the local symlinks are referring to a remote file.
    If the targeted file doesn't exist anymore, we delete the link.

    :param local_path: Base folder where the local files contained in the list are actually stored
    :param local: A local cache containing a file list
    :param remote: A remote cache containing a file list
    :return: Void
    """
    for file in local:
        absolute_path_to_file = str(local_path)+str(local[file])
        if os.path.islink(absolute_path_to_file) and file not in remote:
            try:
                os.remove(absolute_path_to_file)
            except Exception as e:
                # If for some reason we can't rename the file, we put it on the exclusion list
                exclusion_list.update(file)
                print("Delete orphan link: Error when parsing ", file, ": ", e)


def get_file_list_to_copy(local, remote):
    """Creates a file list to copy

    :param local: A local cache containing a file list
    :param remote: A remote cache containing a file list
    :return: A file list to copy
    """
    return {file: local[file] for file in set(local) - set(remote)}


def mk_link_to_local(list_to_process, local_path, remote_path):
    """Creates symbolic links locally, with a remote file as the target

    :param list_to_process: A file list that needs to get a symbolic link created locally
    :param local_path: Base folder where the files contained in the local list are actually stored
    :param remote_path:Base folder where the files contained in the remote list are actually stored
    :return: Void
    """
    for file in list_to_process:
        try:
            os.symlink(remote_path + file, local_path + file)
        except Exception as e:
            print("Make symlink: Error when parsing ", file, ": ", e)


def copy_to_remote(file_list_to_copy, local_path, remote_path):
    """Copies a local file to a given remote location

    :param file_list_to_copy: A file list that will be copied to a remote folder
    :param local_path: Base folder where the files contained in the local list are actually stored
    :param remote_path: Base folder where the files contained in the remote list are actually stored
    :return: Void
    """
    for file in file_list_to_copy:
        try:
            shutil.copy(local_path + file, remote_path + file)
            if os.path.exists(remote_path + file):
                os.remove(local_path + file)
        except Exception as e:
            print("Copy: Error when parsing ", file, ": ", e)


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
    local_file_list = set(get_files(local_path))
    remote_file_list = set(get_files(remote_path))
    # Builds some kind of log listing each file and it's attributes
    local_files_cache.update((build_cache(local_path, local_file_list)))
    remote_files_cache.update(build_cache(remote_path, remote_file_list))

    delete_orphan_links(local_path, get_all_elements(local_path), remote_files_cache)

    #
    # 1/ Manually started: check the difference between a local folder and it's remote counterpart
    #

    # Checks if some files exist on both locations and then tries to rename it.
    # If it works for at least one file, we rebuild the cache with the current content from the local folder.
    if rename_duplicates(local_path, local_files_cache, remote_files_cache):
        local_file_list.clear()
        local_files_cache.clear()
        local_file_list.update(get_files(local_path))
        local_files_cache.update((build_cache(local_path, local_file_list)))

    files_to_copy = dict(get_file_list_to_copy(local_files_cache, remote_files_cache))

    #
    # 2/ Copy the missing files to the remote directory
    # - then removes the original file

    copy_to_remote(files_to_copy, local_path, remote_path)
    # Updates the local cache to include the newly copied files to the list of files that need a symlink in 3/
    # Removes the deleted files from the local cache list
    remote_files_cache.update(files_to_copy)
    remove_from_cache(local_files_cache, files_to_copy)

    #
    # 3/ Create a link to the local folder
    #

    # Create a list of ALL files names (w/ symlinks), then compare it with the remote folder's content
    waiting_for_a_symlink = dict(get_files_waiting_for_a_symlink(get_all_elements(local_path), remote_files_cache))

    # Then pass the list of files that needs a symlink to the function that will create it
    mk_link_to_local(waiting_for_a_symlink, local_path, remote_path)


if __name__ == '__main__':
    main()
