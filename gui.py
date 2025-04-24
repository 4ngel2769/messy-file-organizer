import sys
import os
import json
import shutil
import hashlib
import datetime
import time
import threading
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, 
                             QGroupBox, QFormLayout, QCheckBox, QSpinBox, QListWidget, 
                             QListWidgetItem, QMessageBox, QInputDialog, QScrollArea,
                             QAction, QMenu, QProgressBar, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDateEdit, QTimeEdit, QComboBox, QRadioButton)
from PyQt5.QtCore import Qt, QSize, QSettings, QDateTime, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor, QFont, QFontMetrics

class MessyFileOrganizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Messy File Organizer")
        self.setMinimumSize(800, 600)
        
        # Load icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mfo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Initialize config path
        user_home = os.path.expanduser("~")
        config_dir = os.path.join(user_home, '.config', 'mfo')
        os.makedirs(config_dir, exist_ok=True)
        self.config_path = os.path.join(config_dir, 'config.json')
        
        # Initialize theme settings
        self.settings = QSettings("MessyFileOrganizer", "AppSettings")
        # Convert the dark_mode value to boolean explicitly
        dark_mode_setting = self.settings.value("dark_mode", self.is_system_dark_mode())
        self.dark_mode = dark_mode_setting if isinstance(dark_mode_setting, bool) else dark_mode_setting == "true"
        
        # Load or create config
        self.load_config()
        
        # Load stylesheet based on theme
        self.load_stylesheet()
        
        # Setup UI
        self.setup_ui()
    
    def is_system_dark_mode(self):
        """Check if system is using dark mode (Windows)"""
        try:
            # For Windows
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0  # 0 means dark mode is enabled
        except Exception:
            return False  # Default to light mode if we can't determine
        
    def load_stylesheet(self):
        """Load and apply the application stylesheet based on theme"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Apply base stylesheet
        style_path = os.path.join(base_path, "style.qss")
        stylesheet = ""
        
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                stylesheet = f.read()
        
        # Apply theme-specific styles
        if self.dark_mode:
            theme_style = self.get_dark_mode_stylesheet()
        else:
            theme_style = self.get_light_mode_stylesheet()
            
        stylesheet += "\n" + theme_style
        self.setStyleSheet(stylesheet)
    
    def get_light_mode_stylesheet(self):
        """Generate light mode stylesheet"""
        return """
        /* Light mode styles */
        QMainWindow, QDialog, QWidget {
            background-color: #f5f5f5;
            color: #333333;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: #ffffff;
            border-radius: 6px;
        }
        
        QTabBar::tab {
            background-color: #e6e6e6;
            border: 1px solid #cccccc;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: #333333;
            padding: 6px 12px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 1px solid #ffffff;
            font-weight: bold;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #d9d9d9;
        }
        
        QLineEdit, QSpinBox, QTimeEdit, QDateEdit, QComboBox {
            border: 1px solid #cccccc;
            background-color: #ffffff;
            color: #333333;
            padding: 6px;
            border-radius: 4px;
            min-height: 24px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QTimeEdit:focus, QDateEdit:focus, QComboBox:focus {
            border: 2px solid #0078d7;
        }
        
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            min-height: 30px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1a88e0;
        }
        
        QPushButton:pressed {
            background-color: #005fa3;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #888888;
        }
        
        QGroupBox {
            border: 1px solid #cccccc;
            background-color: #ffffff;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            background-color: #ffffff;
            color: #333333;
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 8px;
            font-weight: bold;
        }
        
        QListWidget, QTableWidget {
            border: 1px solid #cccccc;
            background-color: #ffffff;
            alternate-background-color: #f9f9f9;
            color: #333333;
            border-radius: 4px;
        }
        
        QListWidget::item {
            border-bottom: 1px solid #eeeeee;
            padding: 4px;
        }
        
        QListWidget::item:selected, QTableWidget::item:selected {
            background-color: #0078d7;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #e6e6e6;
            color: #333333;
            padding: 4px;
            border: 1px solid #cccccc;
        }
        
        QCheckBox {
            color: #333333;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 1px solid #cccccc;
            background-color: #ffffff;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            border: 1px solid #0078d7;
            background-color: #0078d7;
            border-radius: 3px;
        }
        
        QProgressBar {
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: #ffffff;
            text-align: center;
            color: #333333;
        }
        
        QProgressBar::chunk {
            background-color: #0078d7;
            border-radius: 3px;
        }
        
        QScrollBar:vertical {
            background-color: #f5f5f5;
            width: 14px;
            margin: 15px 3px 15px 3px;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #c1c1c1;
            min-height: 20px;
            border-radius: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #a8a8a8;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        
        QScrollBar:horizontal {
            background-color: #f5f5f5;
            height: 14px;
            margin: 3px 15px 3px 15px;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #c1c1c1;
            min-width: 20px;
            border-radius: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #a8a8a8;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
        }
        
        QMenu {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
        
        QMenu::item {
            padding: 6px 24px 6px 12px;
        }
        
        QMenu::item:selected {
            background-color: #0078d7;
            color: white;
        }
        
        QLabel {
            color: #333333;
        }
        
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px 8px;
            background-color: #ffffff;
            color: #333333;
            min-height: 24px;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #cccccc;
        }
        
        QComboBox QAbstractItemView {
            border: 1px solid #cccccc;
            background-color: #ffffff;
            color: #333333;
            selection-background-color: #0078d7;
            selection-color: white;
        }
        """
        
    def get_dark_mode_stylesheet(self):
        """Generate dark mode stylesheet"""
        return """
        /* Dark mode styles */
        QMainWindow, QDialog, QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        
        QTabWidget::pane {
            border: 1px solid #3a3a3a;
            background-color: #2d2d2d;
            border-radius: 6px;
        }
        
        QTabBar::tab {
            background-color: #383838;
            border: 1px solid #3a3a3a;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: #e0e0e0;
            padding: 6px 12px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #2d2d2d;
            border-bottom: 1px solid #2d2d2d;
            font-weight: bold;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #454545;
        }
        
        QLineEdit, QSpinBox, QTimeEdit, QDateEdit, QComboBox {
            border: 1px solid #3a3a3a;
            background-color: #2d2d2d;
            color: #e0e0e0;
            padding: 6px;
            border-radius: 4px;
            min-height: 24px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QTimeEdit:focus, QDateEdit:focus, QComboBox:focus {
            border: 2px solid #5294e2;
        }
        
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            min-height: 30px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1a88e0;
        }
        
        QPushButton:pressed {
            background-color: #005fa3;
        }
        
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        
        QGroupBox {
            border: 1px solid #3a3a3a;
            background-color: #2d2d2d;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            background-color: #2d2d2d;
            color: #e0e0e0;
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 8px;
            font-weight: bold;
        }
        
        QListWidget, QTableWidget {
            border: 1px solid #3a3a3a;
            background-color: #2d2d2d;
            alternate-background-color: #333333;
            color: #e0e0e0;
            border-radius: 4px;
        }
        
        QListWidget::item {
            border-bottom: 1px solid #3a3a3a;
            padding: 4px;
        }
        
        QListWidget::item:selected, QTableWidget::item:selected {
            background-color: #0078d7;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #383838;
            color: #e0e0e0;
            padding: 4px;
            border: 1px solid #3a3a3a;
        }
        
        QCheckBox {
            color: #e0e0e0;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 1px solid #3a3a3a;
            background-color: #2d2d2d;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            border: 1px solid #0078d7;
            background-color: #0078d7;
            border-radius: 3px;
        }
        
        QProgressBar {
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            background-color: #2d2d2d;
            text-align: center;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: #0078d7;
            border-radius: 3px;
        }
        
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 14px;
            margin: 15px 3px 15px 3px;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #5a5a5a;
            min-height: 20px;
            border-radius: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #6a6a6a;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 14px;
            margin: 3px 15px 3px 15px;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #5a5a5a;
            min-width: 20px;
            border-radius: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #6a6a6a;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
        }
        
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
        }
        
        QMenu::item {
            padding: 6px 24px 6px 12px;
        }
        
        QMenu::item:selected {
            background-color: #0078d7;
        }
        
        QLabel {
            color: #e0e0e0;
        }
        
        QComboBox {
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 4px 8px;
            background-color: #2d2d2d;
            color: #e0e0e0;
            min-height: 24px;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #3a3a3a;
        }
        
        QComboBox QAbstractItemView {
            border: 1px solid #3a3a3a;
            background-color: #2d2d2d;
            color: #e0e0e0;
            selection-background-color: #0078d7;
        }
        """
    
    def load_config(self):
        if not os.path.exists(self.config_path):
            self.create_default_config()
        try:
            with open(self.config_path, 'r') as file:
                self.config = json.load(file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration file: {e}")
            self.create_default_config()
            with open(self.config_path, 'r') as file:
                self.config = json.load(file)
    
    def create_default_config(self):
        user_home = os.path.expanduser("~")
        downloads_folder = os.path.join(user_home, "Downloads")
        default_config = {
            "downloads_folder": downloads_folder,
            "folders": {
                "Documents": os.path.join(downloads_folder, "Documents"),
                "Apps": os.path.join(downloads_folder, "Apps"),
                "Images": os.path.join(downloads_folder, "Images"),
                "Videos": os.path.join(downloads_folder, "Videos"),
                "Archives": os.path.join(downloads_folder, "Archives"),
                "Music": os.path.join(downloads_folder, "Music"),
                "Other": os.path.join(downloads_folder, "Other")
            },
            "default_folder_mappings": {
                ".md": "Documents",
                ".json": "Documents",
                ".log": "Documents"
            },
            "file_types": {
                "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".ppt", ".xlsx", ".xls"],
                "Apps": [".exe", ".msi"],
                "Images": [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"],
                "Videos": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv"],
                "Archives": [".zip", ".rar", ".tar.gz", ".tar.xz", ".gz", "7z", ".dmg", ".iso", ".pak", ".tar.gz", ".tgz", ".tar.Z", ".tar.bz2", ".tbz2", ".tar.lz", ".tlz", ".tar.xz", ".txz", ".tar.zst"],
                "Music": [".mp3", ".wav", ".aac", ".flac", ".ogg"]
            },
            "notifications": True,
            "scheduled_organization": {
                "enabled": False,
                "frequency": "daily",
                "time": "00:00"
            },
            "duplicate_detection": {
                "enabled": False,
                "action": "notify"  # notify, move, or delete
            },
            "retry_attempts": 3,
            "retry_delay": 2,
            "icon_path": "mfo.png"
        }
        with open(self.config_path, 'w') as file:
            json.dump(default_config, file, indent=4)
        print(f"Default configuration file created at: {self.config_path}")
    
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Create tabs
        general_tab = self.create_general_tab()
        categories_tab = self.create_categories_tab()
        extensions_tab = self.create_extensions_tab()
        statistics_tab = self.create_statistics_tab()
        tools_tab = self.create_tools_tab()
        advanced_tab = self.create_advanced_tab()
        
        # Add tabs to tab widget
        tab_widget.addTab(general_tab, "General")
        tab_widget.addTab(categories_tab, "Categories")
        tab_widget.addTab(extensions_tab, "File Extensions")
        tab_widget.addTab(statistics_tab, "Statistics")
        tab_widget.addTab(tools_tab, "Tools")
        tab_widget.addTab(advanced_tab, "Advanced")
        
        # Create save and cancel buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        # Theme action
        theme_menu = QMenu("Theme", self)
        view_menu.addMenu(theme_menu)
        
        # System theme action
        system_theme_action = QAction("Use System Theme", self)
        system_theme_action.setCheckable(True)
        system_theme_action.setChecked(True)
        system_theme_action.triggered.connect(self.use_system_theme)
        theme_menu.addAction(system_theme_action)
        
        # Light theme action
        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(lambda: self.change_theme(False))
        theme_menu.addAction(light_theme_action)
        
        # Dark theme action
        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme(True))
        theme_menu.addAction(dark_theme_action)
    
    def use_system_theme(self):
        """Set theme based on system preference"""
        is_dark = self.is_system_dark_mode()
        self.change_theme(is_dark)
    
    def change_theme(self, dark_mode):
        """Change the application theme"""
        if self.dark_mode != dark_mode:
            self.dark_mode = dark_mode
            self.settings.setValue("dark_mode", dark_mode)
            self.load_stylesheet()
            QMessageBox.information(self, "Theme Changed", 
                                  f"Application theme changed to {'Dark' if dark_mode else 'Light'} mode.\n"
                                  "The change will be fully applied when you restart the application.")
    
    def create_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Downloads folder section
        downloads_group = QGroupBox("Downloads Folder")
        downloads_layout = QHBoxLayout(downloads_group)
        self.downloads_folder_edit = QLineEdit(self.config["downloads_folder"])
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_downloads_folder)
        downloads_layout.addWidget(self.downloads_folder_edit)
        downloads_layout.addWidget(browse_button)
        layout.addWidget(downloads_group)
        
        # Notifications section
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QVBoxLayout(notifications_group)
        self.notifications_checkbox = QCheckBox("Enable notifications")
        self.notifications_checkbox.setChecked(self.config["notifications"])
        notifications_layout.addWidget(self.notifications_checkbox)
        layout.addWidget(notifications_group)
        
        # Theme section
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout(theme_group)
        
        # System theme checkbox
        self.system_theme_checkbox = QCheckBox("Use system theme")
        self.system_theme_checkbox.setChecked(True)
        self.system_theme_checkbox.toggled.connect(self.toggle_system_theme)
        theme_layout.addWidget(self.system_theme_checkbox)
        
        # Dark mode checkbox
        self.dark_mode_checkbox = QCheckBox("Dark mode")
        self.dark_mode_checkbox.setChecked(self.dark_mode)
        self.dark_mode_checkbox.toggled.connect(self.toggle_dark_mode)
        self.dark_mode_checkbox.setEnabled(not self.system_theme_checkbox.isChecked())
        theme_layout.addWidget(self.dark_mode_checkbox)
        
        layout.addWidget(theme_group)
        
        # Auto-start section
        autostart_group = QGroupBox("Auto-Start")
        autostart_layout = QVBoxLayout(autostart_group)
        self.autostart_checkbox = QCheckBox("Start application on system boot")
        # We'll need to check if auto-start is enabled and set this accordingly
        autostart_layout.addWidget(self.autostart_checkbox)
        layout.addWidget(autostart_group)
        
        layout.addStretch()
        return tab
        
    def toggle_system_theme(self, checked):
        """Toggle between system theme and manual theme selection"""
        self.dark_mode_checkbox.setEnabled(not checked)
        if checked:
            is_dark = self.is_system_dark_mode()
            self.dark_mode_checkbox.setChecked(is_dark)
            self.change_theme(is_dark)
    
    def toggle_dark_mode(self, checked):
        """Toggle between dark and light mode"""
        if not self.system_theme_checkbox.isChecked():
            self.change_theme(checked)
    
    def create_categories_tab(self):
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Categories and their folders
        categories_group = QGroupBox("Category Folders")
        categories_layout = QFormLayout(categories_group)
        
        self.category_edits = {}
        for category, folder in self.config["folders"].items():
            row_layout = QHBoxLayout()
            folder_edit = QLineEdit(folder)
            browse_button = QPushButton("Browse...")
            browse_button.setProperty("category", category)
            browse_button.clicked.connect(self.browse_category_folder)
            row_layout.addWidget(folder_edit)
            row_layout.addWidget(browse_button)
            categories_layout.addRow(category, row_layout)
            self.category_edits[category] = folder_edit
        
        # Add new category button
        add_category_button = QPushButton("Add New Category")
        add_category_button.clicked.connect(self.add_new_category)
        categories_layout.addRow("", add_category_button)
        
        layout.addWidget(categories_group)
        layout.addStretch()
        tab.setWidget(content_widget)
        return tab
    
    def create_extensions_tab(self):
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # File extensions for each category
        self.extension_lists = {}
        
        for category in self.config["file_types"].keys():
            group = QGroupBox(f"{category} Extensions")
            group_layout = QVBoxLayout(group)
            
            # List widget for extensions
            list_widget = QListWidget()
            for extension in self.config["file_types"][category]:
                item = QListWidgetItem(extension)
                list_widget.addItem(item)
            
            # Buttons for managing extensions
            buttons_layout = QHBoxLayout()
            add_button = QPushButton("Add")
            add_button.setProperty("category", category)
            add_button.clicked.connect(self.add_extension)
            
            remove_button = QPushButton("Remove")
            remove_button.setProperty("category", category)
            remove_button.clicked.connect(self.remove_extension)
            
            buttons_layout.addWidget(add_button)
            buttons_layout.addWidget(remove_button)
            
            group_layout.addWidget(list_widget)
            group_layout.addLayout(buttons_layout)
            
            layout.addWidget(group)
            self.extension_lists[category] = list_widget
        
        # Default mappings section
        default_mappings_group = QGroupBox("Default Extension Mappings")
        default_mappings_layout = QVBoxLayout(default_mappings_group)
        
        # List widget for default mappings
        self.default_mappings_list = QListWidget()
        for ext, category in self.config.get("default_folder_mappings", {}).items():
            item = QListWidgetItem(f"{ext} → {category}")
            item.setData(Qt.UserRole, {"extension": ext, "category": category})
            self.default_mappings_list.addItem(item)
        
        # Buttons for managing default mappings
        mapping_buttons_layout = QHBoxLayout()
        add_mapping_button = QPushButton("Add Mapping")
        add_mapping_button.clicked.connect(self.add_default_mapping)
        
        remove_mapping_button = QPushButton("Remove Mapping")
        remove_mapping_button.clicked.connect(self.remove_default_mapping)
        
        mapping_buttons_layout.addWidget(add_mapping_button)
        mapping_buttons_layout.addWidget(remove_mapping_button)
        
        default_mappings_layout.addWidget(self.default_mappings_list)
        default_mappings_layout.addLayout(mapping_buttons_layout)
        
        layout.addWidget(default_mappings_group)
        layout.addStretch()
        tab.setWidget(content_widget)
        return tab
    
    def create_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Retry settings
        retry_group = QGroupBox("Retry Settings")
        retry_layout = QFormLayout(retry_group)
        
        self.retry_attempts_spin = QSpinBox()
        self.retry_attempts_spin.setRange(1, 10)
        self.retry_attempts_spin.setValue(self.config["retry_attempts"])
        retry_layout.addRow("Retry Attempts:", self.retry_attempts_spin)
        
        self.retry_delay_spin = QSpinBox()
        self.retry_delay_spin.setRange(1, 30)
        self.retry_delay_spin.setValue(self.config["retry_delay"])
        retry_layout.addRow("Retry Delay (seconds):", self.retry_delay_spin)
        
        layout.addWidget(retry_group)
        
        # Backup and restore section
        backup_group = QGroupBox("Backup and Restore")
        backup_layout = QVBoxLayout(backup_group)
        
        backup_button = QPushButton("Backup Configuration")
        backup_button.clicked.connect(self.backup_config)
        backup_layout.addWidget(backup_button)
        
        restore_button = QPushButton("Restore Configuration")
        restore_button.clicked.connect(self.restore_config)
        backup_layout.addWidget(restore_button)
        
        layout.addWidget(backup_group)
        layout.addStretch()
        return tab
    
    def browse_downloads_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Downloads Folder", self.downloads_folder_edit.text())
        if folder:
            self.downloads_folder_edit.setText(folder)
    
    def browse_category_folder(self):
        sender = self.sender()
        category = sender.property("category")
        current_path = self.category_edits[category].text()
        folder = QFileDialog.getExistingDirectory(self, f"Select Folder for {category}", current_path)
        if folder:
            self.category_edits[category].setText(folder)
    
    def add_new_category(self):
        category, ok = QInputDialog.getText(self, "Add Category", "Enter new category name:")
        if ok and category:
            if category in self.config["folders"]:
                QMessageBox.warning(self, "Warning", f"Category '{category}' already exists.")
                return
            
            # Add to folders
            downloads_folder = self.downloads_folder_edit.text()
            default_path = os.path.join(downloads_folder, category)
            self.config["folders"][category] = default_path
            
            # Add to file_types
            self.config["file_types"][category] = []
            
            # Refresh UI
            self.save_config()
            QMessageBox.information(self, "Success", f"Category '{category}' added. Please restart the application to see the changes.")
    
    def add_extension(self):
        sender = self.sender()
        category = sender.property("category")
        extension, ok = QInputDialog.getText(self, "Add Extension", f"Enter file extension for {category} (include the dot, e.g. '.pdf'):")
        if ok and extension:
            if not extension.startswith("."):
                extension = "." + extension
            
            list_widget = self.extension_lists[category]
            # Check if extension already exists
            for i in range(list_widget.count()):
                if list_widget.item(i).text() == extension:
                    QMessageBox.warning(self, "Warning", f"Extension '{extension}' already exists in {category}.")
                    return
            
            # Add to list widget
            list_widget.addItem(QListWidgetItem(extension))
    
    def remove_extension(self):
        sender = self.sender()
        category = sender.property("category")
        list_widget = self.extension_lists[category]
        selected_items = list_widget.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an extension to remove.")
            return
        
        for item in selected_items:
            list_widget.takeItem(list_widget.row(item))
    
    def add_default_mapping(self):
        extension, ok = QInputDialog.getText(self, "Add Mapping", "Enter file extension (include the dot, e.g. '.pdf'):")
        if not ok or not extension:
            return
        
        if not extension.startswith("."):
            extension = "." + extension
        
        # Get categories
        categories = list(self.config["folders"].keys())
        category, ok = QInputDialog.getItem(self, "Select Category", "Select category for this extension:", categories, 0, False)
        
        if ok and category:
            # Check if mapping already exists
            for i in range(self.default_mappings_list.count()):
                item_data = self.default_mappings_list.item(i).data(Qt.UserRole)
                if item_data["extension"] == extension:
                    QMessageBox.warning(self, "Warning", f"Mapping for '{extension}' already exists.")
                    return
            
            # Add to list widget
            item = QListWidgetItem(f"{extension} → {category}")
            item.setData(Qt.UserRole, {"extension": extension, "category": category})
            self.default_mappings_list.addItem(item)
    
    def remove_default_mapping(self):
        selected_items = self.default_mappings_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a mapping to remove.")
            return
        
        for item in selected_items:
            self.default_mappings_list.takeItem(self.default_mappings_list.row(item))
    
    def backup_config(self):
        backup_path, _ = QFileDialog.getSaveFileName(self, "Backup Configuration", 
                                                  os.path.expanduser("~"), 
                                                  "JSON Files (*.json)")
        if backup_path:
            try:
                shutil.copy(self.config_path, backup_path)
                QMessageBox.information(self, "Success", f"Configuration backed up to {backup_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to backup configuration: {e}")
    
    def restore_config(self):
        restore_path, _ = QFileDialog.getOpenFileName(self, "Restore Configuration", 
                                                   os.path.expanduser("~"), 
                                                   "JSON Files (*.json)")
        if restore_path:
            try:
                with open(restore_path, 'r') as file:
                    # Validate JSON format
                    restored_config = json.load(file)
                    
                    # Check for required keys
                    required_keys = ["downloads_folder", "folders", "file_types", "notifications", "retry_attempts", "retry_delay"]
                    for key in required_keys:
                        if key not in restored_config:
                            raise ValueError(f"Missing required key: {key}")
                    
                    # Backup current config before restoring
                    backup_path = self.config_path + ".bak"
                    shutil.copy(self.config_path, backup_path)
                    
                    # Copy the restored config
                    shutil.copy(restore_path, self.config_path)
                    
                    QMessageBox.information(self, "Success", 
                                          f"Configuration restored from {restore_path}\n"
                                          f"Previous configuration backed up to {backup_path}")
                    
                    # Reload the application to apply changes
                    self.load_config()
                    QMessageBox.information(self, "Restart Required", 
                                          "Please restart the application to apply the restored configuration.")
                    self.close()
                    
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Error", "Invalid JSON file.")
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore configuration: {e}")
    
    def save_config(self):
        # Update config from UI
        self.config["downloads_folder"] = self.downloads_folder_edit.text()
        self.config["notifications"] = self.notifications_checkbox.isChecked()
        
        # Update category folders
        for category, edit in self.category_edits.items():
            self.config["folders"][category] = edit.text()
        
        # Update file extensions
        for category, list_widget in self.extension_lists.items():
            extensions = []
            for i in range(list_widget.count()):
                extensions.append(list_widget.item(i).text())
            self.config["file_types"][category] = extensions
        
        # Update default mappings
        default_mappings = {}
        for i in range(self.default_mappings_list.count()):
            item_data = self.default_mappings_list.item(i).data(Qt.UserRole)
            default_mappings[item_data["extension"]] = item_data["category"]
        self.config["default_folder_mappings"] = default_mappings
        
        # Update retry settings
        self.config["retry_attempts"] = self.retry_attempts_spin.value()
        self.config["retry_delay"] = self.retry_delay_spin.value()
        
        # Save to file
        try:
            with open(self.config_path, 'w') as file:
                json.dump(self.config, file, indent=4)
            QMessageBox.information(self, "Success", "Configuration saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

    def create_statistics_tab(self):
        """Create the statistics tab to display file distribution and usage stats"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # File distribution section
        distribution_group = QGroupBox("File Distribution")
        distribution_layout = QVBoxLayout(distribution_group)
        
        # Table for showing file counts and sizes by category
        self.stats_table = QTableWidget(0, 3)
        self.stats_table.setHorizontalHeaderLabels(["Category", "File Count", "Total Size"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        distribution_layout.addWidget(self.stats_table)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Statistics")
        refresh_button.clicked.connect(self.refresh_statistics)
        distribution_layout.addWidget(refresh_button)
        
        layout.addWidget(distribution_group)
        
        # Recent activity section
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        tab.setWidget(content_widget)
        return tab
    
    def refresh_statistics(self):
        """Refresh the statistics display with current data"""
        # Clear existing data
        self.stats_table.setRowCount(0)
        
        # Get downloads folder path
        downloads_folder = self.downloads_folder_edit.text()
        
        # Initialize counters
        category_stats = {}
        for category in self.config["folders"].keys():
            category_folder = self.config["folders"][category]
            if os.path.exists(category_folder):
                file_count = 0
                total_size = 0
                
                # Count files and calculate total size
                for root, _, files in os.walk(category_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            file_count += 1
                            total_size += file_size
                        except Exception:
                            pass
                
                category_stats[category] = (file_count, total_size)
        
        # Add data to table
        for category, (file_count, total_size) in category_stats.items():
            row = self.stats_table.rowCount()
            self.stats_table.insertRow(row)
            
            # Format size in human-readable format
            if total_size < 1024:
                size_str = f"{total_size} B"
            elif total_size < 1024 * 1024:
                size_str = f"{total_size / 1024:.2f} KB"
            elif total_size < 1024 * 1024 * 1024:
                size_str = f"{total_size / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
            
            self.stats_table.setItem(row, 0, QTableWidgetItem(category))
            self.stats_table.setItem(row, 1, QTableWidgetItem(str(file_count)))
            self.stats_table.setItem(row, 2, QTableWidgetItem(size_str))
    
    def create_tools_tab(self):
        """Create the tools tab with additional functionality"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Duplicate file detection section
        duplicate_group = QGroupBox("Duplicate File Detection")
        duplicate_layout = QVBoxLayout(duplicate_group)
        
        # Enable duplicate detection
        self.duplicate_checkbox = QCheckBox("Enable duplicate file detection")
        self.duplicate_checkbox.setChecked(self.config.get("duplicate_detection", {}).get("enabled", False))
        duplicate_layout.addWidget(self.duplicate_checkbox)
        
        # Action selection
        action_layout = QHBoxLayout()
        action_label = QLabel("When duplicates are found:")
        self.duplicate_action_combo = QComboBox()
        self.duplicate_action_combo.addItems(["Notify only", "Move to duplicates folder", "Delete duplicates"])
        
        # Set current action
        current_action = self.config.get("duplicate_detection", {}).get("action", "notify")
        if current_action == "notify":
            self.duplicate_action_combo.setCurrentIndex(0)
        elif current_action == "move":
            self.duplicate_action_combo.setCurrentIndex(1)
        elif current_action == "delete":
            self.duplicate_action_combo.setCurrentIndex(2)
        
        action_layout.addWidget(action_label)
        action_layout.addWidget(self.duplicate_action_combo)
        duplicate_layout.addLayout(action_layout)
        
        # Scan button
        scan_button = QPushButton("Scan for Duplicates")
        scan_button.clicked.connect(self.scan_duplicates)
        duplicate_layout.addWidget(scan_button)
        
        # Progress bar
        self.duplicate_progress = QProgressBar()
        self.duplicate_progress.setVisible(False)
        duplicate_layout.addWidget(self.duplicate_progress)
        
        # Results list
        self.duplicate_list = QListWidget()
        duplicate_layout.addWidget(self.duplicate_list)
        
        layout.addWidget(duplicate_group)
        
        # Scheduled organization section
        schedule_group = QGroupBox("Scheduled Organization")
        schedule_layout = QVBoxLayout(schedule_group)
        
        # Enable scheduled organization
        self.schedule_checkbox = QCheckBox("Enable scheduled organization")
        self.schedule_checkbox.setChecked(self.config.get("scheduled_organization", {}).get("enabled", False))
        schedule_layout.addWidget(self.schedule_checkbox)
        
        # Frequency selection
        frequency_layout = QHBoxLayout()
        frequency_label = QLabel("Frequency:")
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Daily", "Weekly", "Monthly"])
        
        # Set current frequency
        current_frequency = self.config.get("scheduled_organization", {}).get("frequency", "daily")
        if current_frequency == "daily":
            self.frequency_combo.setCurrentIndex(0)
        elif current_frequency == "weekly":
            self.frequency_combo.setCurrentIndex(1)
        elif current_frequency == "monthly":
            self.frequency_combo.setCurrentIndex(2)
        
        frequency_layout.addWidget(frequency_label)
        frequency_layout.addWidget(self.frequency_combo)
        schedule_layout.addLayout(frequency_layout)
        
        # Time selection
        time_layout = QHBoxLayout()
        time_label = QLabel("Time:")
        self.time_edit = QTimeEdit()
        
        # Set current time
        current_time = self.config.get("scheduled_organization", {}).get("time", "00:00")
        try:
            hours, minutes = map(int, current_time.split(':'))
            self.time_edit.setTime(QDateTime.currentDateTime().time().addSecs(hours * 3600 + minutes * 60))
        except:
            self.time_edit.setTime(QDateTime.currentDateTime().time())
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        schedule_layout.addLayout(time_layout)
        
        layout.addWidget(schedule_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        tab.setWidget(content_widget)
        return tab
    
    def scan_duplicates(self):
        """Scan for duplicate files in the organized folders"""
        # Clear previous results
        self.duplicate_list.clear()
        self.duplicate_progress.setVisible(True)
        self.duplicate_progress.setValue(0)
        
        # Start scanning in a separate thread to avoid freezing the UI
        threading.Thread(target=self._scan_duplicates_thread, daemon=True).start()
    
    def _scan_duplicates_thread(self):
        """Background thread for duplicate scanning"""
        # Get all folders to scan
        folders_to_scan = list(self.config["folders"].values())
        
        # Dictionary to store file hashes
        file_hashes = defaultdict(list)
        total_files = 0
        processed_files = 0
        
        # First pass: count total files
        for folder in folders_to_scan:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    total_files += len(files)
        
        # Second pass: compute hashes
        for folder in folders_to_scan:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # For large files, just hash the first 8KB for speed
                            file_size = os.path.getsize(file_path)
                            if file_size > 8192:
                                with open(file_path, 'rb') as f:
                                    file_hash = hashlib.md5(f.read(8192)).hexdigest()
                            else:
                                with open(file_path, 'rb') as f:
                                    file_hash = hashlib.md5(f.read()).hexdigest()
                            
                            # Store the file path with its hash
                            file_hashes[file_hash].append(file_path)
                        except Exception as e:
                            print(f"Error hashing {file_path}: {e}")
                        
                        processed_files += 1
                        progress = int((processed_files / total_files) * 100) if total_files > 0 else 0
                        # Update UI from the main thread
                        self.duplicate_progress.setValue(progress)
        
        # Find duplicates (files with the same hash)
        duplicates = {hash_val: paths for hash_val, paths in file_hashes.items() if len(paths) > 1}
        
        # Update the UI with results
        if duplicates:
            for hash_val, paths in duplicates.items():
                # Add a header item for this set of duplicates
                self.duplicate_list.addItem(f"Found {len(paths)} duplicates:")
                
                # Add each duplicate file path
                for path in paths:
                    item = QListWidgetItem(f"  {path}")
                    item.setData(Qt.UserRole, path)  # Store the full path for later use
                    self.duplicate_list.addItem(item)
                
                # Add a separator
                self.duplicate_list.addItem("")
        else:
            self.duplicate_list.addItem("No duplicates found.")
        
        # Hide progress bar when done
        self.duplicate_progress.setVisible(False)
    
    def save_config(self):
        # Update config from UI (existing code)
        self.config["downloads_folder"] = self.downloads_folder_edit.text()
        self.config["notifications"] = self.notifications_checkbox.isChecked()
        
        # Update category folders
        for category, edit in self.category_edits.items():
            self.config["folders"][category] = edit.text()
        
        # Update file extensions
        for category, list_widget in self.extension_lists.items():
            extensions = []
            for i in range(list_widget.count()):
                extensions.append(list_widget.item(i).text())
            self.config["file_types"][category] = extensions
        
        # Update default mappings
        default_mappings = {}
        for i in range(self.default_mappings_list.count()):
            item_data = self.default_mappings_list.item(i).data(Qt.UserRole)
            default_mappings[item_data["extension"]] = item_data["category"]
        self.config["default_folder_mappings"] = default_mappings
        
        # Update retry settings
        self.config["retry_attempts"] = self.retry_attempts_spin.value()
        self.config["retry_delay"] = self.retry_delay_spin.value()
        
        # Update duplicate detection settings
        if not "duplicate_detection" in self.config:
            self.config["duplicate_detection"] = {}
        self.config["duplicate_detection"]["enabled"] = self.duplicate_checkbox.isChecked()
        
        action_index = self.duplicate_action_combo.currentIndex()
        if action_index == 0:
            self.config["duplicate_detection"]["action"] = "notify"
        elif action_index == 1:
            self.config["duplicate_detection"]["action"] = "move"
        elif action_index == 2:
            self.config["duplicate_detection"]["action"] = "delete"
        
        # Update scheduled organization settings
        if not "scheduled_organization" in self.config:
            self.config["scheduled_organization"] = {}
        self.config["scheduled_organization"]["enabled"] = self.schedule_checkbox.isChecked()
        
        frequency_index = self.frequency_combo.currentIndex()
        if frequency_index == 0:
            self.config["scheduled_organization"]["frequency"] = "daily"
        elif frequency_index == 1:
            self.config["scheduled_organization"]["frequency"] = "weekly"
        elif frequency_index == 2:
            self.config["scheduled_organization"]["frequency"] = "monthly"
        
        time = self.time_edit.time()
        self.config["scheduled_organization"]["time"] = f"{time.hour():02d}:{time.minute():02d}"
        
        # Save to file
        try:
            with open(self.config_path, 'w') as file:
                json.dump(self.config, file, indent=4)
            QMessageBox.information(self, "Success", "Configuration saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

def main():
    app = QApplication(sys.argv)
    
    # Set application style to Fusion for better theme support
    app.setStyle("Fusion")
    
    window = MessyFileOrganizerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()