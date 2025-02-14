#!/usr/bin/env python3

import logging
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
from tkinter import ttk

from visualisation.contour_page import ContourPage
from visualisation.xyz_page import XYZPage
from visualisation.overlay_page import OverlayPage
from visualisation.raw_page import RawPage


# Log to root logger
logger = logging.getLogger()


class TextHandler(logging.Handler):
    """
    Custom logging handler for redirecting log messages to a Tkinter Text or ScrolledText widget.

    This allows the application's log messages to be displayed in real-time in the GUI.

    Attributes:
        text (tkinter.Text or ScrolledText): The text widget to which log messages are appended.
    """

    def __init__(self, text: tk.Text):
        """
        Initializes the TextHandler.

        Args:
            text (tk.Text or ScrolledText): The text widget for displaying log messages.
        """

        logging.Handler.__init__(self)
        self.text = text

    def emit(self, record: logging.LogRecord) -> None:
        """
        Formats and appends a log message to the Text widget.

        Args:
            record (LogRecord): The logging record containing the message.
        """

        msg = self.format(record)

        def append():
            self.text.configure(state="normal")
            self.text.insert(tk.END, msg + "\n")
            self.text.configure(state="disabled")
            # Autoscroll to the bottom
            self.text.yview(tk.END)

        # Schedule the append action on the main thread to avoid threading issues
        self.text.after(0, append)


