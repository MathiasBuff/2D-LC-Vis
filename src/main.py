#!/usr/bin/env python3

import logging
import sys
import tkinter as tk
import ctypes
from pathlib import Path
from tkinter import ttk

from controller import AppController

def set_app_icon(hwnd, icon_path):
    # Load the icon
    icon = ctypes.windll.user32.LoadImageW(
        0, ctypes.c_wchar_p(icon_path), 1, 0, 0, 0x00000010  # IMAGE_ICON = 1, LR_LOADFROMFILE = 0x10
    )
    # Send the icon to the window
    ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, icon)  # WM_SETICON = 0x80
    ctypes.windll.user32.SendMessageW(hwnd, 0x80, 1, icon)  # For small icon too


def main():
    """
    Entry point for the application.
    When bundling application as executable, the main.py file is
    targeted, running this function to set up some basic configuration
    and launch the GUI.
    """

    # Handle case where app is running as executable
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = "."

    icon_path = Path(base_path, "utils", "eye-logo-transparent-textless.ico")

    # Logging configuration
    logger = setup_logging(base_path)

    # Create root application window and then hide it
    root = tk.Tk()
    root.withdraw()

    # Set style for the application
    root.style = ttk.Style(root)
    try:
        theme_path = Path(base_path, "utils", "theme", "azure.tcl")
        root.tk.call("source", theme_path)
        root.tk.call("set_theme", "light")
        root.style.theme_use("azure-light")
    except Exception as e:
        logger.warning(f"Failed to apply theme: {e}")
        root.style.theme_use(None)
    # root.iconbitmap(default=icon_path)

    # Launch the main window of the application
    logger.info("Starting up application.\n")
    AppController(root)

    # Close the splash image once everything is loaded
    try:
        import pyi_splash

        pyi_splash.close()
    except Exception as e:
        logger.debug(f"Tried to close splash screen unsuccessfully : {e}")

    root.update_idletasks()  # Make sure window exists

    # Set normal window icon
    root.iconbitmap(icon_path, default=icon_path)

    # # Set taskbar icon via ctypes
    # hwnd = ctypes.windll.user32.GetAncestor(root.winfo_id(), 2)  # GA_ROOT = 2
    # set_app_icon(hwnd, str(icon_path.absolute()))

    root.mainloop()


def setup_logging(base_path):
    logging.basicConfig(
        filename=Path(base_path, "utils", "runtime.log"),
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


if __name__ == "__main__":
    main()
