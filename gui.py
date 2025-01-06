#!/usr/bin/env python3

import logging
import threading
import time
import tkinter as tk
from tkinter import ttk

# Use root logger so that all modules can access it
logger = logging.getLogger()

PADDINGS = {"padx": 10, "pady": 10}

class CentralWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)

        self.master = master
        master.withdraw()

        self.body()
        self.bind("<Control-q>", self.on_exit)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def body(self):

        # theme set in class unncessary dependency ?
        # self.tk.call("source", r"Azure-ttk-theme-main\azure.tcl")
        # self.tk.call("set_theme", "dark")

        self.iconbitmap(default=r"graphics\unige-icon.ico")
        self.title("2D-LC Chromatogram Visualization")

        windowWidth = 1280
        windowHeight = 720
        screenWidth = self.master.winfo_screenwidth()
        screenHeight = self.master.winfo_screenheight()
        xCoordinate = int((screenWidth / 2) - (windowWidth / 2))
        yCoordinate = int((screenHeight / 2) - (windowHeight / 2))
        self.geometry(f"{windowWidth}x{windowHeight}+{xCoordinate}+{yCoordinate}")
        # self.resizable(False, False)

        menu = tk.Menu(self)
        self.config(menu=menu)

        file_menu = tk.Menu(menu)
        # dev_menu = tk.Menu(menu)

        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open")
        file_menu.add_cascade(label="Save")

        # menu.add_cascade(label="Dev", menu=dev_menu)
        # dev_menu.add_command(label="Test", command=self.test)

        self.frame1 = ttk.Labelframe(self, text="Calculation Conditions")
        self.frame2 = ttk.Labelframe(self, text="Log output")
        self.frame1.grid(column=0, row=0, sticky="nsew", **PADDINGS)
        self.frame2.grid(column=2, row=0, sticky="nsew", **PADDINGS)
        ttk.Separator(self, orient="vertical").grid(
            column=1, row=0, rowspan=2, sticky="ns", **PADDINGS
        )

        topframe = ttk.Frame(self.frame1)
        botframe = ttk.Frame(self.frame1)

        topframe.pack(side="top", expand="no", fill="both", **PADDINGS)
        botframe.pack(side="top", expand="no", fill="both", **PADDINGS)

        ttk.Label(topframe, text="Sampling time (min) :", anchor="w", width=20).pack(
            side="left", fill="x", expand="no"
        )
        ttk.Label(botframe, text="Time shift (s) :", anchor="w", width=20).pack(
            side="left", fill="x", expand="no"
        )

        self.usr = ttk.Entry(topframe)
        self.usr.pack(side="right", fill="x", expand="yes")
        self.pwd = ttk.Entry(botframe)
        self.pwd.pack(side="right", fill="x", expand="yes")
        
        return

    def on_exit(self, event=None):
        logger.debug("Exiting application.\n")
        self.destroy()
        self.master.destroy()

def freeze_buttons(widget: tk.Tk | tk.Toplevel):

    _list = widget.winfo_children()

    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())

    buttons_list = []
    for child in _list:
        if type(child) is tk.Button or type(child) is ttk.Button:
            buttons_list.append((child, child["state"]))

    for button in buttons_list:
        button[0].config(state="disabled")

    time.sleep(2)

    for button in buttons_list:
        button[0].config(state=button[1])
