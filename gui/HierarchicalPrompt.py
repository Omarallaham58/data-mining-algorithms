import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading

from clustering.hierarchical import Hierarchical
from visualizer.dendrogram import DendrogramVisualizer
from gui.InputPrompt import InputPrompt

class HierarchicalPrompt(tk.Toplevel):
    def __init__(self, master, existing_data=None):
        super().__init__(master)
        self.title("Hierarchical Clustering Options")
        self.geometry("850x850")
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.data = existing_data or []
        self.original_data = existing_data or []
        self.linkage_type = tk.StringVar(value="single")
        self.zoom = 1.0

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=0)

        # Input handler
        self.input_handler = InputPrompt(self, container=main_frame)
        self.input_handler.pack(fill="both", expand=True, pady=0)
        self.input_handler.on_data_ready = self.on_data_ready

        self.max_clusters = 1 if not existing_data else max(1, len(existing_data))
        self.cluster_label_text = tk.StringVar()
        self.update_cluster_label()

        self.controls_frame = ttk.Frame(main_frame)
        self.controls_frame.pack(fill="x", pady=5)
        self.controls_frame.pack_forget()

        self.create_controls_widgets()

    def update_cluster_label(self):
        self.cluster_label_text.set(f"Enter Number of Clusters (1 to {self.max_clusters}):")

    def clear_previous_data(self):
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
        ttk.Label(self.controls_frame, text="Select Linkage Type:").pack(pady=5)
        for text, value in [("Single", "single"), ("Complete", "complete"),
                            ("Average", "average"), ("Centroid", "centroid")]:
            ttk.Radiobutton(self.controls_frame, text=text, variable=self.linkage_type, value=value).pack(anchor=tk.W, padx=20)

        ttk.Label(self.controls_frame, textvariable=self.cluster_label_text).pack(pady=5)
        self.cluster_entry = ttk.Entry(self.controls_frame)
        self.cluster_entry.insert(0, "1")
        self.cluster_entry.pack(pady=5)

        self.run_button = ttk.Button(self.controls_frame, text="Run Clustering", command=self.run_clustering)
        self.run_button.pack(pady=15)

        self.exit_button = ttk.Button(self.controls_frame, text="Exit", command=self.destroy)
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
            h = Hierarchical(self.data, value, self.linkage_type.get())
            clusters, dendo_data = h.hierarchical()
            visualizer = DendrogramVisualizer(dendo_data, clusters, self.data, value)
            visualizer.plot_dendrogram()
            self.open_result_window(visualizer, clusters)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.run_button.config(state="normal")
            self.loader.pack_forget()

    def open_result_window(self, visualizer, clusters):
        result_win = tk.Toplevel(self)
        result_win.title("Dendrogram and Annex")
        result_win.geometry("1000x800")

        outer_frame = tk.Frame(result_win)
        outer_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer_frame)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        # scrollable_frame = tk.Frame(canvas)
        # CHANGED: use wrapper frame for centering content inside canvas
        scrollable_wrapper = tk.Frame(canvas)  # CHANGED

        # scrollable_frame.bind(
        #     "<Configure>",
        #     lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        # )

        # canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        # CHANGED: Add to canvas with anchor="n" to center horizontally
        canvas_window = canvas.create_window((0, 0), window=scrollable_wrapper, anchor="n")  # CHANGED

        # CHANGED: Update canvas window width to always match canvas size
        def update_window_width(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", update_window_width)  # CHANGED

        # Enable scrolling
        scrollable_wrapper.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        scrollbar.pack(side="right", fill="y")

        image = Image.open("dendrogram.png")
        self.tk_img = ImageTk.PhotoImage(image)
        self.img_label = tk.Label(scrollable_wrapper, image=self.tk_img)
        self.img_label.pack(pady=10)

        save_frame = tk.Frame(scrollable_wrapper)
        save_frame.pack(pady=5)

        ttk.Button(save_frame, text="Save as PNG", command=lambda: self.save_image(visualizer, "png")).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_frame, text="Save as SVG", command=lambda: self.save_image(visualizer, "svg")).pack(side=tk.LEFT, padx=5)

        annex_frame = tk.Frame(scrollable_wrapper)
        annex_frame.pack(fill="both", expand=True, padx=10, pady=10)

        button_frame = tk.Frame(annex_frame)
        button_frame.pack(pady=5)

        annex_text = tk.Text(annex_frame, wrap=tk.WORD)
        annex_text.pack(fill="both", expand=True)

        def display_content(generator_fn):
            annex_text.config(state=tk.NORMAL)
            annex_text.delete("1.0", tk.END)
            annex_text.insert(tk.END, generator_fn())
            annex_text.config(state=tk.DISABLED)

        ttk.Button(button_frame, text="Initial Objects", command=lambda: display_content(visualizer.format_objects)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Merge History", command=lambda: display_content(visualizer.format_merge_history)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Final Clusters", command=lambda: display_content(visualizer.format_final_clusters)).pack(side=tk.LEFT, padx=5)

        display_content(visualizer.format_objects)

    def save_image(self, visualizer, fmt):
        filetypes = [("PNG files", "*.png")] if fmt == "png" else [("SVG files", "*.svg")]
        ext = f".{fmt}"
        path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=filetypes)
        if path:
            try:
                source = visualizer.last_png_path if fmt == "png" else visualizer.last_svg_path
                shutil.copyfile(source, path)
            except Exception as e:
                messagebox.showerror("Save Error", str(e))
