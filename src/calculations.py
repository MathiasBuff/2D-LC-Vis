#!/usr/bin/env python3

import logging
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def main():

    # sampling_time = 0.5078
    # sampling_time = 0.42
    # sampling_time = 0.66
    sampling_time = 0.771
    
    # path = Path("C:\\", "Users", "buff", "Desktop", "tmp", "24-12-17-2D-Data_(peptides et Davy).xlsx")
    # sheet = "Données Sabine"
    
    # path = Path("C:\\", "Users", "buff", "Desktop", "tmp", "250113_mixdT7_5uL 1825.xlsx")
    # sheet = "Test Oligo 3"
    
    path = Path("C:\\", "Users", "buff", "Desktop", "tmp", "ASM 5uL.xlsx")
    sheet = "ASM 5uL"

    # TODO make header optional with checkbox on load
    data = load_data(None, path, sheet, None)

    input_time, input_values = data[:, 0], data[:, 1]

    ax_D1, ax_D2 = construct_axes(input_time, sampling_time)

    value_matrix = construct_matrix(input_values, ax_D1, ax_D2, 0, 0)

    fig = get_figure_contour(ax_D2, ax_D1, value_matrix.transpose(), np.arange(-0.5, 1.7, 0.01))
    # fig.axes[0].set_ylim((0, 100))
    # fig.axes[0].set_xlim((0, 20))
    plt.show()


def load_data(initiator, path, sheet, headers) -> np.ndarray:
    logging.info(f"Loading data on '{sheet}'...")
    if headers:
        h = 0
    else:
        h = None
    if initiator == None:
        return np.array(pd.read_excel(path, sheet, header=h, engine="calamine"))
    else:
        initiator.data = np.array(pd.read_excel(path, sheet, header=h, engine="calamine"))
    logging.info("Data successfully loaded.")


def construct_axes(
    time_data: np.ndarray, sampling_time: float
) -> tuple[np.ndarray, np.ndarray]:
    logging.info("Constructing time vectors...")
    input_time = time_data

    x_start = input_time[0]
    x_end = input_time[-1]
    delta = (x_end - x_start) / (len(input_time) - 1)
    frequency = 1 / (60 * delta)
    logging.info(
        f"Sampling time: {sampling_time:.4f} min  --  Frequency: {frequency:.4f} Hz"
    )

    # reindex time to prevent rounding errors
    input_time = np.arange(start=0, stop=x_end + delta, step=delta)

    time_column_D2 = np.arange(start=0, stop=sampling_time + delta, step=delta)
    time_column_D2 *= 60  # Convert to seconds

    time_column_D1 = np.arange(
        start=0, stop=x_end - (2 * sampling_time), step=sampling_time
    )
    logging.info(
        f"Number of points along D1: {len(time_column_D1)}\n\
Number of points along D2: {len(time_column_D2)}"
    )
    return (time_column_D1, time_column_D2)


def construct_matrix(
    values: np.ndarray, ax_D1: np.ndarray, ax_D2: np.ndarray, shift: float, correction_factor: float
) -> np.ndarray:
    logging.info(f"Reshaping values into 2D matrix...")
    matrix = np.array(values[: len(ax_D2)])
    
    if shift > 0:
        num = np.where(ax_D2 <= shift)[0][-1]
        values = np.concatenate((np.full(num, np.nan), values[:-num]))
    elif shift < 0:
        num = np.where(ax_D2 <= (-shift))[0][-1]
        values = np.concatenate((values[num:], np.full(num, np.nan)))
    
    # SABINE RESHAPING ALGORITHM
    idx_start = 1
    frequency = 60 / ax_D2[1]
    sampling_time = ax_D1[1]
    
    for n in range(len(ax_D1) - 1):
        skew = int(n * correction_factor)
        
        array_start = int(n * sampling_time * frequency) + idx_start - skew
        array_end = array_start + len(ax_D2)
        
        array = values[array_start:array_end]
        matrix = np.vstack((matrix, array))
        
    matrix = matrix.transpose()
        

    # NAIVE RESHAPING ALGORITHM
    # for n in range(1, len(ax_D1)):
    #     skew = int(n * correction_factor)
        
    #     array_start = n * len(ax_D2) - skew
    #     array_end = array_start + len(ax_D2)

    #     array = values[array_start:array_end]
    #     matrix = np.vstack((matrix, array))
    # matrix = matrix.transpose()

    logging.info(f"Values reshaped into {matrix.shape}.")
    return matrix


# TODO: Variables on levels, cmap, and axes
def get_figure_contour(x, y, z, levels):
    figure, axes = plt.subplots(layout="constrained")
    cmap = plt.colormaps["gist_rainbow"].with_extremes(under="white", over="red", bad="black")

    contour_set = axes.contourf(x, y, z, levels, cmap=cmap, extend="both")

    axes.set_xlabel("D2 Time [s]")
    axes.set_ylabel("D1 Time [min]")

    cbar = figure.colorbar(contour_set)
    cbar.ax.set_ylabel("Value")

    return figure


if __name__ == "__main__":
    print(" \n")
    main()
    print()
