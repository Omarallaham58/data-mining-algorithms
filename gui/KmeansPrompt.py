import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading

from clustering.Kmeans import Kmeans
from visualizer.ScatterPlot import ScatterPlot
from gui.InputPrompt import InputPrompt

class KmeansPrompt(tk.Toplevel):
    def __init__(self, master, existing_data=None):
        super().__init__(master)
        self.title("K-means Clustering")
        self.geometry("750x750")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.data = existing_data or []
        self.original_data = existing_data or []

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=0)

        # Input handler
        self.input_handler = InputPrompt(self, container=main_frame)
        self.input_handler.pack(fill="both", expand=True, pady=0)
        self.input_handler.on_data_ready = self.on_data_ready

        # Initialize max_clusters
        self.max_clusters = 1 if not existing_data else max(1, len(existing_data))
        # Create cluster label variable
        self.cluster_label_text = tk.StringVar()
        self.update_cluster_label()

        # Hidden controls until data is ready
        self.controls_frame = ttk.Frame(main_frame)
        self.controls_frame.pack(fill="x", pady=5)
        self.controls_frame.pack_forget()

        self.create_controls_widgets()

    def on_close(self):
        self.destroy()
        #self.master.destroy()

    def update_cluster_label(self):
        """Update the cluster label text with current max_clusters"""
        self.cluster_label_text.set(f"Enter Number of Clusters (1 to {self.max_clusters}):")

    def clear_previous_data(self):
        """Clear all previous clustering results and reset the UI"""
        self.data = []
        self.controls_frame.pack_forget()
        if hasattr(self, 'cluster_entry'):
            self.cluster_entry.delete(0, tk.END)
            self.cluster_entry.insert(0, "1")

    def on_data_ready(self, data):
        if not data and not self.original_data:
            messagebox.showerror("No Data", "No data provided. Please use another input method.")
            return
        if len(data) == 1:
            messagebox.showerror("No Data", "You must input at least 2 distinct points.")
            return
        self.data = data or self.original_data
        self.original_data = self.data
        self.max_clusters = max(1, len(self.data))
        self.update_cluster_label()
        self.cluster_entry.delete(0, tk.END)
        self.cluster_entry.insert(0, "1")
        self.controls_frame.pack(fill="x", pady=(5, 5))

    def create_controls_widgets(self):
        ttk.Label(self.controls_frame, textvariable=self.cluster_label_text).pack(pady=5)
        self.cluster_entry = ttk.Entry(self.controls_frame)
        self.cluster_entry.insert(0, "1")
        self.cluster_entry.pack(pady=5)

        self.run_button = ttk.Button(self.controls_frame, text="Run Clustering", command=self.run_clustering)
        self.run_button.pack(pady=15)

        self.exit_button = ttk.Button(self.controls_frame, text="Exit", command=self.on_close)
        self.exit_button.pack(pady=5)

        self.loader = ttk.Label(self.controls_frame, text="Please wait... Processing...", state="disabled")
        self.loader.pack(pady=10)
        self.loader.pack_forget()

    def run_clustering(self):
        try:
            value = int(self.cluster_entry.get())
            if value < 1 or value > self.max_clusters:
                raise ValueError(f"Number of clusters must be between 1 and {self.max_clusters}")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        self.run_button.config(state="disabled")
        self.loader.pack()
        threading.Thread(target=self._process_clustering, args=(value,)).start()

    def _process_clustering(self, value):
        try:
            k = Kmeans(self.data, value)
            clusters = k.kmeans()
            plot = ScatterPlot(clusters)
            plot.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.run_button.config(state="normal")
            self.loader.pack_forget()
