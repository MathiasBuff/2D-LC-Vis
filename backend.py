#!/usr/bin/env python3

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

logger = logging.getLogger(__name__)

def main():
    
    sampling_time = 0.5078
    # sampling_time = 0.42
    
    #TODO make header optional with checkbox on load
    data = load_data()
    
    input_time, input_values = data[:, 0], data[:, 1]
 
    ax_D1, ax_D2 = construct_axes(input_time, sampling_time)

    value_matrix = construct_matrix(input_values, ax_D1, ax_D2)
    
    get_figure_contour(ax_D2, ax_D1, value_matrix, range(5, 100, 1))
    

def load_data(initiator, path, sheet, headers) -> np.ndarray:
    logging.info(f"Loading data on '{sheet}'...")
    if headers:
        h = 0
    else:
        h = None
    initiator.data = np.array(pd.read_excel(path, sheet, header=h, engine="calamine"))
    logging.info("Data successfully loaded.")

def construct_axes(
    time_data: np.ndarray,
    sampling_time: float
) -> tuple[np.ndarray, np.ndarray]:
    
    input_time = time_data
    
    x_start = input_time[0]
    x_end = input_time[-1]
    delta = (x_end - x_start) / (len(input_time) - 1)
    # frequency = 1 / (60 * delta)
        
    # reindex time to prevent rounding errors
    input_time = np.arange(
        start=0,
        stop=x_end + delta,
        step=delta
    )
    
    time_column_D2 = np.arange(
        start=0,
        stop=sampling_time + delta,
        step=delta
    )
    time_column_D2 *= 60 # Convert to seconds
    
    time_column_D1 = np.arange(
        start=0,
        stop=x_end - (2 * sampling_time),
        step=sampling_time
    )
    
    return (time_column_D1, time_column_D2)

# FIXME: need more robustness on the matrix construction
def construct_matrix(
    values: np.ndarray,
    ax_D1: np.ndarray,
    ax_D2: np.ndarray
) -> np.ndarray:
    matrix = np.array(values[:len(ax_D2)])
        
    for n in range(1, len(ax_D1)):
        array_start = n * len(ax_D2) - int(1.2*n)
        array_end = (n + 1) * len(ax_D2) - int(1.2*n)
        
        array = values[array_start : array_end]
        matrix = np.vstack((matrix, array))
    
    return matrix

# TODO: Variables on levels, cmap, and axes
def get_figure_contour(x, y, z, levels):
    figure, axes = plt.subplots(layout='constrained')
    cmap = plt.colormaps["gist_rainbow"]\
        .with_extremes(under="black", over="white")

    contour_set = axes.contourf(
        x,
        y,
        z,
        levels,
        cmap=cmap,
        extend="both"
        )
    
    axes.set_xlabel("D2 Time [s]")
    axes.set_ylabel("D1 Time [min]")

    cbar = figure.colorbar(contour_set)
    cbar.ax.set_ylabel("Value")
    
    return figure

if __name__ == "__main__":
    print(" \n")
    main()
    print()