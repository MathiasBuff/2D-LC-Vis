#!/usr/bin/env python3

import logging
from tkinter import ttk

import numpy as np

from visualisation.base_page import BaseVisualizationPage

# Use root logger
logger = logging.getLogger(__name__)


class RawPage(BaseVisualizationPage):

    def __init__(self, master):     
        super().__init__(master)
                
        self.create_parameters()
        
        self.data = {
            "x": np.array([0, 1]),
            "y": np.array([0, 1]),
        }
        self.update_figure()
        
    def create_parameters(self):
        
        zoom_frame = ttk.Labelframe(self.param_frame, text="Zoom")
        
        d1_frame = ttk.Frame(zoom_frame, padding=(10, 0))
        intensity_frame = ttk.Frame(zoom_frame, padding=(10, 0))
        
        zoom_frame.grid(column=0, row=0, sticky="nsew", padx=5)
        
        d1_frame.grid(column=0, row=0, sticky="nsew", pady=5)
        intensity_frame.grid(column=1, row=0, sticky="nsew", pady=5)
        
                
        ttk.Label(d1_frame, text="Time range [min]", width=15, anchor="w").grid(
            column=0, row=0, columnspan=3, sticky="new"
        )
        self.x_min = ttk.Entry(d1_frame, width=7)
        self.x_min.grid(column=0, row=1)
        ttk.Label(d1_frame, text="-", width=2, anchor="center").grid(
            column=1, row=1
        )
        self.x_max = ttk.Entry(d1_frame, width=7)
        self.x_max.grid(column=2, row=1)
                
        
        ttk.Label(intensity_frame, text="Intensity range", width=15, anchor="w").grid(
            column=0, row=0, columnspan=3, sticky="new"
        )
        self.y_min = ttk.Entry(intensity_frame, width=7)
        self.y_min.grid(column=0, row=1)
        ttk.Label(intensity_frame, text="-", width=2, anchor="center").grid(
            column=1, row=1
        )
        self.y_max = ttk.Entry(intensity_frame, width=7)
        self.y_max.grid(column=2, row=1)
                
        return super().create_parameters()

    def read_parameters(self):
        
        try:
           self.parameters["x_max"] = self.try_float(self.x_max.get())
           self.parameters["x_min"] = self.try_float(self.x_min.get())
           self.parameters["y_min"] = self.try_float(self.y_min.get())
           self.parameters["y_max"] = self.try_float(self.y_max.get())
                      
           return super().read_parameters()
        except ValueError as e:
            logger.error(f"Invalid input : {e}")
        return

    def draw_axes(self):
        
        self.figure.add_subplot()
        self.figure.subplots_adjust(0.1, 0.2, 0.9, 0.9)
        axes = self.figure.axes[0]

        if self.parameters["x_min"] == None:
            self.parameters["x_min"] = self.data["x"].min()
        if self.parameters["x_max"] == None:
            self.parameters["x_max"] = self.data["x"].max()
        if self.parameters["y_min"] == None:
            self.parameters["y_min"] = self.data["y"].min()
        if self.parameters["y_max"] == None:
            self.parameters["y_max"] = self.data["y"].max()

        axes.set_xlim(self.parameters["x_min"], self.parameters["x_max"])
        axes.set_ylim(self.parameters["y_min"], self.parameters["y_max"])
        axes.set_xlabel("Time [min]")
        axes.set_ylabel("Intensity")

        axes.plot(self.data["x"], self.data["y"])

        return super().draw_axes()