class MainView(tk.Toplevel):
    """
    MainView is responsible for constructing and managing the GUI layout of the 2D-LC Chromatogram Visualization app.

    It handles:
    - Window setup and layout configuration
    - Creation of input fields, buttons, and output display tabs
    - Integration of custom logging to a Tkinter ScrolledText widget
    """

    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    PADDINGS = {"padx": 10, "pady": 10}
    LOGGING_LEVEL = logging.INFO

    def __init__(self, master: tk.Tk):
        """
        Initializes the MainView window.

        Args:
            master (tk.Tk): The root Tkinter window instance.
        """

        super().__init__(master)

        self.master = master
        master.withdraw()

        self.data = None

        # Build the window layout and initialize components
        self.body()

        logger.info("2D-LC Visualizer version 0.2.0")
        logger.info("-" * 42)

        # Bind exit events for closing the application
        self.bind("<Control-q>", self.on_exit)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def body(self) -> None:
        """
        Constructs the main window layout by calling individual setup methods.
        """

        self.setup_window()
        self.setup_general_layout()
        self.populate_calc_frame()
        self.create_console()
        self.create_output_tabs()
        # base = ContourPage(self.output_note)
        # base.pack(expand=True, fill="both")
        # self.output_note.add(base, text="Contour Subclass")
        

    def setup_window(self) -> None:
        """
        Configures the main window's properties, including title, geometry, and initial position.

        Details:
            - It is centered on the user's screen based on the screen's width and height.
            - The window size is defined by class constants `WINDOW_WIDTH` and `WINDOW_HEIGHT`.
            - Uncommenting the `resizable(False, False)` line disables window resizing.

        Attributes:
            WINDOW_WIDTH (int): Width of the main window in pixels (default: 1280).
            WINDOW_HEIGHT (int): Height of the main window in pixels (default: 720).
        """

        self.title("2D-LC Chromatogram Visualization")

        # Calculate and set the window's position to center it on the screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (self.WINDOW_WIDTH / 2))
        y_coordinate = int((screen_height / 2) - (self.WINDOW_HEIGHT / 2))
        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_coordinate}+{y_coordinate}"
        )
        # self.resizable(False, False)  # Uncomment to disable resizing

    def setup_general_layout(self) -> None:
        """
        Creates and arranges the main frames and navigation layout of the application.

        This method initializes and places the following components:
            - Load Button: For loading Excel files.
            - Calculation Frame: For calculation settings and input fields.
            - Output Notebook: For displaying visualization tabs.
            - Console Frame: For displaying log output.
            - Vertical Separator: For visual separation of input and output areas.

        Details:
            - Layout configuration is stored in a list and applied using `place_widgets()`.
            - Grid geometry manager is used for consistent alignment.
            - Row and column weights are set to allow responsive resizing.

        Attributes:
            load_btn (ttk.Button): Button for loading Excel files.
            calc_frame (ttk.Labelframe): Frame for calculation inputs and controls.
            output_note (ttk.Notebook): Notebook container for visualization tabs.
            console_frame (ttk.Labelframe): Frame for displaying log output.
        """

        # Initialize main navigation components
        self.load_btn = ttk.Button(self, text="Load Excel File")

        self.calc_frame = ttk.Labelframe(self, text="Calculation Conditions")
        self.output_note = ttk.Notebook(self)
        self.console_frame = ttk.Labelframe(self, text="Log output")

        # Layout configuration for navigation components
        layout_config = [
            {
                "widget": self.load_btn,
                "grid": {
                    "row": 0,
                    "column": 0,
                    "sticky": "nsew",
                },
            },
            {
                "widget": self.calc_frame,
                "grid": {
                    "row": 1,
                    "column": 0,
                    "sticky": "new",
                },
            },
            {
                "widget": self.output_note,
                "grid": {
                    "row": 0,
                    "column": 2,
                    "rowspan": 3,
                    "sticky": "nsew",
                },
            },
            {
                "widget": self.console_frame,
                "grid": {
                    "row": 2,
                    "column": 0,
                    "sticky": "nsew",
                },
            },
            {
                "widget": ttk.Separator(self, orient="vertical"),
                "grid": {
                    "row": 0,
                    "column": 1,
                    "rowspan": 3,
                    "sticky": "ns",
                },
            },
        ]

        # Place the widgets using the place_widgets() utility method
        self.place_widgets(layout_config)

        # Configure row and column weights for responsive resizing
        row_weights = [0, 0, 1]
        column_weights = [0, 0, 1]

        for n, rw in enumerate(row_weights):
            self.rowconfigure(n, weight=rw)

        for n, cw in enumerate(column_weights):
            self.columnconfigure(n, weight=cw)

    def populate_calc_frame(self) -> None:
        """
        Populates the Calculation Conditions frame with input fields and controls for data processing.

        This method adds the following components:
            - Sampling Time Entry: Text field for inputting the sampling time.
            - Blank Subtraction Checkbox: Checkbox for enabling blank subtraction.
            - Blank Time Entry: Text field for specifying the blank time to subtract.
            - Process Button: Button to initiate data processing.

        Details:
            - Labels are aligned to the left for better readability.
            - Input fields are organized within `st_frame` and `blank_frame` containers.
            - Layout configuration is stored in a list and applied using `place_widgets()`.
            - Row and column weights are set to allow responsive resizing within frames.

        Attributes:
            st_entry (ttk.Entry): Entry field for sampling time in minutes.
            blk_checkbox (ttk.Checkbutton): Checkbox for enabling blank subtraction.
            blk_entry (ttk.Entry): Entry field for blank subtraction time.
            process_btn (ttk.Button): Button to start data processing.
        """
        # Sampling Time Frame
        st_frame = ttk.Frame(self.calc_frame)
        self.st_entry = ttk.Entry(st_frame)

        # Blank Subtraction Frame
        blank_frame = ttk.Frame(self.calc_frame)
        self.blk_checkbox = ttk.Checkbutton(blank_frame)
        self.blk_checkbox.state(["!alternate"])
        self.blk_entry = ttk.Entry(blank_frame)
        self.blk_entry.insert(tk.END, "0")

        # Process Data Button
        self.process_btn = ttk.Button(self.calc_frame, text="Process Data")

        # Layout configuration for input fields and controls
        layout_config = [
            {
                "widget": st_frame,
                "pack": {
                    "side": "top",
                    "expand": False,
                    "fill": "both",
                },
            },
            {
                "widget": ttk.Label(
                    st_frame, text="Sampling time (min) :", anchor="w", width=20
                ),
                "pack": {
                    "side": "left",
                    "expand": False,
                    "fill": "x",
                },
            },
            {
                "widget": self.st_entry,
                "pack": {
                    "side": "right",
                    "expand": True,
                    "fill": "none",
                },
            },
            {
                "widget": blank_frame,
                "pack": {
                    "side": "top",
                    "expand": False,
                    "fill": "both",
                },
            },
            {
                "widget": self.blk_checkbox,
                "grid": {
                    "row": 0,
                    "column": 0,
                },
            },
            {
                "widget": ttk.Label(blank_frame, text="Blank Substraction", anchor="w"),
                "grid": {
                    "row": 0,
                    "column": 1,
                    "sticky": "nsew",
                },
            },
            {
                "widget": self.blk_entry,
                "grid": {
                    "row": 1,
                    "column": 1,
                    "sticky": "nsw",
                },
            },
            {
                "widget": self.process_btn,
                "pack": {
                    "side": "top",
                    "expand": False,
                    "fill": "both",
                },
            },
        ]

        # Place the widgets using the place_widgets() utility method
        self.place_widgets(layout_config)
        blank_frame.columnconfigure(1, weight=1)

    def create_console(self) -> None:
        """
        Creates a ScrolledText widget for displaying log output and attaches it to the console frame.

        This function also sets up a custom TextHandler to redirect log messages to the ScrolledText widget.

        Details:
            - The console is initialized as a disabled text widget to prevent user input.
            - It uses the Calibri font for better readability.
            - The TextHandler schedules log updates using the Tkinter event loop, ensuring thread safety.

        Attributes:
            console (ScrolledText): A scrollable text area for displaying log messages.
        """
        console = ScrolledText.ScrolledText(
            self.console_frame, width=15, height=20, state="disabled"
        )
        console.configure(font="Calibri")
        console.pack(side="bottom", expand=True, fill="both", **self.PADDINGS)

        # Create and add the custom TextHandler to the logger
        text_handler = TextHandler(console)
        logger.addHandler(text_handler)
        text_handler.setLevel(self.LOGGING_LEVEL)

    def create_output_tabs(self) -> None:
        """
        Creates output tabs for displaying various visualizations using Notebook tabs.

        This function initializes the following visualization pages:
            - 2D Contour Plot (ContourPage)
            - 3D Contour Plot (XYZPage)
            - Overlay Plot (OverlayPage)
            - Raw Data Plot (RawPage)

        Details:
            - Each page is packed with `expand=True` and `fill="both"` to ensure responsive resizing.
            - The pages are then added as tabs to the output notebook (`self.output_note`).
            - Layout configuration is stored in a list and applied using the `place_widgets()` method.

        Attributes:
            contour_page (ContourPage): Displays 2D contour plots.
            xyz_page (XYZPage): Displays 3D contour plots.
            overlay_page (OverlayPage): Displays overlay plots.
            raw_page (RawPage): Displays raw chromatogram data.
        """

        # Initialize visualization pages
        self.contour_page = ContourPage(self.output_note)
        self.xyz_page = XYZPage(self.output_note)
        self.overlay_page = OverlayPage(self.output_note)
        self.raw_page = RawPage(self.output_note)

        # Layout configuration for each page
        layout_config = [
            {
                "widget": self.contour_page,
                "pack": {
                    "expand": True,
                    "fill": "both",
                },
            },
            {
                "widget": self.xyz_page,
                "pack": {
                    "expand": True,
                    "fill": "both",
                },
            },
            {
                "widget": self.overlay_page,
                "pack": {
                    "expand": True,
                    "fill": "both",
                },
            },
            {
                "widget": self.raw_page,
                "pack": {
                    "expand": True,
                    "fill": "both",
                },
            },
        ]

        # Place the widgets using the place_widgets() utility method
        self.place_widgets(layout_config)

        # Add each page as a tab in the output notebook
        self.output_note.add(self.contour_page, text="2D Contour")
        self.output_note.add(self.xyz_page, text="3D Contour")
        self.output_note.add(self.overlay_page, text="Overlay")
        self.output_note.add(self.raw_page, text="Raw")

    def on_exit(self, event=None) -> None:
        """
        Handles the application exit event, ensuring proper cleanup.
        """

        logger.debug("Exiting application.\n")
        self.destroy()
        self.master.destroy()

    def place_widgets(self, layout_config: list[dict]) -> None:
        """
        Places widgets on the layout using grid or pack based on configuration.

        Args:
            layout_config (list[dict]): List of widget and layout options.
        """

        for config in layout_config:
            widget = config["widget"]

            # Apply layout based on specified method (grid or pack)
            if "grid" in config:
                widget.grid(**config["grid"], **self.PADDINGS)
            elif "pack" in config:
                widget.pack(**config["pack"], **self.PADDINGS)
