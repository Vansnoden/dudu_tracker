import tkinter as tk

class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        new_win_button = tk.Button(self, text="Create new window", 
                                   command=self.new_window)
        new_win_button.pack(side="top", padx=20, pady=20)

    def new_window(self):
        top = tk.Toplevel(self)
        label = tk.Label(top, text="Hello, world")
        b = tk.Button(top, text="Destroy me", 
                      command=lambda win=top: win.destroy())
        label.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        b.pack(side="bottom")

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()