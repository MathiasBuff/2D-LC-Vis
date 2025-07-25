#!/usr/bin/env python3

import logging
import threading
import tkinter as tk
from tkinter import ttk

from file_io import ask_file
from model import DataManager
from view import MainView

# Log to root logger
logger = logging.getLogger()


class AppController:
    """
    AppController is responsible for managing interactions between the Model and View in the MVC pattern.

    It handles:
        - User interactions (e.g., button clicks) and triggering corresponding actions.
        - Data flow between the Model (DataManager) and the View (MainView).
        - Managing asynchronous operations using threading for data processing and visualization updates.

    Attributes:
        model (DataManager): The model handling data loading and processing.
        view (MainView): The view responsible for displaying the GUI.
    """

    def __init__(self, root: tk.Tk):
        """
        Initializes the AppController, setting up the Model and View components.

        This constructor also binds event handlers for:
            - Load Button: Triggers the Excel file loading process.
            - Process Button: Initiates data processing and visualization updates.

        Args:
            root (tk.Tk): The root Tkinter window instance.
        """
        self.model = DataManager()
        self.view = MainView(root)

        # Bring to front
        self.view.lift()
        self.view.attributes("-topmost", True)
        self.view.after(500, lambda: self.view.attributes("-topmost", False))

        # Bind event handlers to the View's buttons
        self.view.load_btn.config(command=self.on_load_excel_button_click)
        self.view.process_btn.config(command=self.on_process_button_click)

    def on_load_excel_button_click(self) -> None:
        """
        Handles the Load Excel button click event to prompt the user for an Excel file.

        This method:
            - Prompts the user to select an Excel file using the ask_file() dialog.
            - Starts a separate thread to load the selected Excel file using the Model's load() method.
            - Freezes buttons temporarily to prevent double-clicks.

        Threading Details:
            - run_in_thread() is used to maintain UI responsiveness during file loading.
            - freeze_buttons() temporarily disables all buttons during the loading process.

        Error Handling:
            - If the ask_file() dialog is canceled, no further action is taken.
        """
        logger.info("\nAsking user for Excel file...")

        # Prompt the user for file parameters
        file_parameters = ask_file()

        logger.debug(f"ask_file dialog exited with {file_parameters}")

        # Start file loading in a separate thread to keep UI responsive
        run_in_thread(
            self.model.load,
            file_parameters["path"],
            file_parameters["sheet"],
            file_parameters["headers"],
        )

        # Temporarily freeze buttons to prevent multiple clicks
        run_in_thread(
            freeze_buttons,
            self.view,
        )

    def on_process_button_click(self) -> None:
        """
        Handles the Process Data button click event to initiate data processing.

        This method:
            - Retrieves user input for sampling time and blank time (if applicable).
            - Validates the inputs to ensure they are numeric.
            - Starts a separate thread for data processing using the Model's process() method.
            - Freezes buttons temporarily to prevent double-clicks.

        Threading Details:
            - run_in_thread() is used to keep the UI responsive during data processing.
            - freeze_buttons() temporarily disables all buttons during processing.

        Error Handling:
            - If input validation fails, an error is logged and processing is aborted.
        """

        logger.info("Processing data...")

        # Get and validate sampling time input
        try:
            sampling_time = float(self.view.st_entry.get())
        except ValueError:
            logger.error("Invalid sampling time input.")
            return

        # Get and validate blank time input (if checkbox is selected)
        if self.view.blk_checkbox.instate(["selected"]):
            try:
                blank_time = float(self.view.blk_entry.get())
            except ValueError:
                logger.error("Invalid blank time input.")
                return
        else:
            blank_time = None

        # Start data processing in a separate thread to keep UI responsive
        t = run_in_thread(
            self.model.process,
            sampling_time,
            blank_time,
            self.draw_figures,
        )

        # Temporarily freeze buttons to prevent multiple clicks
        run_in_thread(
            freeze_buttons,
            self.view,
        )
    
    def print_matrix(self) -> None:
        self.view.matrix_text.delete(1.0, tk.END)
        try:
            for i in self.model.mesh:
                for j in i:
                    try:
                        self.view.matrix_text.insert(tk.END, "{:.3f}\t".format(float(j)))
                    except ValueError:
                        self.view.matrix_text.insert(tk.END, f"{j}\t")
                self.view.matrix_text.insert(tk.END, "\n")
        except AttributeError:
            logger.error("No data loaded to print matrix.")
            self.view.matrix_text.insert(tk.END, "No data loaded.")

    def draw_figures(self) -> None:
        """
        Initiates the drawing of all visualization figures once data processing is complete.

        This method:
            - Calls draw_figure() for each visualization tab in the output notebook:
                - 2D Contour Plot
                - 3D Contour Plot
                - Overlay Plot
                - Raw Data Plot
            - Each call is executed in a separate thread to maintain UI responsiveness.

        Threading Details:
            - run_in_thread() is used to keep the UI responsive during figure updates.

        Logging:
            - Logs the completion status of each figure drawing operation.
        """

        logger.info("\nDrawing figures...")
        
        self.threads = []

        # Draw the 2D Contour Plot
        self.threads.append(run_in_thread(
            draw_figure,
            self.view.contour_page,
            {
                "x": self.model.ax_D2,
                "y": self.model.ax_D1,
                "z": self.model.value_matrix,
            },
            "Contour",
        ))

        # Draw the 3D Contour Plot
        self.threads.append(run_in_thread(
            draw_figure,
            self.view.xyz_page,
            {
                "x": self.model.ax_D2,
                "y": self.model.ax_D1,
                "z": self.model.value_matrix,
            },
            "3D",
        ))

        # Draw the Overlay Plot
        self.threads.append(run_in_thread(
            draw_figure,
            self.view.overlay_page,
            {
                "x": self.model.ax_D2,
                "y": self.model.ax_D1,
                "z": self.model.value_matrix,
            },
            "Overlay",
        ))

        # Draw the Raw Data Plot
        self.threads.append(run_in_thread(
            draw_figure,
            self.view.raw_page,
            {
                "x": self.model.data[:, 0][:len(self.model.value_matrix.copy().reshape(-1))],
                "y": self.model.value_matrix.copy().reshape(-1),
                "marks": self.model.ax_D1,
            },
            "Raw",
        ))

        run_in_thread(
            self.check_drawings_done,
        )

    def check_drawings_done(self):
            if all(not t.is_alive() for t in self.threads):
                logger.info("All figures drawn.")
                # self.print_matrix()
            else:
                self.view.after(500, self.check_drawings_done)

