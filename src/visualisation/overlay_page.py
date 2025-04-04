#!/usr/bin/env python3

import logging
from tkinter import ttk

import numpy as np

from visualisation.base_page import BaseVisualizationPage, create_tooltip

# Use root logger
logger = logging.getLogger(__name__)


class OverlayPage(BaseVisualizationPage):

    def __init__(self, master):     
        super().__init__(master)
                
        self.create_parameters()
        
        self.data = {
            "x": np.array([0, 1]),
            "y": np.array([0, 1]),
            "z": np.array([[0, 0.5], [0.5, 1]]),
        }
        self.update_figure()
        
    def create_parameters(self):
        
        zoom_frame = ttk.Labelframe(self.param_frame, text="Zoom")
        
        d1_frame = ttk.Frame(zoom_frame, padding=(10, 0))
        d2_frame = ttk.Frame(zoom_frame, padding=(10, 0))
        intensity_frame = ttk.Frame(zoom_frame, padding=(10, 0))
        
        help_ovl_zoom = ttk.Label(zoom_frame, image=self.help_img_tk)
        create_tooltip(help_ovl_zoom, "D1 range: Set the limits of the chromatograms displayed\nD2 range: Set limits of the D2 axis\nIntensity range: Set limits of the Intensity axis")
        
        zoom_frame.grid(column=0, row=0, sticky="nsew", padx=5)
        
        help_ovl_zoom.grid(column=0, row=0, sticky="nw", padx=5)
        d1_frame.grid(column=0, row=1, sticky="nsew", pady=5)
        d2_frame.grid(column=1, row=1, sticky="nsew", pady=5)
        intensity_frame.grid(column=2, row=1, sticky="nsew", pady=5)
        
                
        ttk.Label(d1_frame, text="D1 range [min]", width=15, anchor="w").grid(
            column=0, row=0, columnspan=3, sticky="new"
        )
        self.y_min = ttk.Entry(d1_frame, width=7)
        self.y_min.grid(column=0, row=1)
        ttk.Label(d1_frame, text="-", width=2, anchor="center").grid(
            column=1, row=1
        )
        self.y_max = ttk.Entry(d1_frame, width=7)
        self.y_max.grid(column=2, row=1)
        
        
        ttk.Label(d2_frame, text="D2 range [s]", width=15, anchor="w").grid(
            column=0, row=0, columnspan=3, sticky="new"
        )
        self.x_min = ttk.Entry(d2_frame, width=7)
        self.x_min.grid(column=0, row=1)
        ttk.Label(d2_frame, text="-", width=2, anchor="center").grid(
            column=1, row=1
        )
        self.x_max = ttk.Entry(d2_frame, width=7)
        self.x_max.grid(column=2, row=1)
        
        
        ttk.Label(intensity_frame, text="Intensity range", width=15, anchor="w").grid(
            column=0, row=0, columnspan=3, sticky="new"
        )
        self.z_min = ttk.Entry(intensity_frame, width=7)
        self.z_min.grid(column=0, row=1)
        ttk.Label(intensity_frame, text="-", width=2, anchor="center").grid(
            column=1, row=1
        )
        self.z_max = ttk.Entry(intensity_frame, width=7)
        self.z_max.grid(column=2, row=1)
                
        return super().create_parameters()

    def read_parameters(self):
        
        try:
           self.parameters["x_max"] = self.try_float(self.x_max.get())
           self.parameters["x_min"] = self.try_float(self.x_min.get())
           self.parameters["y_min"] = self.try_float(self.y_min.get())
           self.parameters["y_max"] = self.try_float(self.y_max.get())
           self.parameters["z_min"] = self.try_float(self.z_min.get())
           self.parameters["z_max"] = self.try_float(self.z_max.get())
                      
           return super().read_parameters()
        except ValueError as e:
            logger.error(f"Invalid input : {e}")
        return

    def draw_axes(self):
        
        self.figure.add_subplot()
        self.figure.subplots_adjust(0.1, 0.2, 0.85, 0.9)
        axes = self.figure.axes[0]

        if self.parameters["x_min"] == None:
            self.parameters["x_min"] = self.data["x"].min()
        if self.parameters["x_max"] == None:
            self.parameters["x_max"] = self.data["x"].max()
        if self.parameters["y_min"] == None:
            self.parameters["y_min"] = self.data["y"].min()
        if self.parameters["y_max"] == None:
            self.parameters["y_max"] = self.data["y"].max()
        if self.parameters["z_min"] == None:
            self.parameters["z_min"] = self.data["z"].min()
        if self.parameters["z_max"] == None:
            self.parameters["z_max"] = self.data["z"].max()

        axes.set_xlim(self.parameters["x_min"], self.parameters["x_max"])
        axes.set_ylim(self.parameters["z_min"], self.parameters["z_max"])
        axes.set_xlabel("D2 [s]")
        axes.set_ylabel("Intensity")

        for i, line in enumerate(self.data["z"]):
            if self.data["y"][i] >= self.parameters["y_min"] and self.data["y"][i] <= self.parameters["y_max"]:
                axes.plot(self.data["x"], line, label=f"{self.data["y"][i]:3.1f} min")
        box = axes.get_position()
        axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        axes.legend(bbox_to_anchor=(1, 1.03), loc="upper left", fontsize=8)
        

        return super().draw_axes()