#!/usr/bin/env python3

import logging
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from gui import CentralWindow

def main():
    # Add permanent trace as backup log
    trace_log = Path("var", "trace.log")
    trace_handler = logging.FileHandler(trace_log, "a")
    # trace_handler.setFormatter(
    #     logging.Formatter(
    #         "%(asctime)s - %(levelname)-8s - %(message)s",
    #         datefmt="%Y-%m-%d %H:%M:%S",
    #     )
    # )
    logger = logging.getLogger()
    logger.addHandler(trace_handler)

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
    logger.debug("Starting up application.\n")
    CentralWindow(root)

    root.mainloop()

if __name__ == '__main__' :
    main()