#!/usr/bin/env python3
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Messy File Organizer - A tool to organize your messy downloads folder")
    parser.add_argument('--cli', action='store_true', help='Run in command-line mode instead of GUI')
    parser.add_argument('--config', default=os.path.join(os.path.expanduser("~"), '.config', 'mfo', 'config.json'),
                        help='Path to configuration file')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    parser.add_argument('--log-to-file', action='store_true', help='Log to file instead of console')
    
    args = parser.parse_args()
    
    if args.cli:
        # Import and run the CLI version
        from script import main as cli_main
        cli_main(args)
    else:
        # Import and run the GUI version
        try:
            from PyQt5.QtWidgets import QApplication
            from gui import MessyFileOrganizerGUI
            
            app = QApplication(sys.argv)
            window = MessyFileOrganizerGUI()
            window.show()
            sys.exit(app.exec_())
        except ImportError:
            print("Error: PyQt5 is required for the GUI. Install it with 'pip install PyQt5' or run with --cli flag.")
            sys.exit(1)

if __name__ == "__main__":
    main()