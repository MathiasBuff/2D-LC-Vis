#!/usr/bin/env python3

import logging
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from controller import AppController


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
    root.iconbitmap(default=Path(base_path, "utils", "unige-icon.ico"))

    # Launch the main window of the application
    logger.info("Starting up application.\n")
    AppController(root)

    # Close the splash image once everything is loaded
    # try:
    #     import pyi_splash

    #     pyi_splash.close()
    # except Exception as e:
    #     logger.debug(f"Tried to close splash screen unsuccessfully : {e}")

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
