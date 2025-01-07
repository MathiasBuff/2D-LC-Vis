#!/usr/bin/env python3

import logging
import time
import tkinter as tk
from tkinter import ttk

from backend import load_data, construct_axes, construct_matrix, plot
from opendialog import ask_file

# Use root logger so that all modules can access it
logger = logging.getLogger()

PADDINGS = {"padx": 10, "pady": 10}

class CentralWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)

        self.master = master
        master.withdraw()
        
        self.data = None

        self.body()
        self.bind("<Control-q>", self.on_exit)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def body(self):
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

        self.frame1 = ttk.Labelframe(self, text="Calculation Conditions")
        self.frame2 = ttk.Labelframe(self, text="Log output")
        self.frame1.grid(column=0, row=1, sticky="nsew", **PADDINGS)
        self.frame2.grid(column=2, row=0, rowspan=2, sticky="nsew", **PADDINGS)
        ttk.Separator(self, orient="vertical").grid(
            column=1, row=0, rowspan=2, sticky="ns", **PADDINGS
        )
        
        self.load_btn = ttk.Button(self, text="Load Excel File", command=self.load)
        self.load_btn.grid(column=0, row=0, sticky="nsew", **PADDINGS)

        st_frame = ttk.Frame(self.frame1)
        shift_frame = ttk.Frame(self.frame1)

        st_frame.pack(side="top", expand=False, fill="both", **PADDINGS)
        shift_frame.pack(side="top", expand=False, fill="both", **PADDINGS)

        ttk.Label(st_frame, text="Sampling time (min) :", anchor="w", width=20).pack(
            side="left", fill="x", expand=False
        )
        ttk.Label(shift_frame, text="Time shift (s) :", anchor="w", width=20).pack(
            side="left", fill="x", expand=False
        )

        self.st_entry = ttk.Entry(st_frame)
        self.st_entry.pack(side="right", fill="x", expand="yes")
        self.shift_entry = ttk.Entry(shift_frame)
        self.shift_entry.pack(side="right", fill="x", expand="yes")
        
        self.shift_entry.insert(tk.END, "Not Implemented")
        self.shift_entry['state'] = "disabled"
        
        blank_frame = ttk.Frame(self.frame1)
        blank_frame.pack(side="top", expand=True, fill="both", **PADDINGS)
        
        self.blk_checkbox = ttk.Checkbutton(blank_frame)
        self.blk_checkbox.grid(column=0, row=0)
        
        # Invoke twice to set "off", otherwise state is weird at launch
        self.blk_checkbox.invoke()
        self.blk_checkbox.invoke()
        
        ttk.Label(blank_frame, text="Blank Substraction", anchor="w").grid(
            column=1, row=0, sticky="nsew"
        )
        
        self.blk_entry = ttk.Entry(blank_frame)
        self.blk_entry.grid(column=1, row=1, sticky="nsew")
        
        self.blk_entry.insert(tk.END, "Not Implemented")
        self.blk_entry['state'] = "disabled"
        
        blank_frame.columnconfigure(1, weight=1)
        
        self.process_btn = ttk.Button(self.frame1, text="Process Data", command=self.process)
        self.process_btn.pack(side="top", expand=False, fill="both", **PADDINGS)
        
        return

    def load(self):
        file_parameters = ask_file()
        self.data = load_data(
            file_parameters["path"],
            file_parameters["sheet"],
            file_parameters["headers"],
        )
        print("data loaded.")
    
    def process(self):
        self.ax_D1, self.ax_D2 = construct_axes(
            self.data[:, 0],
            float(self.st_entry.get()),
        )
        
        self.value_matrix = construct_matrix(
            self.data[:, 1],
            self.ax_D1,
            self.ax_D2,
        )
        
        print(self.ax_D1, self.ax_D2)
        print(self.value_matrix.shape)
        
        plot(self.ax_D2, self.ax_D1, self.value_matrix, range(5, 100, 1))
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
