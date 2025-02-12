#!/usr/bin/env python3

import logging

import numpy as np
import pandas as pd

# Use root logger
logger = logging.getLogger(__name__)

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
    values: np.ndarray, ax_D1: np.ndarray, ax_D2: np.ndarray
) -> np.ndarray:
    logging.info(f"Reshaping values into 2D matrix...")
    matrix = np.array(values[: len(ax_D2)])
    
        
    # SABINE RESHAPING ALGORITHM
    idx_start = 1
    frequency = 60 / ax_D2[1]
    sampling_time = ax_D1[1]
    
    for n in range(len(ax_D1) - 1):
        
        array_start = int(n * sampling_time * frequency) + idx_start
        array_end = array_start + len(ax_D2)
        
        array = values[array_start:array_end]
        matrix = np.vstack((matrix, array))
        

    # NAIVE RESHAPING ALGORITHM
    # for n in range(1, len(ax_D1)):
        
    #     array_start = n * len(ax_D2)
    #     array_end = array_start + len(ax_D2)

    #     array = values[array_start:array_end]
    #     matrix = np.vstack((matrix, array))

    logging.info(f"Values reshaped into {matrix.shape}.")
    return matrix
