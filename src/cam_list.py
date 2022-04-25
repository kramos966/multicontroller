import tkinter as tk
import tkinter.ttk as ttk

class CameraList(ttk.Labelframe):
    def __init__(self, parent, title=None):
        ttk.LabelFrame.__init__(self, parent, text=title)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.rowconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.buttons = []

    def add_camera(self, callback=None):
        n_cam = len(self.buttons)
        cam_button = ttk.Button(self, text=f"Cam {n_cam}", callback=callback)
        self.buttons.append(cam_button)
        cam_button.grid(row=n_cam//3, column=n_cam%3, sticky="nsew")

    def show_menu(self, *args):
        """Mostra la informació de cada càmera..."""
        # TODO
        pass

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    clist = CameraList(root, title="Camera list")
    clist.pack(fill="both")
    clist.add_camera()
    clist.add_camera()
    clist.add_camera()
    clist.add_camera()

    root.mainloop()
