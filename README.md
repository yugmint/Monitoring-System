---

# Directory Backup Monitor

This script monitors a specified directory and automatically backs up files and directories to a designated backup location. It uses the `watchdog` library to track file system events such as file creation, modification, deletion, and renaming.

## Features

- **File and Directory Monitoring**: Detects changes in files and directories.
- **Automatic Backup**: Automatically backs up new and modified files and directories.
- **Handle Renaming and Moving**: Properly handles file and directory renaming and moving.
- **Log Errors**: Logs errors to a file for troubleshooting.

## Installation

### Prerequisites

- Python 3.x
- `watchdog` library

You can install the required Python package using `pip`:

```bash
pip install watchdog
```

## Usage

1. **Clone the Repository**

   Clone this repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   ```

2. **Setup Paths**

   Edit the script to specify the source (`path`) and destination (`dest_path`) directories. Replace the placeholder paths with the directories you want to monitor and back up:

   ```python
   path = r"C:\Users\yourusername\Documents\source_directory"
   dest_path = r"C:\Users\yourusername\Documents\backup_directory"
   ```

3. **Run the Script**

   Run the script using Python:

   ```bash
   python monitor_backup.py
   ```

   This will start monitoring the specified source directory and back up changes to the destination directory.

## Script Details

### `BackupHandler`

- **`on_created(event)`**: Handles creation of files and directories. Adds new files to the cache and backs them up. Creates new directories in the backup.
- **`on_modified(event)`**: Handles modifications to existing files. Backs up modified files.
- **`on_deleted(event)`**: Handles deletion of files and directories. Removes corresponding files or directories from the backup and updates the cache.
- **`on_moved(event)`**: Handles renaming or moving of files and directories. Updates backup paths and cache accordingly.

### Logging

Errors during backup operations are logged to `dev.log` for later review.

## Troubleshooting

- **File/Directory Not Backed Up**: Ensure that the source and destination paths are correctly set. Check if the file or directory is properly cached.
- **Errors in `dev.log`**: Review the log file for specific error messages and adjust the script or file permissions as needed.

## Contributing

Feel free to fork the repository, create a branch, and submit pull requests. Contributions to improve the functionality and reliability of this script are welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
