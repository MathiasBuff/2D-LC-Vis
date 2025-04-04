#!/usr/bin/env python3

from abc import abstractmethod, ABC

import logging
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from matplotlib import colormaps
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from file_io import ask_save_parameters

CMAP_LIST = list(colormaps)
CMAP_DEFAULT = "jet"

# Use root logger
logger = logging.getLogger(__name__)
help_img = Image.open("utils\\help.png").resize((16,16))

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        delta = (len(text) / 40) * 14
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 20
        y = y + cy + self.widget.winfo_rooty() - delta
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify="left", wraplength=200,
                      background="#ffffe0", relief="solid", borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

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
        self.help_img_tk = ImageTk.PhotoImage(help_img)
        
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
            side="left", fill="none", expand=False, padx=(10,5)
        )
        help_apply = ttk.Label(buttons_frame, image=self.help_img_tk)
        help_apply.pack(side="left")
        create_tooltip(help_apply, "The 'Apply' button must be clicked to redraw the figure using the settings above. The 'Reset' button allows you to restore default parameters.")
        
        ttk.Button(buttons_frame, text="Save Figure", command=self.save_figure).pack(
            side="left", fill="none", expand=False, padx=(50, 5)
        )
        help_save = ttk.Label(buttons_frame, image=self.help_img_tk)
        help_save.pack(side="left")
        create_tooltip(help_save, "This button allows you to export the currently displayed figure as a file. When clicked, a popup will appear to let you choose export parameters such as dimensions and resolution.")

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
