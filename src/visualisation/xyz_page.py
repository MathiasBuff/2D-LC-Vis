#!/usr/bin/env python3

import logging
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np

from visualisation.base_page import BaseVisualizationPage, create_tooltip

# Use root logger
logger = logging.getLogger(__name__)


class XYZPage(BaseVisualizationPage):
    CMAP_LIST = [
        "jet",
        "turbo",
        "viridis",
        "cividis",
        "plasma",
        "inferno",
        "magma",
        "gray",
        "gray_r",
        "hot",
        "hot_r",
        "cool",
        "cool_r",
        "Spectral",
        "coolwarm",
        "nipy_spectral",
        "gnuplot",
        "gnuplot2",
    ]
    DEFAULT_PARAMETERS = {
        "cmap": "jet",
        "lines": 100,
    }

    def __init__(self, master):
        super().__init__(master)
        self.parameters = self.DEFAULT_PARAMETERS.copy()

        self.create_parameters()

        self.data = {
            "x": np.array([0, 1]),
            "y": np.array([0, 1]),
            "z": np.array([[0, 0.5], [0.5, 1]]),
        }
        self.update_figure()

    def create_parameters(self):

        zoom_frame = ttk.Labelframe(self.param_frame, text="Zoom")

        help_xyz_zoom = ttk.Label(zoom_frame, image=self.help_img_tk)
        create_tooltip(
            help_xyz_zoom,
            "D1 range: Set limits of the D1 axis\nD2 range: Set limits of the D2 axis\nIntensity range: Set limits of the Intensity axis",
        )

        d1_frame = ttk.Frame(zoom_frame, padding=(10, 0))
        d2_frame = ttk.Frame(zoom_frame, padding=(10, 0))
        intensity_frame = ttk.Frame(zoom_frame, padding=(10, 0))

        colors_frame = ttk.Labelframe(
            self.param_frame, text="Coloring (Scale)", padding=(10, 0)
        )

        help_xyz_zoom.grid(column=0, row=0, sticky="nw", padx=5)
        d1_frame.grid(column=0, row=1, sticky="nsew", pady=5)
        d2_frame.grid(column=1, row=1, sticky="nsew", pady=5)
        intensity_frame.grid(column=2, row=1, sticky="nsew", pady=5)

        zoom_frame.grid(column=0, row=0, sticky="nsew", padx=5)
        colors_frame.grid(column=1, row=0, sticky="nsew", padx=5)

        ttk.Label(d1_frame, text="D1 range [min]", width=15, anchor="w").grid(
            column=0, row=0, columnspan=3, sticky="new"
        )
        self.y_min = ttk.Entry(d1_frame, width=7)
        self.y_min.grid(column=0, row=1)
        ttk.Label(d1_frame, text="-", width=2, anchor="center").grid(column=1, row=1)
        self.y_max = ttk.Entry(d1_frame, width=7)
        self.y_max.grid(column=2, row=1)

        ttk.Label(d2_frame, text="D2 range [s]", width=15, anchor="w").grid(
            column=0, row=0, columnspan=3, sticky="new"
        )
        self.x_min = ttk.Entry(d2_frame, width=7)
        self.x_min.grid(column=0, row=1)
        ttk.Label(d2_frame, text="-", width=2, anchor="center").grid(column=1, row=1)
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

        help_xyz_colors = ttk.Label(colors_frame, image=self.help_img_tk)
        create_tooltip(
            help_xyz_colors,
            "Colormap: The color scale that will be used to represent Intensity values\nLevels count: Higher count provides better resolution for sharp changes in intensity, but will make image drawing slower. A value of 100 is provided by default.",
        )
        help_xyz_colors.grid(column=0, row=0, sticky="nw")

        ttk.Label(colors_frame, text="Colormap", width=15, anchor="w").grid(
            column=0, row=1, sticky="w"
        )
        self.cmap_cb = ttk.Combobox(
            colors_frame, values=self.CMAP_LIST, state="readonly", width=15
        )
        self.cmap_cb.grid(column=0, row=2, padx=(0, 10))

        ttk.Label(colors_frame, text="", width=8, anchor="w").grid(
            column=1, row=1, columnspan=2, sticky="w"
        )

        tk.Frame(colors_frame, height=25, width=25).grid(column=1, row=2, padx=2)

        tk.Frame(colors_frame, height=25, width=25).grid(column=2, row=2, padx=2)

        ttk.Label(colors_frame, text="Levels count", width=12, anchor="w").grid(
            column=3, row=1, sticky="w", padx=(10, 0)
        )
        self.line_count = ttk.Entry(colors_frame, width=10)
        self.line_count.insert(0, self.parameters["lines"])
        self.line_count.grid(column=3, row=2, padx=(10, 0))

        self.cmap_cb.current(self.CMAP_LIST.index(self.parameters["cmap"]))
        self.cmap_cb.bind("<<ComboboxSelected>>", self.cb_highlight_clear)

        return super().create_parameters()

    def read_parameters(self):

        try:
            self.parameters["x_max"] = self.try_float(self.x_max.get())
            self.parameters["x_min"] = self.try_float(self.x_min.get())
            self.parameters["y_min"] = self.try_float(self.y_min.get())
            self.parameters["y_max"] = self.try_float(self.y_max.get())
            self.parameters["z_min"] = self.try_float(self.z_min.get())
            self.parameters["z_max"] = self.try_float(self.z_max.get())
            self.parameters["cmap"] = self.cmap_cb.get()
            self.parameters["lines"] = self.try_float(self.line_count.get())

            return super().read_parameters()
        except ValueError as e:
            logger.error(f"Invalid input : {e}")
        return

    def reset_parameters(self):
        self.cmap_cb.current(self.CMAP_LIST.index(self.DEFAULT_PARAMETERS["cmap"]))
        return super().reset_parameters()

    def draw_axes(self):

        self.figure.add_subplot(projection="3d")
        self.figure.subplots_adjust(-0.3, 0.1, 0.9, 0.9)
        axes = self.figure.axes[0]

        cmap = plt.colormaps[self.cmap_cb.get()]

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
        if self.parameters["lines"] == None:
            self.parameters["lines"] = 100
            self.line_count.delete(0, "end")
            self.line_count.insert(0, "100")


        # Since we need to crop data in 3d projection, we copy
        # it first to avoid modifying the original data
        data = self.data.copy()

        data["x"] = data["x"][data["x"] <= self.parameters["x_max"]]
        data["z"] = data["z"][:, : len(data["x"])]
        data["x"] = data["x"][data["x"] >= self.parameters["x_min"]]
        data["z"] = data["z"][:, -len(data["x"]) :]

        data["y"] = data["y"][data["y"] <= self.parameters["y_max"]]
        data["z"] = data["z"][: len(data["y"])]
        data["y"] = data["y"][data["y"] >= self.parameters["y_min"]]
        data["z"] = data["z"][-len(data["y"]) :]

        axes.set_xlim(self.parameters["x_min"], self.parameters["x_max"])
        axes.set_ylim(self.parameters["y_min"], self.parameters["y_max"])
        axes.set_zlim(self.parameters["z_min"], self.parameters["z_max"])
        axes.set_xlabel("D2 [s]")
        axes.set_ylabel("D1 [min]")
        axes.set_zlabel("Intensity")

        axes.view_init(elev=25, azim=245)

        levels = np.linspace(
            self.parameters["z_min"],
            self.parameters["z_max"],
            int(self.parameters["lines"]),
        )

        cs = axes.contour(
            data["x"], data["y"], data["z"], levels, cmap=cmap
        )
        cbar = self.figure.colorbar(cs, pad=0.1)
        cbar.set_label("Intensity", labelpad=-5, y=1.05, rotation="horizontal")
        cbar.ax.ticklabel_format(
            axis="y", style="sci", scilimits=(-2, 4), useOffset=False
        )

        labels = [float(f"{tick:0<3.1e}") for tick in cbar.ax.get_yticks()]
        cbar.ax.set_yticks(labels)

        return super().draw_axes()

    def cb_highlight_clear(self, event=None):
        current = self.cmap_cb.get()
        self.cmap_cb.set("")
        self.cmap_cb.set(current)
        self.update_figure()
