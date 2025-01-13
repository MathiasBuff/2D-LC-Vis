#!/usr/bin/env python3

import logging
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

CMAP_LIST = list(colormaps)
CMAP_DEFAULT = "jet"

logger = logging.getLogger(__name__)

class ContourPage(ttk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.figure = Figure(figsize=(5, 3.3), dpi=150)
        self.x_array = np.array([0, 1])
        self.y_array = np.array([0, 1])
        self.z_array = np.array([[0, 0.5], [0.5, 1]])
        self.params = {"color_u": "#0000FF", "color_o": "#FF0000"}

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.param_frame = ttk.LabelFrame(self, text="Graph Settings")

        ttk.Label(self.param_frame, text="D2 min:", width=8, anchor="e").grid(column=0, row=0, sticky="e", pady=(10, 0))
        self.x_min = ttk.Entry(self.param_frame, width=15)
        self.x_min.grid(column=1, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="D1 min:", width=8, anchor="e").grid(column=2, row=0, sticky="e", pady=(10, 0))
        self.y_min = ttk.Entry(self.param_frame, width=15)
        self.y_min.grid(column=3, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="Val min:", width=8, anchor="e").grid(column=4, row=0, sticky="e", pady=(10, 0))
        self.v_min = ttk.Entry(self.param_frame, width=15)
        self.v_min.grid(column=5, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        
        ttk.Label(self.param_frame, text="D2 max:", width=8, anchor="e").grid(column=0, row=1, sticky="e", pady=(10, 0))
        self.x_max = ttk.Entry(self.param_frame, width=15)
        self.x_max.grid(column=1, row=1, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="D1 max:", width=8, anchor="e").grid(column=2, row=1, sticky="e", pady=(10, 0))
        self.y_max = ttk.Entry(self.param_frame, width=15)
        self.y_max.grid(column=3, row=1, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="Val max:", width=8, anchor="e").grid(column=4, row=1, sticky="e", pady=(10, 0))
        self.v_max = ttk.Entry(self.param_frame, width=15)
        self.v_max.grid(column=5, row=1, sticky="w", padx=(0, 10), pady=(10, 0))

        ttk.Button(self.param_frame, text="Apply", width=15, command=self.update_figure).grid(column=7, row=0, sticky="w", padx=30, pady=(10, 0))
        ttk.Button(self.param_frame, text="Reset", width=15, command=self.reset_params).grid(column=7, row=1, sticky="w", padx=30, pady=(10, 0))

        self.update_figure()

        ttk.Separator(self.param_frame, orient="horizontal").grid(
            column=0, row=2, columnspan=9, sticky="ew", padx=20, pady=10
        )

        ttk.Label(self.param_frame, text="Colormap:", width=15, anchor="e").grid(column=0, row=3, sticky="e", pady=(0, 10))
        self.cmap_cb = ttk.Combobox(self.param_frame, values=CMAP_LIST, state="readonly", width=15)
        self.cmap_cb.grid(column=1, row=3, columnspan=2, sticky="ew", padx=(0, 10), pady=(0, 10))
        self.cmap_cb.current(CMAP_LIST.index(CMAP_DEFAULT))
        self.cmap_cb.bind("<<ComboboxSelected>>", lambda e: self.update_figure())

        ttk.Label(self.param_frame, text="Under/Over:", width=12, anchor="e").grid(column=3, row=3, sticky="e", pady=(0, 10))
        
        frame_color_under = tk.Frame(self.param_frame, background="#cccccc", height=25, width=25)
        frame_color_under.grid(column=4, row=3, sticky="w", padx=(0, 0), pady=(0, 10))
        self.color_under_btn = tk.Button(frame_color_under, height=1, width=1, command=lambda: self.choose_color("under"))
        self.color_under_btn.place(relw=0.7, relh=0.7, relx=0.14, rely=0.14)
        self.color_under_btn.configure(background=self.params["color_u"], relief="flat")

        frame_color_over = tk.Frame(self.param_frame, background="#cccccc", height=25, width=25)
        frame_color_over.grid(column=4, row=3, columnspan=2, sticky="w", padx=(30, 0), pady=(0, 10))
        self.color_over_btn = tk.Button(frame_color_over, height=1, width=1, command=lambda: self.choose_color("over"))
        self.color_over_btn.place(relw=0.7, relh=0.7, relx=0.14, rely=0.14)
        self.color_over_btn.configure(background=self.params["color_o"], relief="flat")

        self.canvas.get_tk_widget().pack(side="top", fill="none", expand=True)
        self.param_frame.pack(side="bottom", fill="none", expand=True)


    def set_data(self, x, y, z):
        self.x_array = x
        self.y_array = y
        self.z_array = z
    
    def choose_color(self, extreme: str):
        _, color = askcolor()
        if extreme == "under":
            self.color_under_btn.configure(background=color)
            self.params["color_u"] = color
        elif extreme == "over":
            self.color_over_btn.configure(background=color)
            self.params["color_o"] = color
        
        self.update_figure()


    def update_figure(self):
        self.figure.clf()
        self.figure = self.draw_axes(self.x_array, self.y_array, self.z_array)
        self.canvas.draw()

    def reset_params(self):
        self.x_min.delete(0, "end")
        self.x_max.delete(0, "end")
        self.y_min.delete(0, "end")
        self.y_max.delete(0, "end")
        self.v_min.delete(0, "end")
        self.v_max.delete(0, "end")
        self.cmap_cb.current(CMAP_LIST.index(CMAP_DEFAULT))
        self.update_figure()

    def draw_axes(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
    ) -> Figure:
        self.params["x_min"] = self.x_min.get()
        self.params["x_max"] = self.x_max.get()
        self.params["y_min"] = self.y_min.get()
        self.params["y_max"] = self.y_max.get()
        self.params["v_min"] = self.v_min.get()
        self.params["v_max"] = self.v_max.get()

        for key in ["x_min", "x_max", "y_min", "y_max", "v_min", "v_max"]:
            try:
                self.params[key] = float(self.params[key])
            except:
                self.params[key] = None
        
        self.figure.add_subplot()
        self.figure.subplots_adjust(0.15, 0.2, 0.9, 0.9)
        axes = self.figure.axes[0]

        try:
            cmap = plt.colormaps[self.cmap_cb.get()].with_extremes(
                under=self.params["color_u"], over=self.params["color_o"]
            )
        except:
            cmap = ListedColormap(["#FFFFFF"])

        if self.params["x_min"] == None:
            self.params["x_min"] = x.min()
        if self.params["x_max"] == None:
            self.params["x_max"] = x.max()
        if self.params["y_min"] == None:
            self.params["y_min"] = y.min()
        if self.params["y_max"] == None:
            self.params["y_max"] = y.max()
        if self.params["v_min"] == None:
            self.params["v_min"] = z.min()
        if self.params["v_max"] == None:
            self.params["v_max"] = z.max()

        axes.set_xlim(self.params["x_min"], self.params["x_max"])
        axes.set_ylim(self.params["y_min"], self.params["y_max"])
        axes.set_xlabel("D2 [s]")
        axes.set_ylabel("D1 [min]")

        levels = np.linspace(self.params["v_min"], self.params["v_max"], 100)

        cs = axes.contourf(x, y, z, levels, cmap=cmap, extend="both")
        cbar = self.figure.colorbar(cs)

        return self.figure


class XYZPage(ttk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.figure = Figure(figsize=(5, 3.3), dpi=150)
        self.x_array = np.array([0, 1])
        self.y_array = np.array([0, 1])
        self.z_array = np.array([[0, 0.5], [0.5, 1]])
        self.params = {"color_u": "#0000FF", "color_o": "#FF0000"}

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.param_frame = ttk.LabelFrame(self, text="Graph Settings")

        ttk.Label(self.param_frame, text="D2 min:", width=8, anchor="e").grid(column=0, row=0, sticky="e", pady=(10, 0))
        self.x_min = ttk.Entry(self.param_frame, width=15)
        self.x_min.grid(column=1, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="D1 min:", width=8, anchor="e").grid(column=2, row=0, sticky="e", pady=(10, 0))
        self.y_min = ttk.Entry(self.param_frame, width=15)
        self.y_min.grid(column=3, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="Val min:", width=8, anchor="e").grid(column=4, row=0, sticky="e", pady=(10, 0))
        self.v_min = ttk.Entry(self.param_frame, width=15)
        self.v_min.grid(column=5, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        
        ttk.Label(self.param_frame, text="D2 max:", width=8, anchor="e").grid(column=0, row=1, sticky="e", pady=(10, 0))
        self.x_max = ttk.Entry(self.param_frame, width=15)
        self.x_max.grid(column=1, row=1, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="D1 max:", width=8, anchor="e").grid(column=2, row=1, sticky="e", pady=(10, 0))
        self.y_max = ttk.Entry(self.param_frame, width=15)
        self.y_max.grid(column=3, row=1, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="Val max:", width=8, anchor="e").grid(column=4, row=1, sticky="e", pady=(10, 0))
        self.v_max = ttk.Entry(self.param_frame, width=15)
        self.v_max.grid(column=5, row=1, sticky="w", padx=(0, 10), pady=(10, 0))

        ttk.Button(self.param_frame, text="Apply", width=15, command=self.update_figure).grid(column=7, row=0, sticky="w", padx=30, pady=(10, 0))
        ttk.Button(self.param_frame, text="Reset", width=15, command=self.reset_params).grid(column=7, row=1, sticky="w", padx=30, pady=(10, 0))

        self.update_figure()

        ttk.Separator(self.param_frame, orient="horizontal").grid(
            column=0, row=2, columnspan=9, sticky="ew", padx=20, pady=10
        )

        ttk.Label(self.param_frame, text="Colormap:", width=15, anchor="e").grid(column=0, row=3, sticky="e", pady=(0, 10))
        self.cmap_cb = ttk.Combobox(self.param_frame, values=CMAP_LIST, state="readonly", width=15)
        self.cmap_cb.grid(column=1, row=3, columnspan=2, sticky="ew", padx=(0, 10), pady=(0, 10))
        self.cmap_cb.current(CMAP_LIST.index(CMAP_DEFAULT))
        self.cmap_cb.bind("<<ComboboxSelected>>", lambda e: self.update_figure())
        
        ttk.Label(self.param_frame, text="Line count:", width=12, anchor="e").grid(column=3, row=3, sticky="e", pady=(0, 10))
        self.level_count = ttk.Entry(self.param_frame, width=10)
        self.level_count.grid(column=4, row=3, columnspan=2, sticky="w", padx=(0, 10), pady=(0, 10))
        self.level_count.insert(0, "100")

        self.canvas.get_tk_widget().pack(side="top", fill="none", expand=True)
        self.param_frame.pack(side="bottom", fill="none", expand=True)


    def set_data(self, x, y, z):
        self.x_array = x
        self.y_array = y
        self.z_array = z
    

    def update_figure(self):
        self.figure.clf()
        self.figure = self.draw_axes(self.x_array, self.y_array, self.z_array)
        self.canvas.draw()

    def reset_params(self):
        self.x_min.delete(0, "end")
        self.x_max.delete(0, "end")
        self.y_min.delete(0, "end")
        self.y_max.delete(0, "end")
        self.v_min.delete(0, "end")
        self.v_max.delete(0, "end")
        self.update_figure()

    def draw_axes(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
    ) -> Figure:
        self.params["x_min"] = self.x_min.get()
        self.params["x_max"] = self.x_max.get()
        self.params["y_min"] = self.y_min.get()
        self.params["y_max"] = self.y_max.get()
        self.params["v_min"] = self.v_min.get()
        self.params["v_max"] = self.v_max.get()

        for key in ["x_min", "x_max", "y_min", "y_max", "v_min", "v_max"]:
            try:
                self.params[key] = float(self.params[key])
            except:
                self.params[key] = None
        
        try:
            self.params["level_count"] = int(self.level_count.get())
        except:
            self.params["level_count"] = 100
        
        self.figure.add_subplot(projection="3d")
        self.figure.subplots_adjust(-0.3, 0.1, 0.9, 0.9)
        axes = self.figure.axes[0]

        try:
            cmap = plt.colormaps[self.cmap_cb.get()]
        except:
            cmap = ListedColormap(["#FFFFFF"])

        if self.params["x_min"] == None:
            self.params["x_min"] = x.min()
        if self.params["x_max"] == None:
            self.params["x_max"] = x.max()
        if self.params["y_min"] == None:
            self.params["y_min"] = y.min()
        if self.params["y_max"] == None:
            self.params["y_max"] = y.max()
        if self.params["v_min"] == None:
            self.params["v_min"] = z.min()
        if self.params["v_max"] == None:
            self.params["v_max"] = z.max()

        x = x[x <= self.params["x_max"]]
        z = z[:, :len(x)]
        x = x[x >= self.params["x_min"]]
        z = z[:, -len(x):]
                
        y = y[y <= self.params["y_max"]]
        z = z[:len(y)]
        y = y[y >= self.params["y_min"]]
        z = z[-len(y):]
                        
        axes.set_xlim(self.params["x_min"], self.params["x_max"])
        axes.set_ylim(self.params["y_min"], self.params["y_max"])
        axes.set_zlim(self.params["v_min"], self.params["v_max"])
        axes.set_xlabel("D2 [s]")
        axes.set_ylabel("D1 [min]")

        levels = np.linspace(self.params["v_min"], self.params["v_max"], self.params["level_count"])

        cs = axes.contour(x, y, z, levels, cmap=cmap)
        cbar = self.figure.colorbar(cs, pad=0.1)

        return self.figure


class OverlayPage(ttk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.figure = Figure(figsize=(5, 3.3), dpi=150)
        self.x_array = np.array([0, 1])
        self.y_array = np.array([0, 1])
        self.z_array = np.array([[0, 0.5], [0.5, 1]])
        self.params = {}

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.param_frame = ttk.LabelFrame(self, text="Graph Settings")

        ttk.Label(self.param_frame, text="D2 min:", width=8, anchor="e").grid(column=0, row=0, sticky="e", pady=(10, 0))
        self.x_min = ttk.Entry(self.param_frame, width=15)
        self.x_min.grid(column=1, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="D1 min:", width=8, anchor="e").grid(column=2, row=0, sticky="e", pady=(10, 0))
        self.y_min = ttk.Entry(self.param_frame, width=15)
        self.y_min.grid(column=3, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="Val min:", width=8, anchor="e").grid(column=4, row=0, sticky="e", pady=(10, 0))
        self.v_min = ttk.Entry(self.param_frame, width=15)
        self.v_min.grid(column=5, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        
        ttk.Label(self.param_frame, text="D2 max:", width=8, anchor="e").grid(column=0, row=1, sticky="e", pady=(10, 10))
        self.x_max = ttk.Entry(self.param_frame, width=15)
        self.x_max.grid(column=1, row=1, sticky="w", padx=(0, 10), pady=(10, 10))
        ttk.Label(self.param_frame, text="D1 max:", width=8, anchor="e").grid(column=2, row=1, sticky="e", pady=(10, 10))
        self.y_max = ttk.Entry(self.param_frame, width=15)
        self.y_max.grid(column=3, row=1, sticky="w", padx=(0, 10), pady=(10, 10))
        ttk.Label(self.param_frame, text="Val max:", width=8, anchor="e").grid(column=4, row=1, sticky="e", pady=(10, 0))
        self.v_max = ttk.Entry(self.param_frame, width=15)
        self.v_max.grid(column=5, row=1, sticky="w", padx=(0, 10), pady=(10, 10))

        ttk.Button(self.param_frame, text="Apply", width=15, command=self.update_figure).grid(column=7, row=0, sticky="w", padx=30, pady=(10, 10))
        ttk.Button(self.param_frame, text="Reset", width=15, command=self.reset_params).grid(column=7, row=1, sticky="w", padx=30, pady=(10, 10))

        self.update_figure()

        self.canvas.get_tk_widget().pack(side="top", fill="none", expand=True)
        self.param_frame.pack(side="bottom", fill="none", expand=True)


    def set_data(self, x, y, z):
        self.x_array = x
        self.y_array = y
        self.z_array = z
    

    def update_figure(self):
        self.figure.clf()
        self.figure = self.draw_axes(self.x_array, self.y_array, self.z_array)
        self.canvas.draw()

    def reset_params(self):
        self.x_min.delete(0, "end")
        self.x_max.delete(0, "end")
        self.y_min.delete(0, "end")
        self.y_max.delete(0, "end")
        self.update_figure()

    def draw_axes(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
    ) -> Figure:
        self.params["x_min"] = self.x_min.get()
        self.params["x_max"] = self.x_max.get()
        self.params["y_min"] = self.y_min.get()
        self.params["y_max"] = self.y_max.get()
        self.params["v_min"] = self.v_min.get()
        self.params["v_max"] = self.v_max.get()

        for key in ["x_min", "x_max", "y_min", "y_max", "v_min", "v_max"]:
            try:
                self.params[key] = float(self.params[key])
            except:
                self.params[key] = None
                
        self.figure.add_subplot()
        self.figure.subplots_adjust(0.1, 0.2, 0.85, 0.9)
        axes = self.figure.axes[0]

        
        if self.params["x_min"] == None:
            self.params["x_min"] = x.min()
        if self.params["x_max"] == None:
            self.params["x_max"] = x.max()
        if self.params["y_min"] == None:
            self.params["y_min"] = y.min()
        if self.params["y_max"] == None:
            self.params["y_max"] = y.max()
        if self.params["v_min"] == None:
            self.params["v_min"] = z.min()
        if self.params["v_max"] == None:
            self.params["v_max"] = z.max()

                                
        axes.set_xlim(self.params["x_min"], self.params["x_max"])
        axes.set_ylim(self.params["v_min"], self.params["v_max"])
        axes.set_xlabel("D2 [s]")
        
        for i, line in enumerate(z):
            if y[i] >= self.params["y_min"] and y[i] <= self.params["y_max"]:
                axes.plot(x, line, label=f"{y[i]:.2f} min")
        box = axes.get_position()
        axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        axes.legend(bbox_to_anchor=(1, 1.03), loc='upper left')

        return self.figure


class RawPage(ttk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.figure = Figure(figsize=(5, 3.3), dpi=150)
        self.x_array = np.array([0, 1])
        self.y_array = np.array([0, 1])
        self.params = {}

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.param_frame = ttk.LabelFrame(self, text="Graph Settings")

        ttk.Label(self.param_frame, text="Time min:", width=8, anchor="e").grid(column=0, row=0, sticky="e", pady=(10, 0))
        self.x_min = ttk.Entry(self.param_frame, width=15)
        self.x_min.grid(column=1, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Label(self.param_frame, text="Val min:", width=8, anchor="e").grid(column=2, row=0, sticky="e", pady=(10, 0))
        self.y_min = ttk.Entry(self.param_frame, width=15)
        self.y_min.grid(column=3, row=0, sticky="w", padx=(0, 10), pady=(10, 0))
        
        ttk.Label(self.param_frame, text="Time max:", width=8, anchor="e").grid(column=0, row=1, sticky="e", pady=(10, 10))
        self.x_max = ttk.Entry(self.param_frame, width=15)
        self.x_max.grid(column=1, row=1, sticky="w", padx=(0, 10), pady=(10, 10))
        ttk.Label(self.param_frame, text="Val max:", width=8, anchor="e").grid(column=2, row=1, sticky="e", pady=(10, 10))
        self.y_max = ttk.Entry(self.param_frame, width=15)
        self.y_max.grid(column=3, row=1, sticky="w", padx=(0, 10), pady=(10, 10))

        ttk.Button(self.param_frame, text="Apply", width=15, command=self.update_figure).grid(column=7, row=0, sticky="w", padx=30, pady=(10, 0))
        ttk.Button(self.param_frame, text="Reset", width=15, command=self.reset_params).grid(column=7, row=1, sticky="w", padx=30, pady=(10, 0))

        self.update_figure()

        self.canvas.get_tk_widget().pack(side="top", fill="none", expand=True)
        self.param_frame.pack(side="bottom", fill="none", expand=True)


    def set_data(self, x, y):
        self.x_array = x
        self.y_array = y
    

    def update_figure(self):
        self.figure.clf()
        self.figure = self.draw_axes(self.x_array, self.y_array)
        self.canvas.draw()

    def reset_params(self):
        self.x_min.delete(0, "end")
        self.x_max.delete(0, "end")
        self.y_min.delete(0, "end")
        self.y_max.delete(0, "end")
        self.update_figure()

    def draw_axes(
        self,
        x: np.ndarray,
        y: np.ndarray,
    ) -> Figure:
        self.params["x_min"] = self.x_min.get()
        self.params["x_max"] = self.x_max.get()
        self.params["y_min"] = self.y_min.get()
        self.params["y_max"] = self.y_max.get()

        for key in ["x_min", "x_max", "y_min", "y_max"]:
            try:
                self.params[key] = float(self.params[key])
            except:
                self.params[key] = None
                
        self.figure.add_subplot()
        self.figure.subplots_adjust(0.1, 0.2, 0.9, 0.9)
        axes = self.figure.axes[0]

        
        if self.params["x_min"] == None:
            self.params["x_min"] = x.min()
        if self.params["x_max"] == None:
            self.params["x_max"] = x.max()
        if self.params["y_min"] == None:
            self.params["y_min"] = y.min()
        if self.params["y_max"] == None:
            self.params["y_max"] = y.max()

        axes.set_xlim(self.params["x_min"], self.params["x_max"])
        axes.set_ylim(self.params["y_min"], self.params["y_max"])
        axes.set_xlabel("Time [min]")

        axes.plot(x, y)

        return self.figure


class ContourGraph(Figure):

    def __init__(
        self,
        x:np.ndarray,
        y:np.ndarray,
        z:np.ndarray,
        limits_x: tuple[float, float] | None = None,
        limits_y: tuple[float, float] | None = None,
        limits_z: tuple[float, float] | None = None,
    ):
        Figure.__init__(self)
        self.add_subplot(111)
        axes = self.axes[0]
        
        cmap = plt.colormaps["jet"].with_extremes(under="white", over="magenta")
            
        if limits_x != None:
            limits_x = axes.set_xlim(limits_x)
        if limits_y != None:
            limits_y = axes.set_ylim(limits_y)
        
        if limits_z == None:
            limits_z = (z.min(), z.max())
        levels = np.linspace(limits_z[0], limits_z[1], 100)
        
        self.cs = axes.contourf(x, y, z, levels, cmap=cmap, extend="both")
        
        self.cbar = self.colorbar(self.cs)
        
class XYZGraph(Figure):

    def __init__(
        self,
        x:np.ndarray,
        y:np.ndarray,
        z:np.ndarray,
        limits_x: tuple[float, float] | None = None,
        limits_y: tuple[float, float] | None = None,
        limits_z: tuple[float, float] | None = None,
    ):
        Figure.__init__(self)
        self.add_subplot(111, projection="3d")
        axes = self.axes[0]
        
        cmap = plt.colormaps["jet"].with_extremes(under="white", over="magenta")
        
        if limits_x != None:
            limits_x = axes.set_xlim(limits_x)
        if limits_y != None:
            limits_y = axes.set_ylim(limits_y)
        
        if limits_z == None:
            limits_z = (z.min(), z.max())
        
        levels = np.linspace(limits_z[0], limits_z[1], 100)
        self.cs = axes.contour(x, y, z, levels, cmap=cmap, extend="both")
        box = axes.get_position()
        self.cbar = self.colorbar(self.cs, pad=0.1)
        
class OverlayGraph(Figure):

    def __init__(self, x, y, z):
        Figure.__init__(self)
        self.add_subplot(111)
        axes = self.axes[0]
        
        for i, line in enumerate(z):
            axes.plot(x, line, label=f"{y[i]:.2f} min")
        box = axes.get_position()
        axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        axes.legend(bbox_to_anchor=(1, 1.03), loc='upper left')
        
class RawGraph(Figure):

    def __init__(self, x, y):
        Figure.__init__(self, figsize=(5, 5), dpi=100)
        self.add_subplot(111)
        axes = self.axes[0]
        axes.plot(x, y)
