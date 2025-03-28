#!/usr/bin/env python3

from abc import abstractmethod, ABC

import logging
import tkinter as tk
from tkinter import ttk

from matplotlib import colormaps
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from file_io import ask_save_parameters

CMAP_LIST = list(colormaps)
CMAP_DEFAULT = "jet"

# Use root logger
logger = logging.getLogger(__name__)


class BaseVisualizationPage(ttk.Frame, ABC):
    """
    Base class for visualization pages using Matplotlib in a Tkinter frame.
    This class centralizes common layout, figure setup, parameter input handling, and update mechanisms.
    It is designed to be inherited by specific visualization pages, which must implement the draw_axes() method.
    
    Attributes:
        figure (Figure): Matplotlib figure for the visualization.
        canvas (FigureCanvasTkAgg): Canvas to display the figure in Tkinter.
        param_frame (ttk.Frame): Frame for parameter inputs and controls.
        data (dict): Dictionary of input data that will be drawn on the figure.
        parameters (dict): Dictionary of parameter variables.
    """
    
    DEFAULT_PARAMETERS = {}
    
    def __init__(self, master=None):
        super().__init__(master, padding=(10, 0))
        
        self.data = {}
        self.parameters = {}
        
        self.body()

    def body(self) -> None:
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.param_frame = ttk.LabelFrame(self, text="Graph Settings", padding=(10, 0))
        buttons_frame = ttk.Frame(self)
                
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.param_frame.pack(side="top", fill="both", expand=False, ipady=5)
        buttons_frame.pack(side="top", fill="x", expand=False, ipady=10)
        
        ttk.Button(buttons_frame, text="Apply", command=self.update_figure).pack(
            side="left", fill="none", expand=False
        )
        ttk.Button(buttons_frame, text="Reset", command=self.reset_parameters).pack(
            side="left", fill="none", expand=False, padx=10
        )        
        ttk.Button(buttons_frame, text="Save Figure", command=self.save_figure).pack(
            side="right", fill="none", expand=False
        )

    @abstractmethod
    def create_parameters(self) -> None:
        pass

    @abstractmethod
    def draw_axes(self) -> None:
        pass

    @abstractmethod
    def read_parameters(self) -> None:
        pass

    def reset_parameters(self) -> None:
        entries = []

        # Recursively find all entry fields within the widget
        def find_entries(w):
            for child in w.winfo_children():
                if isinstance(child, (tk.Entry, ttk.Entry)):
                    entries.append((child))
                else:
                    find_entries(child)

        find_entries(self)

        # Delete all text in entry fields
        for entry in entries:
            entry.delete(0, "end")
        
        # Reset parameters to an empty dict
        self.parameters = self.DEFAULT_PARAMETERS.copy()        
        self.update_figure()

    def update_figure(self) -> None:
        """
        Clears the figure, redraws the axes, and refreshes the canvas.
        """
        self.read_parameters()
        self.figure.clf()
        self.draw_axes()
        self.canvas.draw()

    def save_figure(self) -> None:
        parameters = ask_save_parameters()
        if parameters["path"] == "":
            return

        fig = self.figure
        axes = fig.axes[0]
        current_size = fig.get_size_inches()
        
        cm_to_inches = 1 / 2.54
        
        dpi = parameters["dpi"]
        width = parameters["size"][0] * cm_to_inches
        height = parameters["size"][1] * cm_to_inches
        
        fig.set_size_inches(width, height)
        axes.set_xlabel(axes.get_xlabel())
        axes.set_ylabel(axes.get_ylabel())

        fig.savefig(parameters["path"], dpi=dpi)
        self.figure.set_size_inches(current_size)
        
    
    def try_float(self, input:str) -> float | None:
        if input == "":
            return None
        else:
            try:
                return float(input)
            except ValueError as e:
                raise e
