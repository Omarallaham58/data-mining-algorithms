# visualizer/GraphVisualizer.py

import matplotlib.pyplot as plt
import networkx as nx
from association.Rule import Rule
from tkinter import Toplevel, Label
from PIL import Image, ImageTk

class GraphVisualizer:
    def __init__(self, rules: set[Rule]):
        self.rules = rules


    def plot_graph(self):
        #print("Function entered plot")
        G = nx.DiGraph()
        for rule in self.rules:
            for a in rule.antecedent:
                for c in rule.consequent:
                    G.add_edge(a, c, label=f"{rule.confidence:.2f}")

        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 6))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500,
                font_size=10, edge_color='gray')
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.title("Association Rules Network")
        plt.tight_layout()
        plt.savefig("assoc_rules.png")
        plt.close()  # <-- Close the Matplotlib figure to avoid memory leaks

        # Show in a new Tkinter window
        top = Toplevel()
        top.title("Association Rules Network")
        top.geometry("800x600")

        image = Image.open("assoc_rules.png")
        #image = image.resize((780, 580), Image.ANTIALIAS)  # Resize to fit window
        image = image.resize((780, 580), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        label = Label(top, image=photo)
        label.image = photo  # Keep reference
        label.pack(padx=10, pady=10)
