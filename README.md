# Data Mining Suite - Clustering & Association Rule Mining



A comprehensive desktop application implementing:
- **Clustering Algorithms**: K-Means and Hierarchical
- **Association Rule Mining**: Apriori algorithm
- **Multi-input Support**: Manual, CSV, URL, and preloaded datasets

## 🔍 Features

### Core Functionality
- **Four Input Methods**:
  - Manual data entry
  - CSV file upload
  - URL dataset loading
  - Preloaded datasets
- **Threaded Processing** for responsive UI

### Clustering Modules
- **K-Means**:
  - Random centroid initialization
  - Euclidean distance metrics
  - Visualized via 2D/3D scatter plots (PCA for high-dim)
- **Hierarchical**:
  - Multiple linkage methods (single, complete, average, centroid)
  - Interactive dendrogram visualization

### Association Rule Mining
- **Apriori Algorithm**:
  - Support/confidence/lift calculations
  - Rule network visualization
  - Automatic data discretization

## 🛠️ Tech Stack
- **Language**: Python 3.8+
- **GUI**: Tkinter
- **Visualization**: Matplotlib, NetworkX
- **Data Handling**: Pandas, NumPy
- **Concurrency**: Threading

## 📦 Installation
```bash
git clone https://github.com/yourusername/data-mining-suite.git
cd data-mining-suite
pip install -r requirements.txt
