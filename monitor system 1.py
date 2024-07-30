import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import getpass
import shutil
import os


class BackupHandler(FileSystemEventHandler):
    """Handle file system events and perform backups."""

    def __init__(self, src_path, dest_path):
        self.src_path = src_path
        self.dest_path = dest_path
        self.file_cache = {}  # Dictionary to map source paths to backup paths

    def on_modified(self, event):
        """Handle file modifications."""
        if not event.is_directory and event.src_path in self.file_cache:
            self.backup_file(event.src_path)
            logging.info(f"File modified: {event.src_path}")

    def on_created(self, event):
        """Handle file and directory creations."""
        if event.is_directory:
            self.copy_directory(event.src_path)
            logging.info(f"Directory created: {event.src_path}")
        else:
            relative_path = os.path.relpath(event.src_path, start=self.src_path)
            backup_path = os.path.join(self.dest_path, relative_path)
            self.file_cache[event.src_path] = backup_path

            # Ensure the destination directory exists
            backup_dir = os.path.dirname(backup_path)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            self.backup_file(event.src_path)
            logging.info(f"File created: {event.src_path}")

    def on_deleted(self, event):
        """Handle file and directory deletions."""
        if event.is_directory:
            backup_path = os.path.join(self.dest_path, os.path.relpath(event.src_path, start=self.src_path))
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
                logging.info(f"Directory deleted: {event.src_path}")

            # Remove from cache
            for src_path in list(self.file_cache.keys()):
                if os.path.commonpath([src_path, event.src_path]) == event.src_path:
                    del self.file_cache[src_path]
        else:
            if event.src_path in self.file_cache:
                backup_path = self.file_cache[event.src_path]
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    logging.info(f"File deleted: {event.src_path}")
                del self.file_cache[event.src_path]

    def on_moved(self, event):
        """Handle file and directory moves/renames."""
        if event.is_directory:
            old_backup_path = os.path.join(self.dest_path, os.path.relpath(event.src_path, start=self.src_path))
            if os.path.exists(old_backup_path):
                new_backup_path = os.path.join(self.dest_path, os.path.relpath(event.dest_path, start=self.src_path))
                shutil.move(old_backup_path, new_backup_path)
                logging.info(f"Directory renamed: {event.src_path} to {event.dest_path}")

            # Update cache
            for src_path, backup_path in list(self.file_cache.items()):
                if os.path.commonpath([src_path, event.src_path]) == event.src_path:
                    new_backup_path = os.path.join(self.dest_path, os.path.relpath(src_path, start=self.src_path).replace(event.src_path, event.dest_path, 1))
                    self.file_cache[src_path] = new_backup_path
                    if not os.path.exists(new_backup_path):
                        self.backup_file(src_path)
        else:
            if event.src_path in self.file_cache:
                old_backup_path = self.file_cache[event.src_path]
                if os.path.exists(old_backup_path):
                    new_backup_path = os.path.join(self.dest_path, os.path.relpath(event.dest_path, start=self.src_path))
                    os.rename(old_backup_path, new_backup_path)
                    logging.info(f"File renamed: {event.src_path} to {event.dest_path}")

                # Update cache
                del self.file_cache[event.src_path]
                self.file_cache[event.dest_path] = new_backup_path
                self.backup_file(event.dest_path)
            else:
                new_backup_path = os.path.join(self.dest_path, os.path.relpath(event.dest_path, start=self.src_path))
                self.file_cache[event.dest_path] = new_backup_path
                self.backup_file(event.dest_path)

    def backup_file(self, source):
        """Backup a file from source to destination."""
        relative_path = os.path.relpath(source, start=self.src_path)
        destination = os.path.join(self.dest_path, relative_path)
        destination_dir = os.path.dirname(destination)

        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        if os.path.isfile(source):
            try:
                shutil.copy2(source, destination)
                logging.info(f"File backed up: {os.path.basename(source)}")
            except Exception as e:
                logging.error(f"Error copying {os.path.basename(source)}: {e}")

    def copy_directory(self, source):
        """Copy an entire directory to the backup destination."""
        dir_name = os.path.relpath(source, start=self.src_path)
        destination = os.path.join(self.dest_path, dir_name)

        if not os.path.exists(destination):
            try:
                shutil.copytree(source, destination)
                logging.info(f"Directory backed up: {dir_name}")
            except Exception as e:
                logging.error(f"Error copying directory {dir_name}: {e}")


# Set up logging configuration

user = getpass.getuser()
logging.basicConfig(
    filename="dev.log",
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - User: {user}',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define the source and destination paths
src_path = r"C:\Users\yugendra.salunke\Documents\test1\test"
dest_path = r"C:\Users\yugendra.salunke\Documents\test_backup"

# Create destination directory if it doesn't exist
if not os.path.exists(dest_path):
    os.makedirs(dest_path)

# Set up the event handler
event_handler = BackupHandler(src_path, dest_path)
observer = Observer()
observer.schedule(event_handler, src_path, recursive=True)
print("Start Observing:")
observer.start()

logging.info(f"Monitoring directory: {src_path}")

try:
    while True:
        time.sleep(10)
        # Optional: log periodically to show the script is running
        # logging.info("Monitoring in progress...")
        print("Watching...")

except KeyboardInterrupt:
    # logging.info("Stopping observer...")
    print("Stopping observing...")
    observer.stop()
    observer.join()
