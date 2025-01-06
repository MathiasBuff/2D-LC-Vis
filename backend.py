#!/usr/bin/env python3

from ast import TypeVarTuple
import logging
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tkinter.filedialog import askdirectory

logger = logging.getLogger(__name__)

def main():
    # TODO replace constants with user-input variables
    filepath = Path("data", "24-12-17-2D-Data_(peptides et Davy).xlsx")
    sheetname = "Feuil1"
    sampling_time = 0.5078
    
    #TODO make header optional with checkbox on load
    data = np.array(pd.read_excel(filepath, sheetname, header=0))
    input_time, input_values = data[:, 0], data[:, 1]
    
    x_start = input_time[0]
    x_end = input_time[-1]
    delta = (x_end - x_start) / (len(input_time) - 1)
    frequency = 1 / (60 * delta)
    
    # reindex time to prevent rounding errors
    input_time = np.arange(
        start=0,
        stop=x_end + delta,
        step=delta
    )
    
    rows_per_column = round(frequency * sampling_time * 60)
    time_column_D2 = np.arange(
        start=0,
        stop=sampling_time + delta,
        step=delta
    )
    time_column_D2 = time_column_D2[:rows_per_column + 1]
    time_column_D2 *= 60 # Convert to seconds
    
    # initialise the value matrix with first column
    value_matrix = np.array(input_values[:rows_per_column + 1])
    
    end_time_D1 = int(x_end / sampling_time) * sampling_time
    time_column_D1 = np.arange(
        start=0,
        stop=end_time_D1,
        step=sampling_time
    )
    
    # going back 1 index might be bug
    for n in range(1, len(time_column_D1)):
        array_start = n * rows_per_column
        array_end = (n + 1) * rows_per_column + 1
        
        array = input_values[array_start : array_end]
        value_matrix = np.vstack((value_matrix, array))
    
    # value_matrix = np.transpose(value_matrix)
    
    # print(time_column_D1.shape)
    # print(time_column_D2.shape)
    # print(value_matrix.shape)
    
    # plt.contourf(time_column_D2, time_column_D1, value_matrix)
    # plt.show()
    
    fig1, ax2 = plt.subplots(layout='constrained')
    cmap = plt.colormaps["inferno"]\
        .with_extremes(under="black", over="white")
    CS = ax2.contourf(
        time_column_D2,
        time_column_D1,
        value_matrix,
        range(-10, 130, 20),
        cmap=cmap
        )
    
    CS.cmap.set_under()
    CS.cmap.set_over("white")

    # Note that in the following, we explicitly pass in a subset of the contour
    # levels used for the filled contours.  Alternatively, we could pass in
    # additional levels to provide extra resolution, or leave out the *levels*
    # keyword argument to use all of the original levels.

    ax2.set_title("Example Contour Plot")
    ax2.set_xlabel("D2 Time [s]")
    ax2.set_ylabel("D1 Time [min]")

    # Make a colorbar for the ContourSet returned by the contourf call.
    cbar = fig1.colorbar(CS)
    cbar.ax.set_ylabel("Value")
    
    plt.show()

if __name__ == "__main__":
    print(" \n")
    main()
    print()