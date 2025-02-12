#!/usr/bin/env python3

import sys
import logging
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import Dialog

import pandas as pd

# Use root logger
logger = logging.getLogger(__name__)


class OpenExcelDialog(Dialog):
    """Class to create a Excel File opening dialog."""

    def __init__(self, parent=None, title: str | None = "Open Excel File"):
        super().__init__(parent, title=title)

    def body(self, master):
        """create dialog body.

        return widget that should have initial focus.

        #overridden from simpledialog.Dialog
        """
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = "."

        # self.iconbitmap(default=Path(base_path, "utils", "unige-icon.ico"))

        windowWidth = 300
        windowHeight = 250
        screenWidth = master.winfo_screenwidth()
        screenHeight = master.winfo_screenheight()
        xCoordinate = int((screenWidth / 2) - (windowWidth / 2))
        yCoordinate = int((screenHeight / 2) - (windowHeight / 2))
        self.geometry(f"{windowWidth}x{windowHeight}+{xCoordinate}+{yCoordinate}")
        self.resizable(False, False)

        paddings = {"padx": 5, "pady": 10}

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
        ttk.Label(worksheet_frame, text="Worksheet:", anchor="w", width=15).pack(
            side="left", fill="x", expand="yes"
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
        self.sheet_cb.pack(side="right", fill="x", expand="no", padx=5)

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
        sheets = pd.ExcelFile(path).sheet_names
        self.sheet_cb.configure({"values": sheets})
        self.sheet_cb.current(0)


def ask_file() -> dict:
    """get file parameters (path, sheetname, has_headers) from a user"""
    l = OpenExcelDialog()
    return l.result
