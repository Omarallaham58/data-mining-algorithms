import tkinter as tk
import urllib.request
import json
import threading
from tkinter import ttk, filedialog, messagebox
from utils.utils import Utils

class InputPrompt(ttk.Frame):
    def __init__(self, master, container=None):
        super().__init__(container or master)
        self.master = master
        self.input_method = tk.StringVar(value="manual")
        self.loader_label = None
        self.num_dimensions = 0
        self.entries = []
        self.table_frame = None
        self.dynamic_frame = None
        self.manual_buttons_frame = None
        self.selected_local = tk.StringVar()
        self.local_dataset_map = self.load_dataset_info()
        self.local_dataset_names = list(self.local_dataset_map.keys())

        self.create_widgets()

    def create_widgets(self):
        # Method selection frame
        method_frame = ttk.LabelFrame(self, text="Select Input Method")
        method_frame.pack(fill="x", padx=10, pady=(10,5))

        # Radio buttons for input methods
        methods = [
            ("Manual Input", "manual"),
            ("Upload CSV", "csv"),
            ("Load from URL", "url"),
            ("Choose Existing Dataset", "local")
        ]

        for text, val in methods:
            ttk.Radiobutton(method_frame, text=text, variable=self.input_method, value=val).pack(side=tk.LEFT, padx=10)

        button_container = ttk.Frame(method_frame)
        button_container.pack(fill="x", pady=(0, 5), expand=True)

        ttk.Button(button_container, text="Confirm Input Type", command=self.show_input_section).pack(side=tk.LEFT,
                                                                                                      padx=10,
                                                                                                      expand=True)
        ttk.Button(button_container, text="Refresh", command=self.refresh_ui).pack(side=tk.LEFT, padx=10, expand=True)

        self.input_area_frame = ttk.Frame(self)
        self.input_area_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.input_frames = {
            "manual": self.setup_manual_input(),
            "csv": self.create_path_frame("Browse CSV", self.browse_file),
            "url": self.create_path_frame("Enter URL", self.load_from_url),
            "local": self.setup_local_input()
        }

        # Hide all frames initially
        for frame in self.input_frames.values():
            frame.pack_forget()

    def refresh_ui(self):
        # Clear all dynamic content
        if self.dynamic_frame:
            for widget in self.dynamic_frame.winfo_children():
                widget.destroy()
        self.entries = []
        self.num_dimensions = 0

        if hasattr(self.master, 'clear_previous_data'):
            self.master.clear_previous_data()

        # Clear manual buttons if they exist
        if self.manual_buttons_frame:
            self.manual_buttons_frame.destroy()
            self.manual_buttons_frame = None

        # Reset the selected input method
        selected = self.input_method.get()
        if selected == "manual":
            # Reinitialize the manual input section
            self.input_frames["manual"].destroy()
            self.input_frames["manual"] = self.setup_manual_input()
            self.dynamic_frame = self.input_frames["manual"]
        elif selected == "url":
            self.input_frames["url"].entry.delete(0, tk.END)
        elif selected == "csv":
            self.input_frames["csv"].entry.delete(0, tk.END)
        elif selected == "local":
            self.selected_local.set("")

    def setup_manual_input(self):
        frame = ttk.Frame(self.input_area_frame)
        self.dynamic_frame = frame  # Reference for dynamic content

        # Dimension input
        ttk.Label(frame, text="Enter number of dimensions per point:").pack()
        self.dim_entry = ttk.Entry(frame)
        self.dim_entry.pack()
        ttk.Button(frame, text="Confirm", command=self.generate_manual_table).pack(pady=5)

        return frame

    def setup_local_input(self):
        frame = ttk.Frame(self.input_area_frame)

        # Dataset selection
        ttk.Label(frame, text="Choose a dataset:").pack(anchor=tk.W, padx=5, pady=5)
        self.combo = ttk.Combobox(frame, textvariable=self.selected_local,
                                  values=self.local_dataset_names, state='readonly')
        self.combo.pack(fill="x", padx=10)
        self.combo.bind("<<ComboboxSelected>>", self.display_description)

        # Description label
        self.description_label = ttk.Label(frame, text="", wraplength=600, justify=tk.LEFT)
        self.description_label.pack(padx=10, pady=5)

        # Load button
        ttk.Button(frame, text="Load Dataset", command=self.load_local_dataset).pack(pady=5)

        return frame

    def create_path_frame(self, label_text, browse_command):
        frame = ttk.Frame(self.input_area_frame)

        ttk.Label(frame, text=label_text).pack(anchor=tk.W, padx=10)
        entry = ttk.Entry(frame)
        entry.pack(fill="x", padx=10, pady=5)

        if browse_command:
            ttk.Button(frame, text="Browse", command=browse_command).pack(pady=2)

        frame.entry = entry  # Store reference to the entry widget
        return frame

    def clear_manual_input(self):
        """Clear all manual input widgets"""
        if self.table_frame:
            self.table_frame.destroy()
            self.table_frame = None
        self.entries = []

    def show_input_section(self):
        # Clear any previous manual buttons
        if self.manual_buttons_frame:
            self.manual_buttons_frame.destroy()
            self.manual_buttons_frame = None

        self.clear_manual_input()

        # Clear any previous data in the parent (HierarchicalPrompt)
        if hasattr(self.master, 'clear_previous_data'):
            self.master.clear_previous_data()

        # Hide all frames first
        for frame in self.input_frames.values():
            frame.pack_forget()

        # Show selected frame
        selected = self.input_method.get()
        self.input_frames[selected].pack(fill="x", pady=5)

        # Reset dynamic frame reference for manual input
        if selected == "manual":
            self.dynamic_frame = self.input_frames["manual"]



    def generate_manual_table(self):
        self.clear_manual_input()  # Clear any existing table

        try:
            self.num_dimensions = int(self.dim_entry.get())
            if self.num_dimensions <= 0:
                raise ValueError("Must be positive")
        except Exception:
            messagebox.showerror("Invalid input", "Please enter a valid number of dimensions.")
            return

        # Create scrollable frame for input rows
        scroll_frame = ttk.Frame(self.dynamic_frame)
        scroll_frame.pack(fill="both", expand=True, pady=5)

        canvas = tk.Canvas(scroll_frame, height=150)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_table = ttk.Frame(canvas)

        scrollable_table.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_table, anchor="n")  # align to top center
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # CHANGED

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ✅ Keep reference for add_manual_row/clear_manual_input
        self.table_frame = scrollable_table

        # Add two initial rows
        self.add_manual_row()
        self.add_manual_row()

        # Manual input control buttons
        self.manual_buttons_frame = ttk.Frame(self.dynamic_frame)
        self.manual_buttons_frame.pack(pady=5)

        ttk.Button(self.manual_buttons_frame, text="Add Row", command=self.add_manual_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.manual_buttons_frame, text="Submit Manual Data", command=self.submit_manual_input).pack(
            side=tk.LEFT, padx=5)





    def add_manual_row(self):
        row_entries = []
        row_index = len(self.entries)

        for j in range(self.num_dimensions):
            e = ttk.Entry(self.table_frame, width=10)
            e.grid(row=row_index, column=j, padx=2, pady=2)
            row_entries.append(e)

        self.entries.append(row_entries)

    def submit_manual_input(self):
        try:
            points = set()
            for row in self.entries:
                point = []
                for e in row:
                    val = e.get().strip()
                    point.append(float(val) if val != "" else 0.0)
                if any(e.get().strip() for e in row):  # skip empty rows
                    points.add(tuple(point))

            if not points:
                raise ValueError("At least two data points are required.")

            data = [list(p) for p in points]
            self.on_data_ready(data)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.input_frames["csv"].entry.delete(0, tk.END)
            self.input_frames["csv"].entry.insert(0, path)
            self.load_from_file(path)

    def load_from_file(self, path=None):
        if not path:
            path = self.input_frames["csv"].entry.get()

        if not path:
            return

        try:
            self.show_loader(True)
            data = Utils.prepare_data_for_clustering(path)
            self.on_data_ready(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
        finally:
            self.show_loader(False)

    def load_from_url(self):
        url = self.input_frames["url"].entry.get()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a URL first")
            return

        try:
            self.show_loader(True)
            threading.Thread(target=self._fetch_and_load_url_data, args=(url,)).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load URL: {str(e)}")
            self.show_loader(False)

    def _fetch_and_load_url_data(self, url):
        try:
            path, _ = urllib.request.urlretrieve(url)
            df = Utils.prepare_data_for_clustering(path)
            self.on_data_ready(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process URL data: {str(e)}")
        finally:
            self.show_loader(False)

    def load_local_dataset(self):
        selected = self.selected_local.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a dataset first")
            return

        try:
            self.show_loader(True)
            path = f"local_datasets/{selected}"
            data = Utils.prepare_data_for_clustering(path)
            self.on_data_ready(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset: {str(e)}")
        finally:
            self.show_loader(False)

    def load_dataset_info(self):
        try:
            with open("local_datasets/dataset_info.json", "r") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load dataset info: {e}")
            return {}

    def display_description(self, event=None):
        selected = self.selected_local.get()
        desc = self.local_dataset_map.get(selected, "No description available.")
        self.description_label.config(text=desc)

    def show_loader(self, show):
        if show:
            if not self.loader_label:
                self.loader_label = ttk.Label(self, text="Processing...")
            self.loader_label.pack(pady=10)
        elif self.loader_label:
            self.loader_label.pack_forget()

    def on_data_ready(self, data):
        """This should be overridden by parent class"""
        print("Data ready:", data)

    def clear_dynamic_frame(self):
        if self.dynamic_frame:
            for widget in self.dynamic_frame.winfo_children():
                widget.destroy()
        self.entries = []
        self.num_dimensions = 0

    def clear_all_inputs(self):
        self.clear_dynamic_frame()
        self.input_method.set("manual")