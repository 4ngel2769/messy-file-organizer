###########################################
##       Download File Organizer         ##
##     The path to learning python       ##
##                                       ##
## angeldev0                             ##
###########################################

import os
import shutil
import json
import logging
import argparse
import platform
import sys
import subprocess
from time import sleep
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from plyer import notification
import winreg as reg  # For auto-start functionality on Windows

# Configure logging
def configure_logging(log_to_file, log_file_path, log_level):
    logging.basicConfig(
        filename=log_file_path if log_to_file else None,
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
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
    if extension == '.tmp' or file_path.endswith('~'):
        logger.info(f"Ignored temporary file: {file_path}")
        return  # Ignore .tmp files and temporary files ending with ~

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
                    message=f"File: {os.path.basename(file_path)}\nCategory: {category}\nDestination: {unique_file_path}",
                    timeout=10
                )
            break
        except FileNotFoundError:
            attempts += 1
            logger.warning(f"File not found: {file_path}. Attempt {attempts} of {config['retry_attempts']}. Retrying...")
            sleep(config['retry_delay'])
        except Exception as e:
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
            # Add a delay to ensure the file is fully downloaded
            sleep(5)
            move_file(event.src_path, self.config)

# Function to get the default downloads folder based on OS
def get_default_downloads_folder():
    if platform.system() == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    elif platform.system() == 'Darwin':  # macOS
        return os.path.join(os.environ['HOME'], 'Downloads')
    else:  # Linux and other UNIX-like systems
        return os.path.join(os.environ['HOME'], 'Downloads')

# Function to create an icon for the system tray
def create_image():
    # Generate an image and draw a pattern
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=(255, 0, 0))
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=(255, 0, 0))
    return image

# Functions for system tray menu actions
def stop(icon, item):
    observer.stop()
    icon.stop()
    sys.exit()

def show_about(icon, item):
    notification.notify(
        title="Download File Organizer",
        message="Download File Organizer\nVersion 1.0.0\nThe path to learning python\nangeldev0",
        timeout=10
    )

def open_config(icon, item):
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if platform.system() == 'Windows':
        os.startfile(config_path)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.call(['open', config_path])
    else:  # Linux and other UNIX-like systems
        subprocess.call(['xdg-open', config_path])

def toggle_monitoring(icon, item):
    global monitoring
    if monitoring:
        observer.stop()
        item.text = "Resume Monitoring"
        monitoring = False
        logger.info("Monitoring paused.")
    else:
        observer.start()
        item.text = "Pause Monitoring"
        monitoring = True
        logger.info("Monitoring resumed.")

def reload_config(icon, item):
    global config
    config = load_config(config_path)
    create_folders(config)
    logger.info("Configuration reloaded.")
    notification.notify(
        title="Download File Organizer",
        message="Configuration reloaded successfully.",
        timeout=10
    )

def enable_autostart():
    pth = os.path.dirname(os.path.realpath(__file__))
    s_name = "DownloadFileOrganizer"
    address = os.path.join(pth, "download_file_organizer.exe")
    
    key = reg.HKEY_CURRENT_USER
    key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'
    
    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.SetValueEx(open, s_name, 0, reg.REG_SZ, address)
    reg.CloseKey(open)
    logger.info("Application set to auto-start on login.")
    notification.notify(
        title="Download File Organizer",
        message="Application set to auto-start on login.",
        timeout=10
    )

def disable_autostart():
    s_name = "DownloadFileOrganizer"
    
    key = reg.HKEY_CURRENT_USER
    key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'
    
    try:
        open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.DeleteValue(open, s_name)
        reg.CloseKey(open)
        logger.info("Application auto-start disabled.")
        notification.notify(
            title="Download File Organizer",
            message="Application auto-start disabled.",
            timeout=10
        )
    except FileNotFoundError:
        logger.warning("Auto-start entry not found.")

# Main function to set up the observer
def main():
    parser = argparse.ArgumentParser(description="Monitor and organize your Downloads folder.")
    parser.add_argument('-c', '--config', type=str, default=os.path.join(os.path.dirname(__file__), 'config.json'), help='Path to the configuration file')
    parser.add_argument('-l', '--log_to_file', action='store_true', help='Enable logging to file')
    parser.add_argument('-lf', '--log_file_path', type=str, default='file_organizer.log', help='Path to the log file')
    parser.add_argument('-ll', '--log_level', type=str, default='INFO', help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('-d', '--downloads_folder', type=str, help='Path to the Downloads folder')
    parser.add_argument('-n', '--notifications', action='store_true', help='Enable desktop notifications')
    parser.add_argument('-ra', '--retry_attempts', type=int, help='Number of retry attempts for file operations')
    parser.add_argument('-rd', '--retry_delay', type=int, help='Delay between retry attempts in seconds')
    args = parser.parse_args()

    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    global logger
    logger = configure_logging(args.log_to_file, args.log_file_path, log_level)
    
    global config_path
    config_path = args.config
    config = load_config(config_path)
    backup_config(config_path)

    # Override config values with CLI arguments if provided
    if args.downloads_folder:
        config['downloads_folder'] = args.downloads_folder
    else:
        config['downloads_folder'] = get_default_downloads_folder()
        
    if args.notifications:
        config['notifications'] = args.notifications
    if args.retry_attempts is not None:
        config['retry_attempts'] = args.retry_attempts
    if args.retry_delay is not None:
        config['retry_delay'] = args.retry_delay

    create_folders(config)

    global monitoring
    monitoring = True

    global observer
    event_handler = DownloadEventHandler(config)
    observer = Observer()
    observer.schedule(event_handler, config['downloads_folder'], recursive=False)

    observer_thread = Thread(target=observer.start)
    observer_thread.daemon = True
    observer_thread.start()
    
    logger.info(f"Monitoring Downloads folder for new files: {config['downloads_folder']}")

    # Create the system tray icon
    icon = Icon("Download File Organizer", create_image(), "Download File Organizer", 
                menu=Menu(
                    MenuItem("About", show_about),
                    MenuItem("Open Config", open_config),
                    MenuItem("Pause Monitoring", toggle_monitoring),
                    MenuItem("Reload Config", reload_config),
                    MenuItem("Enable Auto-Start", enable_autostart),
                    MenuItem("Disable Auto-Start", disable_autostart),
                    MenuItem("Exit", stop)
                ))
    icon.run()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
