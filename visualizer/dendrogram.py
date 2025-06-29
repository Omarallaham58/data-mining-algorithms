import shutil
from tkinter import messagebox

import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
import numpy as np

class DendrogramVisualizer:
    def __init__(self, dendo_data, clusters, original_data, nb_clusters):
        self.dendo_data = dendo_data
        self.clusters = clusters
        self.original_data = original_data
        self.nb_clusters = nb_clusters
        self.labels = []

    def generate_labels(self):
        self.labels = [f'Object {i}' for i in range(len(self.original_data))]

    def convert_for_dendrogram(self):
        epsilon = 0.15
        dendo_jittered = []
        for i, row in enumerate(self.dendo_data):
            # Copy the row to avoid mutating original data
            new_row = list(row)  # convert from np.array or list to ensure it's mutable
            new_row[2] += i * epsilon  # Add jitter to distance
            dendo_jittered.append(new_row)

        return np.array(dendo_jittered)

    def get_color_threshold(self, linkage_matrix):
        # extract the distances at which clusters were merged (3rd column of linkage matrix)
        distances = linkage_matrix[:, 2]  # Distances at each merge (2nd column for all rows)
        n_merges = len(distances)

        # we set the threshold above the highest distance so that no cut happens
        if self.nb_clusters == 1:
            return np.max(distances) + 1

        # total merges = (number of points - 1)
        # to get N final clusters, we stop after (total_points - N) merges
        # So we cut the dendrogram just below the merge that would reduce us to (nb_clusters - 1)
        # The index from the end of the array gives us this threshold
        # do the calculation where we need to cut off, return the value to the method then when it reaches it, it does the threshold
        cut_index = -(self.nb_clusters - 1)
        return distances[cut_index]

    def plot_dendrogram(self):
        self.generate_labels()
        linkage_matrix = self.convert_for_dendrogram()
        plt.figure(figsize=(10, 6))
        color_threshold = self.get_color_threshold(linkage_matrix)
        dendrogram(linkage_matrix,
                   labels=np.array(self.labels),
                   color_threshold=color_threshold,
                   above_threshold_color='white')
        t = f'Hierarchical Clustering Dendrogram, Final Number of Clusters is {self.nb_clusters}'
        plt.title(t)
        plt.xlabel('Data Objects')
        plt.ylabel('Distance')
        plt.tight_layout()

        self.last_png_path = "dendrogram.png"
        self.last_svg_path = "dendrogram.svg"

        plt.savefig("dendrogram.svg", format='svg', bbox_inches='tight')
        plt.savefig("dendrogram.png", format='png', bbox_inches='tight')
        # plt.show()

    # for annexes
    def format_objects(self):
        formatted = "\n--- Original Data ---\n"
        for i in range(len(self.original_data)):
            formatted += f'Object {i}: {self.original_data[i]}\n'
        return formatted

    def format_merge_history(self):
        formatted = "\n--- Dendrogram Merge History ---\n"
        if self.nb_clusters == len(self.original_data):
            formatted += "Each object is its own cluster, no merges.\n"
        else:
            # Only print merges until the number of clusters is achieved
            required_merges = len(self.original_data) - self.nb_clusters
            for idx, merge in enumerate(self.dendo_data[:required_merges]): # all 'required_rows' from the list
                a, b, dist, count = merge
                formatted += f"{idx + 1}. Merged {a} + {b} | Distance: {dist:.2f} | New size: {count}\n"
        return formatted

    def format_final_clusters(self):
        formatted = "\n--- Final Clusters ---\n"

        n_points = len(self.original_data)
        required_merges = n_points - self.nb_clusters

        # Initial clusters (each object by index)
        cluster_map = {i: [i] for i in range(n_points)}  # id -> list of object indices
        next_id = n_points  # Next cluster id after initial ones

        for i, merge in enumerate(self.dendo_data):
            if i >= required_merges:
                break  # Stop when we've reached the desired number of clusters

            a, b, dist, count = merge
            # Merge clusters
            merged = cluster_map[a] + cluster_map[b]
            cluster_map[next_id] = merged
            del cluster_map[a]
            del cluster_map[b]
            next_id += 1

        # Format the final clusters
        for idx, (cid, obj_indices) in enumerate(cluster_map.items(), 1):
            formatted += f"Cluster {idx}: "
            formatted += ", ".join(f"Object {i}" for i in obj_indices) # ({self.original_data[i]}
            formatted += "\n"

        return formatted





    def save_images_only(self, linkage_matrix=None):
        """Plot dendrogram and save it silently without showing."""
        if linkage_matrix is None:
            linkage_matrix = self.convert_for_dendrogram()

        plt.figure(figsize=(10, 6))
        color_threshold = self.get_color_threshold(linkage_matrix)
        dendrogram(linkage_matrix,
                   labels=np.array(self.labels),
                   color_threshold=color_threshold,
                   above_threshold_color='white')
        plt.title(f'Hierarchical Clustering Dendrogram, Final Clusters: {self.nb_clusters}')
        plt.xlabel('Data Objects')
        plt.ylabel('Distance')
        plt.tight_layout()

        self.last_png_path = "dendrogram.png"
        self.last_svg_path = "dendrogram.svg"

        plt.savefig(self.last_svg_path, format='svg', bbox_inches='tight')
        plt.savefig(self.last_png_path, format='png', bbox_inches='tight')
        plt.close()




