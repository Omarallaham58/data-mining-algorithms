
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from association.Apriori import Apriori
from visualizer.GraphVisualizer import GraphVisualizer
import pandas as pd
import urllib.request
import threading
import json
import os

from utils.utils import Utils

class AssociationPrompt(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Association Rule Mining")
        self.geometry("750x700")
        self.transactions = []
        self.rules = set()
        self.local_dataset_map = self.load_dataset_info()
        self.local_dataset_names = list(self.local_dataset_map.keys())
        self.selected_local = tk.StringVar()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.create_widgets()

    def _on_close(self):
        self.destroy()
        #self.master.destroy()


    def create_widgets(self):
        self.input_method = tk.StringVar(value="manual")

        method_frame = ttk.LabelFrame(self, text="1. Select Input Method")
        method_frame.pack(fill="x", padx=10, pady=10)

        for text, val in [("Manual Input", "manual"), ("Upload CSV", "csv"), ("Load from URL", "url"),
                          ("Choose Existing Dataset", "local")]:
            ttk.Radiobutton(method_frame, text=text, variable=self.input_method, value=val).pack(side=tk.LEFT, padx=10)

        # 🆕 Pack confirm and refresh buttons side by side
        btn_frame = ttk.Frame(method_frame)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.confirm_button = ttk.Button(btn_frame, text="Confirm Input Type", command=self.show_input_section)
        self.confirm_button.pack(side=tk.LEFT, padx=5)

        self.refresh_button = ttk.Button(btn_frame, text="Refresh", command=self.refresh_ui)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.input_area_frame = ttk.Frame(self)
        self.input_area_frame.pack(fill="x", padx=10, pady=5)

        self.input_frames = {
            "manual": self.create_manual_input_frame(self.input_area_frame),
            "csv": self.create_path_frame(self.input_area_frame, "Browse CSV", self.browse_file),
            "url": self.create_path_frame(self.input_area_frame, "Enter URL", None)
        }

        local_frame = ttk.Frame(self.input_area_frame)
        ttk.Label(local_frame, text="Choose a dataset:").pack(anchor=tk.W, padx=5, pady=5)
        self.combo = ttk.Combobox(local_frame, textvariable=self.selected_local, values=self.local_dataset_names,
                                  state='readonly')
        self.combo.pack(fill="x", padx=10)

        self.description_label = ttk.Label(local_frame, text="", wraplength=600, justify=tk.LEFT)
        self.description_label.pack(padx=10, pady=5)

        self.combo.bind("<<ComboboxSelected>>", self.display_description)
        self.input_frames["local"] = local_frame

        for frame in self.input_frames.values():
            frame.pack_forget()

        param_frame = ttk.LabelFrame(self, text="2. Parameters")
        param_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(param_frame, text="Min Support Count:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.support_entry = ttk.Entry(param_frame)
        self.support_entry.insert(0, "2")
        self.support_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(param_frame, text="Min Confidence (0–1):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.conf_entry = ttk.Entry(param_frame)
        self.conf_entry.insert(0, "0.5")
        self.conf_entry.grid(row=1, column=1, padx=5, pady=5)

        self.run_button = ttk.Button(self, text="Run Apriori", command=self.start_thread)
        self.run_button.pack(pady=10)

        self.loader = ttk.Label(self, text="Processing... Please wait.")
        self.loader.pack(pady=5)
        self.loader.pack_forget()

        self.output_text = ScrolledText(self, height=15)
        self.output_text.pack(fill="both", padx=10, pady=10)

        self.visualize_button = ttk.Button(self, text="Visualize Rules", command=self.visualize_rules,
                                           state=tk.DISABLED)
        self.visualize_button.pack(pady=5)





    def create_path_frame(self, parent, label_text, browse_command):
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=label_text).pack(anchor=tk.W, padx=10)
        entry = ttk.Entry(frame)
        entry.pack(fill="x", padx=10, pady=5)
        if browse_command:
            ttk.Button(frame, text="Browse", command=browse_command).pack(pady=2)
        frame.entry = entry
        return frame

    def show_input_section(self):
        for frame in self.input_frames.values():
            frame.pack_forget()
        selected = self.input_method.get()
        frame = self.input_frames[selected]
        frame.pack(fill="x", pady=5)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.input_frames["csv"].entry.delete(0, tk.END)
            self.input_frames["csv"].entry.insert(0, path)

    def start_thread(self):
        threading.Thread(target=self.run_apriori).start()

    def run_apriori(self):
        self.loader.pack()
        self.run_button.config(state=tk.DISABLED)
        self.visualize_button.config(state=tk.DISABLED)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)

        try:
            method = self.input_method.get()

            if method == "manual":
                raw = self.input_frames["manual"].text_area.get("1.0", tk.END)
                self.transactions = Utils.parse_transactions(raw, source_type='manual')
                self.run_apriori_postload()

            elif method == "local":
                selected_file = self.selected_local.get()
                if not selected_file:
                    raise ValueError("No dataset selected.")
                path = os.path.join("local_datasets", selected_file)
                if not os.path.exists(path):
                    raise FileNotFoundError(f"File '{selected_file}' not found in 'local_datasets'.")
                df = pd.read_csv(path)
                dtype_info = Utils.getDataType(path)
                if dtype_info["categorical_ratio"] != 1.0:
                    df = Utils.discretize_numeric_columns(df)
                self.transactions = Utils.parse_transactions(df, source_type='csv')
                self.run_apriori_postload()

            elif method == "url":
                url = self.input_frames["url"].entry.get()
                threading.Thread(target=self.load_from_url, args=(url,)).start()
               # self.load_from_url(url)

            else:
                path = self.input_frames[method].entry.get()
                df = pd.read_csv(path)
                dtype_info = Utils.getDataType(path)
                if dtype_info["categorical_ratio"] != 1.0:
                    df = Utils.discretize_numeric_columns(df)
                self.transactions = Utils.parse_transactions(df, source_type='csv')
                self.run_apriori_postload()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.loader.pack_forget()
            self.run_button.config(state=tk.NORMAL)

    def load_from_url(self, url):
        try:
            path, _ = urllib.request.urlretrieve(url)
            df = pd.read_csv(path)
            dtype_info = Utils.getDataType(path)
            if dtype_info["categorical_ratio"] != 1.0:
                df = Utils.discretize_numeric_columns(df)
            self.transactions = Utils.parse_transactions(df, source_type='csv')
            self.run_apriori_postload()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load URL data: {str(e)}")
            self.loader.pack_forget()
            self.run_button.config(state=tk.NORMAL)

    def run_apriori_postload(self):
        try:
            minsup_count = int(self.support_entry.get())
            minconf = float(self.conf_entry.get())
            minsup = minsup_count / len(self.transactions)

            model = Apriori(self.transactions, minsup, minconf)
            self.rules = model.run()

            if not self.rules:
                self.output_text.insert(tk.END, "No rules found.\n")
            else:
                self.output_text.insert(tk.END, "=== Association Rules ===\n")
                for rule in sorted(self.rules, key=lambda r: r.lift, reverse=True):
                    self.output_text.insert(tk.END, f"{rule}\n")

            self.visualize_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.run_button.config(state=tk.NORMAL)
            self.loader.pack_forget()
            self.output_text.config(state=tk.DISABLED)

    def visualize_rules(self):
        if self.rules:
            GraphVisualizer(self.rules).plot_graph()
        else:
            messagebox.showwarning("No Rules", "No rules to visualize.")

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

    def create_manual_input_frame(self, parent):
        frame = ttk.Frame(parent)

        label = ttk.Label(
            frame,
            text="Enter each transaction (1 per line, comma separated):\nEx: Milk,Bread",
            foreground="gray"
        )
        label.pack(anchor=tk.W, padx=5, pady=(0, 2))

        text_area = ScrolledText(frame, height=7)
        text_area.pack(fill="both", expand=True)

        frame.text_area = text_area
        return frame

    def refresh_ui(self):
        # Clear input areas
        selected = self.input_method.get()
        if selected == "manual":
            self.input_frames["manual"].text_area.delete("1.0", tk.END)
        elif selected == "url":
            self.input_frames["url"].entry.delete(0, tk.END)
        elif selected == "csv":
            self.input_frames["csv"].entry.delete(0, tk.END)
        elif selected == "local":
            self.selected_local.set("")
            self.description_label.config(text="")

        # Clear output
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

        # Reset state
        self.visualize_button.config(state=tk.DISABLED)
        self.loader.pack_forget()

        # Clear previous transactions and rules
        self.transactions = []
        self.rules = set()
