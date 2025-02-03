#!/usr/bin/env python3

import sys
from pathlib import Path
import logging
import threading
import time

import matplotlib
import matplotlib.pyplot
import matplotlib.style

matplotlib.use("TkAgg")
matplotlib.style.use("fast")
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
from tkinter import ttk

import matplotlib.axes
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from calculations import construct_axes, construct_matrix, load_data
from visualization import (ContourPage, OverlayPage, ProjectionsPage, RawPage,
                       XYZPage)
from files import ask_file

# Use root logger so that all modules can access it
logger = logging.getLogger()

PADDINGS = {"padx": 10, "pady": 10}
LOGGING_LEVEL = logging.DEBUG


class TextHandler(logging.Handler):
    """
    This class allows you to log to a Tkinter Text or ScrolledText widget.

    Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    """

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state="normal")
            self.text.insert(tk.END, msg + "\n")
            self.text.configure(state="disabled")
            # Autoscroll to the bottom
            self.text.yview(tk.END)

        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


class CentralWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)

        self.master = master
        master.withdraw()

        self.data = None
        self.flag_dev = False

        self.body()
        logging.info("2D-LC Visualizer v0.1.0")
        logging.info("-" * 42)
        self.bind("<Control-q>", self.on_exit)
        self.bind("<Control-Shift-D>", self.toggle_dev)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def body(self):
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = "."

        self.iconbitmap(default=Path(base_path, "utils", "unige-icon.ico"))
        self.title("2D-LC Chromatogram Visualization")

        windowWidth = 1280
        windowHeight = 720
        screenWidth = self.master.winfo_screenwidth()
        screenHeight = self.master.winfo_screenheight()
        xCoordinate = int((screenWidth / 2) - (windowWidth / 2))
        yCoordinate = int((screenHeight / 2) - (windowHeight / 2))
        self.geometry(f"{windowWidth}x{windowHeight}+{xCoordinate}+{yCoordinate}")
        # self.resizable(False, False)

        self.calc_frame = ttk.Labelframe(self, text="Calculation Conditions")
        self.output_note = ttk.Notebook(self)
        self.console_frame = ttk.Labelframe(self, text="Log output")
        self.calc_frame.grid(column=0, row=1, sticky="new", **PADDINGS)
        self.output_note.grid(column=2, row=0, rowspan=3, sticky="nsew", **PADDINGS)
        self.console_frame.grid(column=0, row=2, sticky="sew", **PADDINGS)
        ttk.Separator(self, orient="vertical").grid(
            column=1, row=0, rowspan=3, sticky="ns", **PADDINGS
        )
        self.rowconfigure(2, weight=1)
        self.columnconfigure(2, weight=1)

        self.load_btn = ttk.Button(self, text="Load Excel File", command=self.load)
        self.load_btn.grid(column=0, row=0, sticky="nsew", **PADDINGS)

        st_frame = ttk.Frame(self.calc_frame)
        shift_frame = ttk.Frame(self.calc_frame)
        cf_frame = ttk.Frame(self.calc_frame)

        st_frame.pack(side="top", expand=False, fill="both", **PADDINGS)
        shift_frame.pack(side="top", expand=False, fill="both", **PADDINGS)
        cf_frame.pack(side="top", expand=False, fill="both", **PADDINGS)

        ttk.Label(st_frame, text="Sampling time (min) :", anchor="w", width=20).pack(
            side="left", fill="x", expand=False
        )
        ttk.Label(shift_frame, text="Time shift (s) :", anchor="w", width=20).pack(
            side="left", fill="x", expand=False
        )
        ttk.Label(cf_frame, text="Correction factor :", anchor="w", width=20).pack(
            side="left", fill="x", expand=False
        )

        self.st_entry = ttk.Entry(st_frame)
        self.st_entry.pack(side="right", fill="none", expand="yes")
        self.shift_entry = ttk.Entry(shift_frame)
        self.shift_entry.pack(side="right", fill="none", expand="yes")
        self.cf_entry = ttk.Entry(cf_frame)
        self.cf_entry.pack(side="right", fill="none", expand="yes")
        
        self.shift_entry.insert("end", "0")
        self.cf_entry.insert("end", "0")

        blank_frame = ttk.Frame(self.calc_frame)
        blank_frame.pack(side="top", expand=False, fill="both", **PADDINGS)

        self.blk_checkbox = ttk.Checkbutton(blank_frame)
        self.blk_checkbox.grid(column=0, row=0)
        self.blk_checkbox.state(["!alternate"])

        ttk.Label(blank_frame, text="Blank Substraction", anchor="w").grid(
            column=1, row=0, sticky="nsew"
        )

        self.blk_entry = ttk.Entry(blank_frame)
        self.blk_entry.grid(column=1, row=1, sticky="nsw")
        self.blk_entry.insert(tk.END, "10")
        # self.blk_entry.state(["disabled"])

        blank_frame.columnconfigure(1, weight=1)

        self.process_btn = ttk.Button(
            self.calc_frame, text="Process Data", command=self.process_gui
        )
        self.process_btn.pack(side="top", expand=False, fill="both", **PADDINGS)

        console = ScrolledText.ScrolledText(
            self.console_frame, width=15, height=20, state="disabled"
        )
        console.configure(font="Calibri")
        console.grid(column=0, row=0, sticky="nsew", **PADDINGS)

        self.console_frame.columnconfigure(0, weight=1)
        self.console_frame.rowconfigure(0, weight=1)

        # Create textLogger
        text_handler = TextHandler(console)

        # Add the handler to logger
        logger.addHandler(text_handler)
        text_handler.setLevel(LOGGING_LEVEL)

        self.pb = ttk.Progressbar(
            self.console_frame, orient="horizontal", mode="determinate"
        )
        self.pb.grid(column=0, row=1, sticky="nsew", **PADDINGS)

        self.contour_page = ContourPage(self.output_note)
        self.contour_page.pack(fill="both", expand=True)
        self.output_note.add(self.contour_page, text="2D Contour")

        self.xyz_page = XYZPage(self.output_note)
        self.xyz_page.pack(fill="both", expand=True)
        self.output_note.add(self.xyz_page, text="3D Contour")

        self.overlay_page = OverlayPage(self.output_note)
        self.overlay_page.pack(fill="both", expand=True)
        self.output_note.add(self.overlay_page, text="Overlay")

        self.raw_page = RawPage(self.output_note)
        self.raw_page.pack(fill="both", expand=True)
        self.output_note.add(self.raw_page, text="Raw")

        return

    def load(self):
        logging.info("Asking user for Excel file...")
        file_parameters = ask_file()
        logging.debug(f"ask_file dialog exited with {file_parameters}")
        threading.Thread(
            target=load_data,
            args=[
                self,
                file_parameters["path"],
                file_parameters["sheet"],
                file_parameters["headers"],
            ],
        ).start()
        threading.Thread(
            target=freeze_buttons,
            args=[self],
        ).start()

    def process_gui(self):
        logging.info("Processing data...")
        threading.Thread(
            target=self._process,
        ).start()
        threading.Thread(
            target=freeze_buttons,
            args=[self],
        ).start()

    def _process(self):
        self.ax_D1, self.ax_D2 = construct_axes(
            self.data[:, 0],
            float(self.st_entry.get()),
        )

        self.value_matrix = construct_matrix(
            self.data[:, 1],
            self.ax_D1,
            self.ax_D2,
            float(self.shift_entry.get()),
            float(self.cf_entry.get())
        )

        if self.blk_checkbox.instate(["selected"]):
            try:
                blank_time = float(self.blk_entry.get())
                blank_line = np.where(self.ax_D1 <= blank_time)[0][-1]
                
                logging.info(f"Substracting data at {self.ax_D1[blank_line]:.4f} min.")
                self.value_matrix = (
                    self.value_matrix.transpose() - self.value_matrix[:, blank_line]
                )
                self.value_matrix = self.value_matrix.transpose()
            except:
                pass

        logging.info("Processing complete.")
        logging.info("Drawing figures...")

        self.draw_contour()
        self.draw_xyz()
        self.draw_overlay()
        self.draw_raw()

        logging.info("Done.")

        try:
            self.draw_projections()
        except:
            pass

        return

    def draw_contour(self):
        self.contour_page.set_data(self.ax_D2, self.ax_D1, self.value_matrix)
        self.contour_page.update_figure()

    def draw_xyz(self):
        self.xyz_page.set_data(self.ax_D2, self.ax_D1, self.value_matrix)
        self.xyz_page.update_figure()

    def draw_overlay(self):
        self.overlay_page.set_data(self.ax_D2, self.ax_D1, self.value_matrix)
        self.overlay_page.update_figure()

    def draw_raw(self):
        self.raw_page.set_data(self.data[:, 0], self.data[:, 1])
        self.raw_page.update_figure()

    def draw_projections(self):
        self.projections_page.set_data(self.ax_D2, self.ax_D1, self.value_matrix)
        self.projections_page.update_figure()

    def on_exit(self, event=None):
        logger.debug("Exiting application.\n")
        self.destroy()
        self.master.destroy()

    def toggle_dev(self, event=None):
        if not self.flag_dev:
            self.dev_menu = tk.Menu(self)
            self.config(menu=self.dev_menu)
            self.dev_menu.add_command(
                label="Projections Graph", command=self.toggle_projections
            )
        else:
            self.dev_menu.destroy()

        self.flag_dev = not self.flag_dev

    def toggle_projections(self):
        try:
            self.projections_page.destroy()
        except:
            self.projections_page = ProjectionsPage(self.output_note)
            self.projections_page.pack(fill="both", expand=True)
            self.output_note.add(self.projections_page, text="Projections")


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

    time.sleep(1)

    for button in buttons_list:
        button[0].config(state=button[1])
