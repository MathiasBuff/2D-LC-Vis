#!/usr/bin/env python3

import logging
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from gui import CentralWindow


def main():
    # Logging configuration
    logging.basicConfig(
        filename="runtime.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger()

    # Create root application window and then hide it
    root = tk.Tk()
    root.withdraw()

    # Set style for the application
    theme_path = Path("graphics", "theme", "azure.tcl")
    root.style = ttk.Style(root)
    root.tk.call("source", theme_path)
    root.tk.call("set_theme", "light")
    root.style.theme_use("azure-light")

    # Launch the main window of the application
    logger.info("Starting up application.\n")
    CentralWindow(root)

    root.mainloop()


if __name__ == "__main__":
    main()
