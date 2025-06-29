import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA


class ScatterPlot:
    def __init__(self, clusters):
        self.clusters = clusters
        self.dimensionality = len(clusters[0]['data'][0])

    def show(self):
        window = tk.Toplevel()
        window.title("K-Means Clustering Result")
        window.geometry("900x600")

        plot_frame = ttk.Frame(window)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_frame = ttk.Frame(window, width=300)
        text_frame.pack(side=tk.RIGHT, fill=tk.Y)
        text_frame.pack_propagate(False)

        fig = plt.figure(figsize=(6, 6))
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan', 'olive']

        if self.dimensionality > 3:
            # Flatten all data points and centroids
            all_points = [point for cluster in self.clusters for point in cluster['data']]
            all_centroids = [cluster['centroid'] for cluster in self.clusters]

            # Apply PCA to reduce to 3D
            all_reduced = PCA(n_components=3).fit_transform(all_points + all_centroids)
            total_points = len(all_points)
            reduced_points = all_reduced[:total_points]
            reduced_centroids = all_reduced[total_points:]

            # Rebuild clusters with reduced data
            index = 0
            for i, cluster in enumerate(self.clusters):
                size = len(cluster['data'])
                cluster['data_3d'] = reduced_points[index:index + size]
                cluster['centroid_3d'] = reduced_centroids[i]
                index += size

            ax = fig.add_subplot(111, projection='3d')
            for idx, cluster in enumerate(self.clusters):
                points = cluster['data_3d']
                centroid = cluster['centroid_3d']
                x_vals = [p[0] for p in points]
                y_vals = [p[1] for p in points]
                z_vals = [p[2] for p in points]
                ax.scatter(x_vals, y_vals, z_vals, color=colors[idx % len(colors)], label=f'Cluster {idx+1}')
                ax.scatter(centroid[0], centroid[1], centroid[2], color='black', marker='x', s=100)

        elif self.dimensionality == 3:
            ax = fig.add_subplot(111, projection='3d')
            for idx, cluster in enumerate(self.clusters):
                points = cluster['data']
                centroid = cluster['centroid']
                x_vals = [p[0] for p in points]
                y_vals = [p[1] for p in points]
                z_vals = [p[2] for p in points]
                ax.scatter(x_vals, y_vals, z_vals, color=colors[idx % len(colors)], label=f'Cluster {idx+1}')
                ax.scatter(centroid[0], centroid[1], centroid[2], color='black', marker='x', s=100)

        elif self.dimensionality == 2:
            ax = fig.add_subplot(111)
            for idx, cluster in enumerate(self.clusters):
                points = cluster['data']
                centroid = cluster['centroid']
                x_vals = [p[0] for p in points]
                y_vals = [p[1] for p in points]
                ax.scatter(x_vals, y_vals, color=colors[idx % len(colors)], label=f'Cluster {idx+1}')
                ax.scatter(centroid[0], centroid[1], color='black', marker='x', s=100)

        elif self.dimensionality == 1:
            ax = fig.add_subplot(111)
            for idx, cluster in enumerate(self.clusters):
                points = [p[0] for p in cluster['data']]
                centroid = cluster['centroid'][0]
                ax.scatter(points, [0] * len(points), color=colors[idx % len(colors)], label=f'Cluster {idx+1}')
                ax.scatter(centroid, 0, color='black', marker='x', s=100)

        ax.set_title("K-Means Clusters")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)

        for idx, cluster in enumerate(self.clusters):
            text_widget.insert(tk.END, f"Cluster {idx+1}:\n")
            text_widget.insert(tk.END, f"  Centroid: {cluster['centroid']}\n")
            text_widget.insert(tk.END, f"  Points:\n")
            for point in cluster['data']:
                text_widget.insert(tk.END, f"    {point}\n")
            text_widget.insert(tk.END, "\n")
