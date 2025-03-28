# Slow-ass Disks Waker

Slow-ass Disks Waker is a script that helps synchronize files between a local and remote directory. It ensures that files are copied, duplicates are handled properly, and symbolic links are created to maintain a consistent file structure while avoiding unnecessary disk access.

### Please note: this project is not finished in its current state.

## 👀 Features

- Lists files in both local and remote directories.
- Builds a cache of file attributes to avoid redundant disk access.
- Detects and renames duplicate files to prevent overwrites.
- Removes local copies of identical files already present in the remote directory.
- Copies missing files from the local directory to the remote one.
- Creates symbolic links in the local directory pointing to the corresponding remote files.
- Deletes orphaned symbolic links if their target no longer exists in the remote directory.

## ❓ How It Works

1. **Initialize caches:** The script builds a cache of files and their attributes for both local and remote directories.
2. **Delete orphaned symlinks:** Any symbolic links in the local directory that point to missing remote files are removed.
3. **Handle duplicates:** If a file exists in both directories but has a different modification date, the local file is renamed to avoid overwriting the remote one. If the file is identical (same size and modification time), the local copy is deleted.
4. **Copy missing files:** Any files that exist locally but not remotely are copied to the remote directory, and the local copy is removed.
5. **Create symlinks:** Symbolic links are created in the local directory for files that were copied to the remote location.

## ⚡ Usage

To run the script, simply execute:

```bash
python main.py
```

By default, it operates on the following directories:
- **Local path:** `C:/users/User/Downloads/`
- **Remote path:** `D:/Downloads/`

Modify these paths in the `main()` function if needed.

## 🤔 Limitations

- The script does not currently support event-based or scheduled execution; it must be run manually.
- Error handling is minimal; issues encountered while renaming or deleting files will be logged, but the script may not recover automatically.
- No support for network-mounted drives or special file systems has been implemented.

