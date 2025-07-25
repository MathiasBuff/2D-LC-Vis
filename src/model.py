#!/usr/bin/env python3

import logging

import numpy as np
import pandas as pd

# Log to root logger
logger = logging.getLogger()


class DataManager:
    """
    DataManager is responsible for loading, processing, and organizing
    chromatographic data for visualization. It handles:
    - Loading Excel data into a NumPy array.
    - Constructing time axes for D1 and D2 dimensions.
    - Reshaping data into a 2D matrix for contour visualization.
    - Performing blank subtraction, if required.
    """

    def __init__(self):
        pass

    def load(self, path: str, sheet: str, headers) -> np.ndarray:
        """
        Loads data from an Excel file and converts it into a NumPy array.

        Args:
            path (str): Path to the Excel file.
            sheet (str): Name of the Excel sheet to load.
            headers (bool): If True, the first row is used as column headers.

        Raises:
            FileNotFoundError: If the provided file path does not exist.
            ValueError: If the sheet name is not found or data is invalid.
        """

        logger.info(f"Loading data from sheet '{sheet}'...")

        # Set header row index based on user choice
        h = 0 if headers else None

        # Load data as a NumPy array using calamine engine for compatibility
        self.data = np.array(pd.read_excel(path, sheet, header=h, engine="calamine"))

        logger.info("Data successfully loaded.")

    def process(
        self, sampling_time: float, blank_time: float = None, callback: callable = None
    ) -> None:
        """
        Processes the loaded data by constructing time axes, reshaping the data
        into a 2D matrix, and optionally subtracting a blank.

        Args:
            sampling_time (float): The time interval for D2.
            blank_time (float, optional): Time value to subtract as blank. Defaults to None.
            callback (callable, optional): Function to call upon completion.
        """
        try:
            _ = self.data
        except AttributeError:
            logger.error("No data loaded.")
            return

        # Construct time vectors for D1 and D2
        self.ax_D1, self.ax_D2 = self.construct_axes(sampling_time)

        # Reshape the data into a 2D matrix
        self.value_matrix = self.construct_matrix()

        # Perform blank subtraction if blank_time is specified
        if blank_time:
            self.subtract_blank(blank_time)
        
        self.mesh = np.concat((self.ax_D1.reshape((-1, 1)), self.value_matrix), axis=1)
        self.mesh = np.concat((np.concat((np.array([" "]), self.ax_D2), axis=0).reshape((1, -1)), self.mesh), axis=0)

        logger.info("Processing complete.")

        # Trigger callback if provided
        if callback:
            callback()

    def construct_axes(self, sampling_time: float) -> tuple[np.ndarray, np.ndarray]:
        """
        Constructs time vectors for D1 and D2 dimensions based on loaded data and sampling time.

        Args:
            sampling_time (float): The time interval for D2.

        Returns:
            tuple: A tuple containing:
                - time_column_D1 (np.ndarray): Time vector for the first dimension (D1).
                - time_column_D2 (np.ndarray): Time vector for the second dimension (D2).
        """

        logger.info("\nConstructing time vectors...")

        # Calculate time increments and frequency
        x_start, x_end = self.data[:, 0][0], self.data[:, 0][-1]
        delta = (x_end - x_start) / (len(self.data[:, 0]) - 1)
        frequency = 1 / (60 * delta)  # Hz

        logger.info(
            f"Sampling time: {sampling_time:.4f} min\n\
Frequency: {frequency:.4f} Hz"
        )

        # Construct the time vector for D2 (second dimension)
        time_column_D2 = np.arange(start=0, stop=sampling_time + delta, step=delta)
        time_column_D2 *= 60  # Convert to seconds

        # Construct the time vector for D1 (first dimension)
        time_column_D1 = np.arange(
            start=0, stop=x_end - (2 * sampling_time), step=sampling_time
        )

        logger.debug(
            f"Number of points along D1: {len(time_column_D1)}\n\
Number of points along D2: {len(time_column_D2)}"
        )

        return (time_column_D1, time_column_D2)

    def construct_matrix(self) -> np.ndarray:
        """
        Reshapes the loaded data into a 2D matrix for contour visualization.

        Returns:
            np.ndarray: 2D matrix of reshaped data values.
        """

        logger.info(f"Reshaping values into 2D matrix...")

        # Calculate sampling frequency and time step
        frequency = 60 / self.ax_D2[1]
        sampling_time = self.ax_D1[1]

        # Collect cut columns
        cols = []

        # Iterate over D1 time points to extract corresponding D2 segments
        for n in range(len(self.ax_D1)):
            array_start = int(n * sampling_time * frequency)
            array_end = array_start + len(self.ax_D2)
            cols.append(self.data[:, 1][array_start:array_end])

        # Stack columns to form the 2D value matrix
        matrix = np.vstack(cols)

        logger.debug(f"Values reshaped into {matrix.shape}.")

        return matrix

    def subtract_blank(self, blank_time: float) -> None:
        """
        Subtracts a blank value from the data matrix at the specified blank time.

        Args:
            blank_time (float): Time value to subtract as blank.

        Notes:
            - The blank value is taken from the row corresponding to the blank time.
            - The blank is subtracted along the second dimension.
        """

        # Find the index corresponding to the blank time
        blank_line = np.where(self.ax_D1 <= blank_time)[0][-1]

        logger.info(f"Substracting data at {self.ax_D1[blank_line]:.4f} min.")

        # Subtract the blank line from the entire matrix
        self.value_matrix = self.value_matrix - self.value_matrix[blank_line, :]
