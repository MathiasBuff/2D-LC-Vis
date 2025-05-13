#!/usr/bin/env python3

import logging
import sys
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import Dialog

import pandas as pd

# Use root logger
logger = logging.getLogger(__name__)


class OpenExcelDialog(Dialog):
    """Class to create a Excel File opening dialog."""

    def __init__(self, parent=None, title: str | None = "Open Excel File"):

        self.manual_text = """Please select a valid Excel file with the "Browse..." button.

The file should contain a sheet with only the data (Time, Intensity) stored in the first two columns, and optionnaly column headers on the first line.
If the columns have headers, please select the "Ignore first line" option.

Then, please select the appropriate sheet and click the "OK" button"""

        super().__init__(parent, title=title)

    def body(self, master):
        """create dialog body.

        return widget that should have initial focus.

        #overridden from simpledialog.Dialog
        """
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = "."

        # self.iconbitmap(default=Path(base_path, "utils", "unige-icon.ico"))

        windowWidth = 360
        windowHeight = 425
        screenWidth = master.winfo_screenwidth()
        screenHeight = master.winfo_screenheight()
        xCoordinate = int((screenWidth / 2) - (windowWidth / 2))
        yCoordinate = int((screenHeight / 2) - (windowHeight / 2))
        self.geometry(f"{windowWidth}x{windowHeight}+{xCoordinate}+{yCoordinate}")
        self.resizable(False, False)

        paddings = {"padx": 5, "pady": 10}

        manual_frame = ttk.Frame(self)
        manual_frame.pack(side="top", expand="yes", fill="both", **paddings)

        manual = ttk.Label(
            manual_frame,
            text=self.manual_text,
            justify="left",
            wraplength=350,
        )
        manual.pack(expand=True, fill="both")

        path_frame = ttk.Frame(self)
        header_frame = ttk.Frame(self)
        worksheet_frame = ttk.Frame(self)

        path_frame.pack(side="top", expand="no", fill="both", **paddings)
        header_frame.pack(side="top", expand="no", fill="both", **paddings)
        worksheet_frame.pack(side="top", expand="no", fill="both", **paddings)

        ttk.Label(path_frame, text="File Path:", anchor="w", width=15).pack(
            side="top", fill="x", expand="no"
        )
        ttk.Label(header_frame, text="Ignore first line", anchor="w", width=15).pack(
            side="right", fill="x", expand="yes"
        )
        ttk.Label(worksheet_frame, text="Worksheet:", anchor="w", width=10).pack(
            side="left", fill="none", expand="no"
        )

        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.pack(side="left", fill="x", expand="yes")
        self.path_entry.state(["disabled"])
        self.path_btn = ttk.Button(
            path_frame, text="Browse...", width=10, command=self.ask_file_path
        )
        self.path_btn.pack(side="right", fill="none", expand="no", padx=5)
        self.head_chck = ttk.Checkbutton(header_frame)
        self.head_chck.state(["!alternate"])
        self.head_chck.pack(side="left", fill="none", expand="no")
        self.sheet_cb = ttk.Combobox(worksheet_frame, state="readonly")
        self.sheet_cb.pack(side="left", fill="x", expand="no", padx=5)

        return self.path_btn

    def buttonbox(self):
        """add standard button box.

        #overridden from simpledialog.Dialog to fit style
        """

        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok)
        w.configure(style="Accent.TButton")
        w.pack(side="left", padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side="left", padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def validate(self):
        result = {
            "path": self.path_entry.get(),
            "headers": self.head_chck.instate(["selected"]),
            "sheet": self.sheet_cb.get(),
        }
        self.result = result
        return True

    def ask_file_path(self):
        path = Path(askopenfilename(filetypes=[("Excel Files", "*.xlsx")]))
        self.path_entry.state(["!disabled"])
        self.path_entry.delete(0)
        self.path_entry.insert(0, path)
        self.path_entry.state(["disabled"])
        self.path = path
        sheets = pd.ExcelFile(path, engine="calamine").sheet_names
        self.sheet_cb.configure({"values": sheets})
        self.sheet_cb.current(0)


class SaveFigureDialog(Dialog):

    def __init__(self, parent=None, title: str | None = "Save Figure Parameters"):

        self.manual_text = "Please select the file path with the 'Browse...' button."
        # """
        # You can accept default values as set below or change them manually.
        # The size values correspond to the image size *on print*.
        # Please note that width lower than 12 cm or height lower than 6 cm may lead to problems with figure boundaries.

        # Once parameters are as wanted, click the "OK" button to save the figure."""

        super().__init__(parent, title=title)

    def body(self, master):
        """create dialog body.

        return widget that should have initial focus.

        #overridden from simpledialog.Dialog
        """
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = "."

        # self.iconbitmap(default=Path(base_path, "utils", "unige-icon.ico"))

        # windowWidth = 360
        # windowHeight = 390
        windowWidth = 360
        windowHeight = 200
        screenWidth = master.winfo_screenwidth()
        screenHeight = master.winfo_screenheight()
        xCoordinate = int((screenWidth / 2) - (windowWidth / 2))
        yCoordinate = int((screenHeight / 2) - (windowHeight / 2))
        self.geometry(f"{windowWidth}x{windowHeight}+{xCoordinate}+{yCoordinate}")
        self.resizable(False, False)

        paddings = {"padx": 10, "pady": 5}

        manual_frame = ttk.Frame(self)
        manual_frame.pack(side="top", expand="yes", fill="both", **paddings)

        manual = ttk.Label(
            manual_frame,
            text=self.manual_text,
            justify="left",
            wraplength=340,
        )
        manual.pack(expand=True, fill="both")

        path_frame = ttk.Frame(master)
        size_frame = ttk.Frame(master)
        dpi_frame = ttk.Frame(master)

        path_frame.grid(column=0, row=0, columnspan=2, sticky="nsew", **paddings)
        size_frame.grid(column=0, row=1, sticky="nsw", **paddings)
        dpi_frame.grid(column=1, row=1, sticky="nse", **paddings)

        ttk.Label(path_frame, text="File Path:", anchor="w", width=15).pack(
            side="top", fill="x", expand="no"
        )

        self.path_entry = ttk.Entry(path_frame, width=28)
        self.path_entry.pack(side="left", fill="x", expand="yes")
        self.path_entry.state(["disabled"])
        self.path_btn = ttk.Button(
            path_frame, text="Browse...", width=10, command=self.ask_file_path
        )
        self.path_btn.pack(side="right", fill="none", expand="no", padx=5)

        # ttk.Label(size_frame, text="Width x Height [cm]:", anchor="w").pack(
        # side="top", fill="x", expand="no"
        # )
        self.width_entry = ttk.Entry(size_frame, width=8)
        # self.width_entry.pack(side="left", fill="x", expand="no")
        # ttk.Label(size_frame, text="x").pack(side="left", fill="none", expand="no")
        self.height_entry = ttk.Entry(size_frame, width=8)
        # self.height_entry.pack(side="left", fill="x", expand="no")

        # ttk.Label(dpi_frame, text="DPI:", anchor="w", width=5).pack(
        # side="top", fill="x", expand="no"
        # )
        self.dpi_entry = ttk.Entry(dpi_frame, width=10)
        # self.dpi_entry.pack(side="left", fill="x", expand="no")

        self.width_entry.insert(0, "20.0")
        self.height_entry.insert(0, "15.0")
        self.dpi_entry.insert(0, "300")

        return self.path_btn

    def buttonbox(self):
        """add standard button box.

        #overridden from simpledialog.Dialog to fit style
        """

        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok)
        w.configure(style="Accent.TButton")
        w.pack(side="left", padx=10, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side="left", padx=10, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(side="bottom", pady=5)

    def validate(self):
        try:
            self.result = {
                "path": self.path_entry.get(),
                "size": (float(self.width_entry.get()), float(self.height_entry.get())),
                "dpi": int(self.dpi_entry.get()),
            }
            return True
        except:
            return False

    def ask_file_path(self):
        path = Path(
            asksaveasfilename(
                filetypes=[
                    (".png", "*.png"),
                    (".tiff", "*.tiff"),
                    (".svg", "*.svg"),
                    (".pdf", "*.pdf"),
                ],
                defaultextension=".png",
            )
        )
        self.path_entry.state(["!disabled"])
        self.path_entry.delete(0)
        self.path_entry.insert(0, path)
        self.path_entry.state(["disabled"])
        self.path = path


def ask_file() -> dict:
    """get file parameters (path, sheetname, has_headers) from the user"""
    l = OpenExcelDialog()
    return l.result


def ask_save_parameters() -> dict:
    """get figure save parameters from the user"""
    l = SaveFigureDialog()
    return l.result
