from .commander import CommanderDevice
from .console_frame import ConsoleLogger
from .cam_list import CameraList
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import asksaveasfilename, askopenfilename
import multiprocessing as mp
import platform
import json

class TkCommander(tk.Tk, CommanderDevice):
    def __init__(self, timeout=0.5):
        tk.Tk.__init__(self)
        CommanderDevice.__init__(self, timeout=timeout)
        self.config_theme()

        # Cua de missatges
        self.message_queue = mp.Queue()
        self.input_queue = mp.Queue()

        # Crea un menú
        self.create_menu()
        # Crea el logger
        self.logger_widget = ConsoleLogger(self, title="Console Log")
        self.logger_widget.pack(side="left", fill="both", expand=True)
        self.logger_widget.bind_ret(self.input_text)
        # Crea el widget de les càmeres
        self.camlist_widget = CameraList(self, title="Cameras")
        self.camlist_widget.pack(side="right", fill="both")

        # Comencem a actualitzar el log
        self.update_log()

    def create_menu(self):
        bg = self["background"]
        self.menubar = tk.Menu(self, tearoff=0, background=bg)
        self.config(menu=self.menubar)
        # Menú file
        self.filemenu = tk.Menu(self.menubar, tearoff=0, background=bg)
        self.filemenu.add_command(label="Open config.", accelerator="Ctrl+O", command=self.open_config)
        self.bind("<Control-o>", self.open_config)
        self.filemenu.add_command(label="Save config.", accelerator="Ctrl+S", command=self.save_config)
        self.bind("<Control-s>", self.save_config)
        self.filemenu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.quit)
        self.bind("<Control-q>", self.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

    def add_camera(self, *args):
        self.add_connection(*args)
        # Afegeix un botó per a la càmera
        self.camlist_widget.add_camera()

    def config_theme(self):
        """Configura el tema del tkinter segons el SO"""
        self.style = ttk.Style(self)
        current_plat = platform.system()
        if current_plat == "Linux":
            self.style.theme_use("clam")
        elif current_plat == "Windows":
            self.style.theme_use("winnative")
        elif current_plat == "Darwin":
            self.style.theme_use("aqua")
        bg = self.style.lookup("TFrame", "background")
        self["background"] = bg

    def put_text(self, text):
        # Posa els missatges en una cua
        self.message_queue.put(text)

    def input_text(self, *args):
        # Funció per a introduir comandes
        inputted_text = self.logger_widget.get_command()
        # Si no està buit el camp, retornem el texte
        if (not (inputted_text.isspace())):
            if inputted_text == "":
                return
            text = inputted_text.strip()
            # Posem el nostre text a la cua d'impressió
            self.put_text(f"> {text}")
            # ... i l'enviem a la cua d'ordres!
            self.input_queue.put(text)
            return inputted_text

    def update_log(self, *args):
        # Actualitzem el log amb els missatges dins la cua
        n_msg = self.message_queue.qsize()
        for i in range(n_msg):
            msg = self.message_queue.get()
            self.logger_widget.put_text(msg)

        # Comprovem els missatges després d'un cert temps d'espera
        self.after(100, self.update_log)

    def run(self):
        # Llegeix comandes, si n'hi hagués
        nc = self.input_queue.qsize()
        if not self.running:
            self.quit()
        for i in range(nc):
            command = self.input_queue.get()
            self.check_ports(command)
        self.after(100, self.run)

    def quit(self, *args):
        # Si estem treballant, tanquem les connexions bé
        if self.running:
            self.close_all()
        self.destroy()

    def command(self):
        # Comença el bucle principal en un altre procés
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.running = True
        self.run()
        self.mainloop()

    def save_config(self, *args):
        fname = asksaveasfilename()
        keys = self.connections.keys()  # Només ens interessen les claus...
        data = {}
        data["ip_devices"] = list(keys)
        if fname:
            with open(fname, "w") as f:
                json.dump(data, f, indent=4)

    def open_config(self, *args):
        fname = askopenfilename()
        if fname:
            with open(fname, "r") as f:
                data = json.load(f)

            # Un cop carregades les dades, cridem les connexions...
            connections = data["ip_devices"]
            for connection in connections:
                self.input_queue.put(f"connect {connection} 8888")
