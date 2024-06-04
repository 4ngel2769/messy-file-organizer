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
import winreg as reg

# File Organizer Class
class FileOrganizer:
    def __init__(self, args):
        self.args = args
        self.config_path = args.config
        self.load_config()
        self.logger = self.configure_logging()
        self.backup_config()
        self.create_folders()
        self.monitoring = True
        self.observer = Observer()
        self.event_handler = DownloadEventHandler(self)
    
    def configure_logging(self):
        log_level = getattr(logging, self.args.log_level.upper(), logging.INFO)
        logging.basicConfig(
            filename=self.args.log_file_path if self.args.log_to_file else None,
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return logging.getLogger()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                self.config = json.load(file)
        except Exception as e:
            print(f"Failed to load configuration file: {e}")
            sys.exit(1)

    def backup_config(self):
        try:
            backup_path = self.config_path + ".bak"
            shutil.copy(self.config_path, backup_path)
            self.logger.info(f"Backup of configuration file created at: {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to create backup of configuration file: {e}")

    def create_folders(self):
        for folder in self.config['folders'].values():
            os.makedirs(folder, exist_ok=True)

    def get_unique_file_path(self, destination, filename):
        base, extension = os.path.splitext(filename)
        counter = 1
        new_file_path = os.path.join(destination, filename)
        while os.path.exists(new_file_path):
            new_file_path = os.path.join(destination, f"{base} ({counter}){extension}")
            counter += 1
        return new_file_path

    def move_file(self, file_path):
        _, extension = os.path.splitext(file_path)
        if extension == '.tmp' or file_path.endswith('~'):
            self.logger.info(f"Ignored temporary file: {file_path}")
            return

        destination = self.config['folders']['Other']
        category = 'Other'

        for cat, extensions in self.config['file_types'].items():
            if extension in extensions:
                destination = self.config['folders'][cat]
                category = cat
                break

        attempts = 0
        while attempts < self.config['retry_attempts']:
            try:
                unique_file_path = self.get_unique_file_path(destination, os.path.basename(file_path))
                shutil.move(file_path, unique_file_path)
                self.logger.info(f"Moved file: {file_path} to {unique_file_path}")
                if self.config['notifications']:
                    notification.notify(
                        title="File Moved",
                        message=f"File: {os.path.basename(file_path)}\nCategory: {category}\nDestination: {unique_file_path}",
                        timeout=10
                    )
                break
            except FileNotFoundError:
                attempts += 1
                self.logger.warning(f"File not found: {file_path}. Attempt {attempts} of {self.config['retry_attempts']}. Retrying...")
                sleep(self.config['retry_delay'])
            except Exception as e:
                self.logger.error(f"Failed to move file: {file_path}. Attempt {attempts} of {self.config['retry_attempts']}. Reason: {e}")
                sleep(self.config['retry_delay'])
        else:
            self.logger.error(f"Exhausted all retry attempts for file: {file_path}")

    def start_monitoring(self):
        self.observer.schedule(self.event_handler, self.config['downloads_folder'], recursive=False)
        self.observer_thread = Thread(target=self.observer.start)
        self.observer_thread.daemon = True
        self.observer_thread.start()
        self.logger.info(f"Monitoring Downloads folder for new files: {self.config['downloads_folder']}")

    def stop_monitoring(self):
        self.observer.stop()
        self.observer_thread.join()

    def reload_config(self):
        self.load_config()
        self.create_folders()
        self.logger.info("Configuration reloaded.")
        notification.notify(
            title="Download File Organizer",
            message="Configuration reloaded successfully.",
            timeout=10
        )

    def enable_autostart(self):
        pth = os.path.dirname(os.path.realpath(__file__))
        s_name = "DownloadFileOrganizer"
        address = os.path.join(pth, "download_file_organizer.exe")

        key = reg.HKEY_CURRENT_USER
        key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'

        open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open, s_name, 0, reg.REG_SZ, address)
        reg.CloseKey(open)
        self.logger.info("Application set to auto-start on login.")
        notification.notify(
            title="Download File Organizer",
            message="Application set to auto-start on login.",
            timeout=10
        )

    def disable_autostart(self):
        s_name = "DownloadFileOrganizer"

        key = reg.HKEY_CURRENT_USER
        key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'

        try:
            open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
            reg.DeleteValue(open, s_name)
            reg.CloseKey(open)
            self.logger.info("Application auto-start disabled.")
            notification.notify(
                title="Download File Organizer",
                message="Application auto-start disabled.",
                timeout=10
            )
        except FileNotFoundError:
            self.logger.warning("Auto-start entry not found.")

    def create_image(self):
        width, height = 64, 64
        image = Image.new('RGB', (width, height), (0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=(255, 0, 0))
        dc.rectangle((0, height // 2, width // 2, height), fill=(255, 0, 0))
        return image

    def run_tray_icon(self):
        icon = Icon("Download File Organizer", self.create_image(), "Download File Organizer", 
                    menu=Menu(
                        MenuItem("About", self.show_about),
                        MenuItem("Open Config", self.open_config),
                        MenuItem("Pause Monitoring", self.toggle_monitoring),
                        MenuItem("Reload Config", self.reload_config),
                        MenuItem("Enable Auto-Start", self.enable_autostart),
                        MenuItem("Disable Auto-Start", self.disable_autostart),
                        MenuItem("Exit", self.stop)
                    ))
        icon.run()

    def show_about(self, icon, item):
        notification.notify(
            title="Download File Organizer",
            message="Download File Organizer\nVersion 1.0.0\nThe path to learning python\nangeldev0",
            timeout=10
        )

    def open_config(self, icon, item):
        if platform.system() == 'Windows':
            os.startfile(self.config_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', self.config_path])
        else:  # Linux and other UNIX-like systems
            subprocess.call(['xdg-open', self.config_path])

    def toggle_monitoring(self, icon, item):
        if self.monitoring:
            self.stop_monitoring()
            item.text = "Resume Monitoring"
            self.monitoring = False
            self.logger.info("Monitoring paused.")
        else:
            self.start_monitoring()
            item.text = "Pause Monitoring"
            self.monitoring = True
            self.logger.info("Monitoring resumed.")

    def stop(self, icon, item):
        self.stop_monitoring()
        icon.stop()
        sys.exit()

class DownloadEventHandler(FileSystemEventHandler):
    def __init__(self, organizer):
        self.organizer = organizer

    def on_created(self, event):
        if not event.is_directory:
            sleep(5)  # Add a delay to ensure the file is fully downloaded
            self.organizer.move_file(event.src_path)

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

    organizer = FileOrganizer(args)
    organizer.start_monitoring()
    organizer.run_tray_icon()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        organizer.stop_monitoring()

if __name__ == "__main__":
    main()
