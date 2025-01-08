#!/usr/bin/env python3

import logging
import time
import matplotlib
import matplotlib.pyplot
matplotlib.use('TkAgg')
import matplotlib.axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk

from backend import load_data, construct_axes, construct_matrix, get_figure_contour
from opendialog import ask_file
from mplgraphs import ContourGraph, XYZGraph, OverlayGraph, RawGraph


# Use root logger so that all modules can access it
logger = logging.getLogger()

PADDINGS = {"padx": 10, "pady": 10}

class GraphPage(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.mpl_canvas = FigureCanvasTkAgg(None, self)

    def add_mpl_figure(self, fig):
        self.mpl_canvas = FigureCanvasTkAgg(fig, self)
        self.mpl_canvas.draw()
        self.mpl_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _clear(self):
        for child in self.winfo_children():
            child.destroy()


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

        self.calc_frame = ttk.Labelframe(self, text="Calculation Conditions")
        self.output_note = ttk.Notebook(self)
        self.calc_frame.grid(column=0, row=1, sticky="nsew", **PADDINGS)
        self.output_note.grid(column=2, row=0, rowspan=2, sticky="nsew", **PADDINGS)
        ttk.Separator(self, orient="vertical").grid(
            column=1, row=0, rowspan=2, sticky="ns", **PADDINGS
        )
        self.rowconfigure(1, weight=1)
        
        self.load_btn = ttk.Button(self, text="Load Excel File", command=self.load)
        self.load_btn.grid(column=0, row=0, sticky="nsew", **PADDINGS)

        st_frame = ttk.Frame(self.calc_frame)
        shift_frame = ttk.Frame(self.calc_frame)

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
        
        blank_frame = ttk.Frame(self.calc_frame)
        blank_frame.pack(side="top", expand=False, fill="both", **PADDINGS)
        
        self.blk_checkbox = ttk.Checkbutton(blank_frame)
        self.blk_checkbox.grid(column=0, row=0)
        self.blk_checkbox.state(["!alternate"])
        
        ttk.Label(blank_frame, text="Blank Substraction", anchor="w").grid(
            column=1, row=0, sticky="nsew"
        )
        
        self.blk_entry = ttk.Entry(blank_frame)
        self.blk_entry.grid(column=1, row=1, sticky="nsew")
        
        self.blk_entry.insert(tk.END, "Not Implemented")
        self.blk_entry['state'] = "disabled"
        
        blank_frame.columnconfigure(1, weight=1)
        
        self.process_btn = ttk.Button(self.calc_frame, text="Process Data", command=self.process)
        self.process_btn.pack(side="top", expand=False, fill="both", **PADDINGS)
        
        self.output_contour = ttk.LabelFrame(self.output_note, text="Contour Plot")
        self.output_contour.pack(fill='both', expand=True)
        self.output_note.add(self.output_contour, text="Contour")
        
        self.output_xyz = ttk.LabelFrame(self.output_note, text="3D Plot")
        self.output_xyz.pack(fill='both', expand=True)
        self.output_note.add(self.output_xyz, text="3D Plot")
        
        self.output_overlay = ttk.LabelFrame(self.output_note, text="2D Overlay")
        self.output_overlay.pack(fill='both', expand=True)
        self.output_note.add(self.output_overlay, text="2D Overlay")
        
        self.output_raw = ttk.LabelFrame(self.output_note, text="2D Raw")
        self.output_raw.pack(fill='both', expand=True)
        self.output_note.add(self.output_raw, text="2D Raw")
                
        self.contour_graph = GraphPage(self.output_contour)
        self.xyz_graph = GraphPage(self.output_xyz)
        self.overlay_graph = GraphPage(self.output_overlay)
        self.raw_graph = GraphPage(self.output_raw)
        
        self.contour_graph.grid(column=0, row=0, columnspan=7, sticky="nsew")
        self.xyz_graph.grid(column=0, row=0, columnspan=7, sticky="nsew")
        self.overlay_graph.grid(column=0, row=0, columnspan=7, sticky="nsew")
        self.raw_graph.grid(column=0, row=0, columnspan=7, sticky="nsew")
        
        ttk.Label(self.output_contour, text="X min:", width=10, anchor="e").grid(column=0, row=1, sticky="w")
        self.output_contour.x_min = ttk.Entry(self.output_contour, width=5)
        self.output_contour.x_min.grid(column=1, row=1, sticky="w", padx=(0, 10), pady=5)
        ttk.Label(self.output_contour, text="Y min:", width=10, anchor="e").grid(column=2, row=1, sticky="w")
        self.output_contour.y_min = ttk.Entry(self.output_contour, width=5)
        self.output_contour.y_min.grid(column=3, row=1, sticky="w", padx=(0, 10), pady=5)
        ttk.Label(self.output_contour, text="Z min:", width=10, anchor="e").grid(column=4, row=1, sticky="w")
        self.output_contour.z_min = ttk.Entry(self.output_contour, width=5)
        self.output_contour.z_min.grid(column=5, row=1, sticky="w", padx=(0, 10), pady=5)
        
        ttk.Label(self.output_contour, text="X max:", width=10, anchor="e").grid(column=0, row=2, sticky="w")
        self.output_contour.x_max = ttk.Entry(self.output_contour, width=5)
        self.output_contour.x_max.grid(column=1, row=2, sticky="w", padx=(0, 10), pady=5)
        ttk.Label(self.output_contour, text="Y max:", width=10, anchor="e").grid(column=2, row=2, sticky="w")
        self.output_contour.y_max = ttk.Entry(self.output_contour, width=5)
        self.output_contour.y_max.grid(column=3, row=2, sticky="w", padx=(0, 10), pady=5)
        ttk.Label(self.output_contour, text="Z max:", width=10, anchor="e").grid(column=4, row=2, sticky="w")
        self.output_contour.z_max = ttk.Entry(self.output_contour, width=5)
        self.output_contour.z_max.grid(column=5, row=2, sticky="w", padx=(0, 10), pady=5)
        
        self.output_contour.columnconfigure(6, weight=1)
        self.output_xyz.columnconfigure(6, weight=1)
        self.output_overlay.columnconfigure(6, weight=1)
        self.output_raw.columnconfigure(6, weight=1)
        
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

        self.draw_contour()
        self.draw_xyz()
        self.draw_overlay()
        self.draw_raw()    
        
        return


    def draw_contour(self):
        try:
            limits_x = (float(self.output_contour.x_min.get()), float(self.output_contour.x_max.get()))
        except:
            limits_x = None
        try:
            limits_y = (float(self.output_contour.y_min.get()), float(self.output_contour.y_max.get()))
        except:
            limits_y = None
        try:
            limits_z = (float(self.output_contour.z_min.get()), float(self.output_contour.z_max.get()))
        except:
            limits_z = None

        fig_contour = ContourGraph(
            self.ax_D2,
            self.ax_D1,
            self.value_matrix,
            limits_x=limits_x,
            limits_y=limits_y,
            limits_z=limits_z,
        )
        
        self.contour_graph._clear()
        self.contour_graph.add_mpl_figure(fig_contour)
        
        return fig_contour

    def draw_xyz(self):
        fig_xyz = XYZGraph(
            self.ax_D2,
            self.ax_D1,
            self.value_matrix
        )
        
        self.xyz_graph._clear()
        self.xyz_graph.add_mpl_figure(fig_xyz)
        
        return fig_xyz

    def draw_overlay(self):
        fig_overlay = OverlayGraph(
            self.ax_D2,
            self.ax_D1,
            self.value_matrix
        )
        
        self.overlay_graph._clear()
        self.overlay_graph.add_mpl_figure(fig_overlay)
        
        return fig_overlay

    def draw_raw(self):
        fig_raw = RawGraph(
            self.data[:, 0],
            self.data[:, 1]
        )
        
        self.raw_graph._clear()
        self.raw_graph.add_mpl_figure(fig_raw)
        
        return fig_raw

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
