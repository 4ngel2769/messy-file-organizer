<div align="center">
    <img src="./mfo.png" width=128>
    <h1>Messy File Organizer</h1>
    <h3>Smart file organization for your downloads folder</h3>
    <div>
        <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
        <img src="https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white">
        <img src="https://img.shields.io/badge/Windows-0cb1f4?style=for-the-badge&logo=windows&logoColor=white">
        <img src="https://img.shields.io/badge/Windows%2011-%230079d5.svg?style=for-the-badge&logo=Windows%2011&logoColor=white">
        <img src="https://img.shields.io/badge/Linux-000?style=for-the-badge&logo=linux&logoColor=white">
    </div>
    <p>
        <a href="https://github.com/4ngel2769/messy-file-organizer/releases/latest">
            <img src="https://img.shields.io/github/v/release/4ngel2769/messy-file-organizer?style=flat-square" alt="Latest Release">
        </a>
        <a href="https://github.com/4ngel2769/messy-file-organizer/blob/main/LICENSE">
            <img src="https://img.shields.io/github/license/4ngel2769/messy-file-organizer?style=flat-square" alt="License">
        </a>
    </p>
</div>


# Table of contents
<details>
    <summary>Click to expand</summary>

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Using the GUI](#using-the-gui)
    * [General Settings](#general-settings)
    * [Categories](#categories)
    * [File Extensions](#file-extensions)
    * [Statistics](#statistics)
    * [Tools](#tools)
    * [Advanced Settings](#advanced-settings)
- [Running from Source](#running-from-source)
    * [Requirements](#requirements)
    * [Command Line Usage](#command-line-usage)
- [Building from Source](#building-from-source)
    * [Windows](#windows-building)
    * [Linux](#linux-building)
    * [macOS](#macos-building)
- [Contributing](#contributing)

</details>

## About

Messy File Organizer is a powerful tool designed to solve the problem of cluttered download folders. It automatically categorizes and organizes files based on their types, keeping your digital workspace clean and efficient.

The application monitors your downloads folder in real-time, detecting new files and sorting them into appropriate category folders based on file extensions. This eliminates the need for manual organization and helps you find files quickly when needed.

Messy File Organizer works on Windows 10 & 11 and Linux systems. Mac support is experimental as it hasn't been extensively tested.

## Features

✨ **Automatic File Organization** - Files are sorted into categories as soon as they're downloaded

📊 **File Statistics** - View distribution of files by category and size

🔍 **Duplicate File Detection** - Find and manage duplicate files across categories

⏱️ **Scheduled Organization** - Set up automatic organization on a daily, weekly, or monthly basis

🎨 **Dark/Light Theme** - Choose your preferred visual style or use system settings

🔧 **Customizable Categories** - Add, remove, or modify file categories and extensions

💾 **Configuration Backup** - Easily backup and restore your organization settings

## Installation

### Windows

You can use `winget` to install it on Windows 11 and 10: 
```powershell
winget install 4ngel2769.MessyOrganizer
```

Or download the installer from the [latest release](https://github.com/4ngel2769/messy-file-organizer/releases/latest) page.

### Linux

Download the AppImage from the [latest release](https://github.com/4ngel2769/messy-file-organizer/releases/latest) page.

## Using the GUI

Messy File Organizer features a modern, user-friendly interface that makes configuration simple and intuitive.

### General Settings

- Set your downloads folder location
- Enable/disable notifications
- Configure auto-start options
- Choose between light and dark themes or use system settings

### Categories

- Manage category folders where files will be organized
- Add new categories for custom organization
- Customize the destination path for each category

### File Extensions

- Configure which file extensions belong to which categories
- Add custom mappings for specific file extensions
- Set default category for unknown file types

### Statistics

- View file distribution across categories
- See total file count and size for each category
- Track recent file organization activity

### Tools

- **Duplicate File Detection**: Find and manage duplicate files across categories
- **Scheduled Organization**: Configure automatic organization on a schedule
- Choose actions for duplicates: notify only, move to a separate folder, or delete

### Advanced Settings

- Configure retry attempts and delays for file operations
- Backup and restore your configuration
- Fine-tune application behavior
## Running from Source

If you prefer to run the application directly from source code, follow these steps:

### Requirements

Make sure you have the necessary libraries installed in your environment:

```bash
pip install PyQt5 pillow watchdog plyer
```

Clone and enter the repository:

```bash
# Clone the repository
git clone https://github.com/4ngel2769/messy-file-organizer.git
cd messy-file-organizer

# Install all dependencies
pip install -r requirements.txt
```

### Command Line Usage

View available command line options:

```bash
python gui.py --help
```

Start the application with the graphical interface:

```bash
python gui.py
```

Once running, the application will appear in your system tray. You can access settings and controls by clicking the tray icon.

**Tray Icon Options:**
- Open Settings: Configure the application
- View Logs: Check the application logs
- Pause/Resume Monitoring: Temporarily stop file organization
- Enable/Disable Autostart: Control startup behavior
- Exit: Close the application

## Building from Source

You can build standalone executables from the source code.

### Windows Building

```bash
# Install PyInstaller if you don't have it
pip install pyinstaller

# Navigate to the project directory
cd messy-file-organizer

# Create the executable
pyinstaller --onefile --windowed --icon=mfo.ico --name="MessyFileOrganizer" gui.py
```

The executable will be created in the `dist` folder.

### Linux Building

```bash
# Install PyInstaller if you don't have it
pip install pyinstaller

# Navigate to the project directory
cd messy-file-organizer

# Create the executable
pyinstaller --onefile --windowed --icon=mfo.ico --name="MessyFileOrganizer" gui.py
```

### macOS Building

Building on macOS requires similar steps to Linux, but has not been extensively tested.

## Contributing

Contributions are welcome! Here's how you can help:

- **Report bugs** by opening an issue
- **Suggest features** that would make the app more useful
- **Submit pull requests** with improvements or bug fixes
- **Test on different platforms**, especially macOS

Please ensure your code follows the project's style and includes appropriate documentation.

---

<div align="center">
    <p>If you find this project useful, consider supporting its development!</p>
    <a href="https://ko-fi.com/angeldev0">
        <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white">
    </a>
    <p>Made with ❤️ by <a href="https://github.com/4ngel2769">Angel</a></p>
</div>