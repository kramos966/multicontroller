import tkinter as tk
import tkinter.ttk as ttk

class CameraConfigs(ttk.LabelFrame):
    def __init__(self, parent, title=None):
        ttk.LabelFrame.__init__(self, parent, text=title)
        self.options = {}

