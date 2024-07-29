import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import getpass
import shutil
import os


class BackupHandler(FileSystemEventHandler):
    """Handle file system events and perform backups."""

    def __init__(self, dest_path):
        self.dest_path = dest_path
        self.file_cache = {}  # Dictionary to map source paths to backup paths

    def on_modified(self, event):
        """Handle file modifications."""
        if event.is_directory:
            return
        # Check if the file is in the cache
        if event.src_path in self.file_cache:
            self.backup_file(event.src_path)

    def on_created(self, event):
        """Handle file and directory creations."""
        if event.is_directory:
            self.copy_directory(event.src_path)
        else:
            # Add new file to the cache and backup
            backup_path = os.path.join(self.dest_path, os.path.relpath(event.src_path, start=path))
            self.file_cache[event.src_path] = backup_path
            self.backup_file(event.src_path)

    def on_deleted(self, event):
        """Handle file and directory deletions."""
        if event.is_directory:
            # Handle directory deletion
            backup_path = os.path.join(self.dest_path, os.path.relpath(event.src_path, start=path))
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)  # Remove the directory from the backup
                print(f"Directory deleted: {event.src_path}")
            # Remove from cache
            for src_path in list(self.file_cache.keys()):
                if os.path.commonpath([src_path, event.src_path]) == event.src_path:
                    del self.file_cache[src_path]
        else:
            # Handle file deletion
            if event.src_path in self.file_cache:
                backup_path = self.file_cache[event.src_path]
                if os.path.exists(backup_path):
                    os.remove(backup_path)  # Remove the file from the backup
                    print(f"File deleted: {event.src_path}")
                del self.file_cache[event.src_path]

    def on_moved(self, event):
        """Handle file and directory moves/renames."""
        if event.is_directory:
            # Handle directory rename/move
            old_backup_path = os.path.join(self.dest_path, os.path.relpath(event.src_path, start=path))
            if os.path.exists(old_backup_path):
                shutil.move(old_backup_path, os.path.join(self.dest_path, os.path.relpath(event.dest_path, start=path)))
                print(f"Directory renamed: {event.src_path} to {event.dest_path}")

            # Update cache
            for src_path, backup_path in list(self.file_cache.items()):
                if os.path.commonpath([src_path, event.src_path]) == event.src_path:
                    new_backup_path = os.path.join(self.dest_path, os.path.relpath(src_path, start=path).replace(event.src_path, event.dest_path, 1))
                    self.file_cache[src_path] = new_backup_path
                    if not os.path.exists(new_backup_path):
                        self.backup_file(src_path)
        else:
            # Handle file rename/move
            if event.src_path in self.file_cache:
                old_backup_path = self.file_cache[event.src_path]
                if os.path.exists(old_backup_path):
                    os.rename(old_backup_path, os.path.join(self.dest_path, os.path.basename(event.dest_path)))
                    print(f"File renamed: {event.src_path} to {event.dest_path}")

                # Update cache
                del self.file_cache[event.src_path]
                self.file_cache[event.dest_path] = os.path.join(self.dest_path, os.path.basename(event.dest_path))
                self.backup_file(event.dest_path)
            else:
                # If the source path wasn't in cache, add the new path
                self.file_cache[event.dest_path] = os.path.join(self.dest_path, os.path.basename(event.dest_path))
                self.backup_file(event.dest_path)

    def backup_file(self, source):
        """Backup a file from source to destination."""
        file_name = os.path.basename(source)
        destination = os.path.join(self.dest_path, file_name)

        if os.path.isfile(source):
            try:
                shutil.copy2(source, destination)
                print(f"Copy Done: {file_name}")
            except Exception as e:
                print(f"Error copying {file_name}: {e}")
                logging.error(f"Error copying {file_name}: {e}")

    def copy_directory(self, source):
        """Copy an entire directory to the backup destination."""
        dir_name = os.path.relpath(source, start=path)
        destination = os.path.join(self.dest_path, dir_name)

        if not os.path.exists(destination):
            try:
                shutil.copytree(source, destination)
                print(f"Directory Backup Done: {dir_name}")
            except Exception as e:
                print(f"Error copying directory {dir_name}: {e}")
                logging.error(f"Error copying directory {dir_name}: {e}")
        else:
            print(f"Directory already exists: {dir_name}")

# Get user information for logging
user = getpass.getuser()

# Set up logging configuration
logging.basicConfig(
    filename="dev.log",
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(process)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define the source and destination paths
path = r"C:\Users\yugendra.salunke\Documents\test1\test"
dest_path = r"C:\Users\yugendra.salunke\Documents\test_backup"

# Create destination directory if it doesn't exist
if not os.path.exists(dest_path):
    os.makedirs(dest_path)

# Set up the event handler
event_handler = BackupHandler(dest_path)
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

print(f"Monitoring directory: {path}")

try:
    while True:
        time.sleep(10)
        print("Watching...")

except KeyboardInterrupt:
    print("Stopping observer...")
    observer.stop()
    observer.join()
