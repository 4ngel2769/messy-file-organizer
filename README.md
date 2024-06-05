<div align="center">
    <img src="./mfo.png" width=128>
    <h1>Messy Organizer</h1>
    <h3>An application that sorts newly downloaded files into categories</h3>
    <div>
        <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
        <img src="https://img.shields.io/badge/Visual%20Studio-5C2D91.svg?style=for-the-badge&logo=visual-studio&logoColor=white">
        <img src="https://img.shields.io/badge/Windows-0cb1f4?style=for-the-badge&logo=windows&logoColor=white">
        <img src="https://img.shields.io/badge/Windows%2011-%230079d5.svg?style=for-the-badge&logo=Windows%2011&logoColor=white">
        <img src="https://img.shields.io/badge/Linux-000?style=for-the-badge&logo=linux&logoColor=white">
    </div>
    <h6>⚠️This is a work in progress. Please be patient 💚</h6>
</div>


# Table of contents
<details>
    <summary>click to expand</summary>

- [About](#about)
- [Usage](#usage)
    * [Application (Installer)](#application-with-installer)
        - [Windows](#windows)
        - [Linux](#linux)
    * [Python script](#python-script)
        1. [Requirements](#requirements)
        2. [Command line (`cli`) usage](#cli)
        3. [Desktop](#desktop-script)
- [Compiling from source](#compiling-from-source)
    * [Windows](#windows-compiling)
    * [Linux](#linux-compiling)
    * [macOS](#macos-compiling)

</details>

#

# About
Messy is an app I made to help me with my downloads hoarding problem. Since I keep most of the things I download stay in that folder for months it has become a nightmare to navigate and find files.

And so here is __Messy__, the fix for my problem. The app will create a couple of folders for a few categories of files. Every time a new file is downloaded inside of the Downloads folder, Messy will detect what kind of file it is and sort it into a category to keep things organized and out of your way.

Messy currently works on Windows 10 & 11, and should work on linux as well. Mac support is not guaranteed because I don't own a mac device to test it.

###### `p.s. if you own a mac and are willing to help with the project, you're more than welcomed!`

# Usage
Guide to using Messy.

## Application (with installer)
Get the latest installer for you OS from [`releases/latest`](https://github.com/4ngel2769/messy-file-organizer/releases/latest) and go through the installation steps. After running, the app will start in the background. Settings can be accessed from the taskbar icon. 

You have the options to:
- View the logs
- Open the configuration file
- Pause/resume file monitoring (`will stop moving files while paused`)
- Enable/disable autostart (`Windows only`)
- Reload configuration file

<!-- ### Windows -->
<!-- ### Linux -->

## Python script
Run the app using the script.py only.
### Requirements
Make sure you have the necessary libraries installed in your environment by running:
```py
pip install pyinstaller pystray pillow watchdog plyer
```

Clone and enter the repository:
```zsh
# Windows Terminal and Linux/*nix-like systems
git clone https://github.com/4ngel2769/messy-file-organizer.git
cd messy-file-organizer
```

### CLI
```zsh
python script.py --help
```
```py
usage: script.py [-h] [-c CONFIG] [-l] [-lf LOG_FILE_PATH] [-ll LOG_LEVEL] [-d DOWNLOADS_FOLDER] [-p] [-n]
                 [-ra RETRY_ATTEMPTS] [-rd RETRY_DELAY]

Monitor and organize your Downloads folder.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to the configuration file
  -l, --log_to_file     Enable logging to file
  -lf LOG_FILE_PATH, --log_file_path LOG_FILE_PATH
                        Path to the log file
  -ll LOG_LEVEL, --log_level LOG_LEVEL
                        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  -d DOWNLOADS_FOLDER, --downloads_folder DOWNLOADS_FOLDER
                        Path to the Downloads folder
  -p, --paused          Start in paused state
  -n, --notifications   Enable desktop notifications
  -ra RETRY_ATTEMPTS, --retry_attempts RETRY_ATTEMPTS
                        Number of retry attempts for file operations
  -rd RETRY_DELAY, --retry_delay RETRY_DELAY
                        Delay between retry attempts in seconds
```

### Desktop (script)
Run this in your terminal:
```zsh
python script.py
```
Messy will not start in the background and can be used as if it was installed.



# Compiling from source
Guide to compiling the python script into an executable.

## Windows (compiling)
Navigate to the folder where the `script.py` is and open your terminal.
Run these commands to create the executable:
```zsh
# creates the .spec file
pyi-makespec \script.py
# Customize the .spec file as needed

# compiles the executable in ./dist/script.exe
pyinstaller --onefile --windowed --icon=mfo.ico .\script.spec
```

## Linux (compiling)
Use the same steps in [Windows](#windows-compiling)

## macOS (compiling)
Don't know how to yet.