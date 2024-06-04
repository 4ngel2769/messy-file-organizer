###########################################
##       Download FIle Organizer         ##
##     The path to learning python       ##
##                                       ##
## angeldev0                             ##
###########################################

import os
import shutil
import json
import logging
import argparse
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

# Configure logging
def configure_logging(log_to_file, log_file_path):
    logging.basicConfig(
        filename=log_file_path if log_to_file else None,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger()
    return logger

# Load config from config.json
def load_config(config_path):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration file: {e}")
        exit(1)

# Create backup of configuration file
def backup_config(config_path):
    try:
        backup_path = config_path + ".bak"
        shutil.copy(config_path, backup_path)
        logger.info(f"Backup of configuration file created at: {backup_path}")
    except Exception as e:
        logger.error(f"Failed to create backup of configuration file: {e}")

# Create necessary folders if they don't exist
def create_folders(config):
    for folder in config['folders'].values():
        os.makedirs(folder, exist_ok=True)

# Function to handle file name conflicts
def get_unique_file_path(destination, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    new_file_path = os.path.join(destination, filename)
    while os.path.exists(new_file_path):
        new_file_path = os.path.join(destination, f"{base} ({counter}){extension}")
        counter += 1
    return new_file_path

# Function to categorize and move files with retries
def move_file(file_path, config):
    _, extension = os.path.splitext(file_path)
    destination = config['folders']['Other']
    category = 'Other'
    
    for cat, extensions in config['file_types'].items():
        if extension in extensions:
            destination = config['folders'][cat]
            category = cat
            break

    attempts = 0
    while attempts < config['retry_attempts']:
        try:
            unique_file_path = get_unique_file_path(destination, os.path.basename(file_path))
            shutil.move(file_path, unique_file_path)
            logger.info(f"Moved file: {file_path} to {unique_file_path}")
            if config['notifications']:
                notification.notify(
                    title="File Moved",
                    message=f"{os.path.basename(file_path)} moved to {category}",
                    timeout=5
                )
            break
        except Exception as e:
            attempts += 1
            logger.error(f"Failed to move file: {file_path}. Attempt {attempts} of {config['retry_attempts']}. Reason: {e}")
            sleep(config['retry_delay'])
    else:
        logger.error(f"Exhausted all retry attempts for file: {file_path}")

# Event handler for watchdog
class DownloadEventHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config

    def on_created(self, event):
        if not event.is_directory:
            move_file(event.src_path, self.config)

# Main function to set up the observer
def main():
    parser = argparse.ArgumentParser(description="Monitor and organize your Downloads folder.")
    parser.add_argument('-c', '--config', type=str, default=os.path.join(os.path.dirname(__file__), 'config.json'), help='Path to the configuration file')
    parser.add_argument('-l', '--log_to_file', action='store_true', help='Enable logging to file')
    parser.add_argument('-lf', '--log_file_path', type=str, default='file_organizer.log', help='Path to the log file')
    parser.add_argument('-d', '--downloads_folder', type=str, help='Path to the Downloads folder')
    parser.add_argument('-n', '--notifications', action='store_true', help='Enable desktop notifications')
    parser.add_argument('-ra', '--retry_attempts', type=int, help='Number of retry attempts for file operations')
    parser.add_argument('-rd', '--retry_delay', type=int, help='Delay between retry attempts in seconds')
    args = parser.parse_args()

    global logger
    logger = configure_logging(args.log_to_file, args.log_file_path)
    
    config = load_config(args.config)
    backup_config(args.config)

    # Override config values with CLI arguments if provided
    if args.downloads_folder:
        config['downloads_folder'] = args.downloads_folder
    if args.notifications:
        config['notifications'] = args.notifications
    if args.retry_attempts is not None:
        config['retry_attempts'] = args.retry_attempts
    if args.retry_delay is not None:
        config['retry_delay'] = args.retry_delay

    create_folders(config)

    event_handler = DownloadEventHandler(config)
    observer = Observer()
    observer.schedule(event_handler, config['downloads_folder'], recursive=False)

    observer.start()
    logger.info("Monitoring Downloads folder for new files...")

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
