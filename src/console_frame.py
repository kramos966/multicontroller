import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk

class TtkScrollText(ttk.Frame):
    """Widget d'entrada de text feta amb ttk."""
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        # Quadre de text
        self.text_widget = tk.Text(self)
        self.text_widget.pack(side="left", expand=True, fill="both")

        # Barra de posició
        # TODO: La barra de posicionament desaprareix si la mida de la finestra es fa massa petita...
        self.scrollbar = ttk.Scrollbar(self, command=self.text_widget.yview, orient="vertical")
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", expand=False, fill="y")

    def enable(self):
        self.text_widget.configure(state="normal")

    def disable(self):
        self.text_widget.configure(state="disabled")

    def put_text(self, text):
        self.text_widget.insert(tk.INSERT, text+"\n")

class ConsoleEntry(ttk.Entry):
    """Barra d'entrada de comandes. Té un mètode d'esborrat sencer en prémer enter."""
    def __init__(self, parent):
        ttk.Entry.__init__(self, parent)

    def get_command(self):
        command = self.get()
        self.delete(0, tk.END)
        return command

class ConsoleLogger(ttk.Labelframe):
    """Quadre (tk.Labelframe) que conté un widget de logging i una barra de 
    comandes."""
    def __init__(self, parent, title=None):
        ttk.Labelframe.__init__(self, parent, text=title, labelanchor="nw")

        self.logger = TtkScrollText(self)
        self.logger.pack(expand=True, fill="both")
        self.logger.disable()

        self.text_entry = ConsoleEntry(self)
        self.text_entry.pack(expand=False, fill="x")

    def put_text(self, text):
        self.logger.enable()
        self.logger.put_text(text)
        self.logger.disable()

    def get_command(self):
        command = self.text_entry.get_command()
        return command

    def bind_ret(self, func):
        self.text_entry.bind("<Return>", func)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    log = ConsoleLogger(root, title="Console Log")
    log.pack(fill="both", expand=True)
    root.mainloop()