def run_in_thread(target, *args):
    """
    Utility method to run a target function in a separate thread.

    Args:
        target (callable): The function to run in the thread.
        *args: Arguments to pass to the target function.
    """

    t = threading.Thread(target=target, args=args)
    t.start()
    return t


def draw_figure(page, data: dict, name: str = "") -> None:
    """
    General method to update a figure on a given page.

    Args:
        page: The page object containing the figure to update.
        data (dict): Dictionary containing the numeric data that will be represented.
        name (str, optional): Name of the figure to pass to logging. Defaults to empty string.
    """

    page.data = data
    page.update_figure()
    logger.debug(f"{name} figure complete.")


def freeze_buttons(widget: tk.Tk | tk.Toplevel, duration: int = 1) -> None:
    """
    Disables all child buttons of the widget temporarily to prevent accidental double-clicks.

    Args:
        widget (tk.Tk | tk.Toplevel): The parent widget containing buttons to disable.
        duration (int, optional): Duration (in seconds) to disable buttons. Defaults to 1 second.
    """

    buttons = []

    # Recursively find all buttons within the widget
    def find_buttons(w):
        for child in w.winfo_children():
            if isinstance(child, (tk.Button, ttk.Button)):
                buttons.append((child, child["state"]))
            else:
                find_buttons(child)

    find_buttons(widget)

    # Disable all buttons
    for button, _ in buttons:
        button.config(state="disabled")

    # Re-enable buttons after the specified duration
    widget.after(
        duration * 1000,
        lambda: [button.config(state=state) for button, state in buttons],
    )
