import tkinter as tk
from gui import TeluguBusInfoGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = TeluguBusInfoGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
