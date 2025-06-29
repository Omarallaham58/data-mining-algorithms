import tkinter as tk
from tkinter import ttk
from gui.HierarchicalPrompt import HierarchicalPrompt
from gui.KmeansPrompt import KmeansPrompt
from gui.AssociationPrompt import AssociationPrompt

class MainApp:
    def __init__(self, master):
        self.master = master
        master.title("Data Mining Toolkit")
        master.geometry("400x250")

        ttk.Label(master, text="Select a Task:", font=("Arial", 14)).pack(pady=20)

        ttk.Button(master, text="Association Rule Mining", command=self.open_association).pack(pady=10, fill="x", padx=40)
        ttk.Button(master, text="K-Means Clustering", command=self.open_kmeans).pack(pady=10, fill="x", padx=40)
        ttk.Button(master, text="Hierarchical Clustering", command=self.open_hierarchical).pack(pady=10, fill="x", padx=40)

    def open_association(self):
        AssociationPrompt(self.master)

    def open_kmeans(self):
        KmeansPrompt(self.master)

    def open_hierarchical(self):
        HierarchicalPrompt(self.master)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
