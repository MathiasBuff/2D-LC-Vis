#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure


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
