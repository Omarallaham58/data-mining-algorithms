import math
import pandas as pd

class Utils:

    # ========== CLUSTERING UTILS ==========

    @staticmethod
    def euclidean_distance(object1: list[float], object2: list[float]) -> float:
        distance = 0
        for a, b in zip(object1, object2):
            distance += (a - b) ** 2
        return math.sqrt(distance)

    @staticmethod
    def single_link(cluster1: list[list[float]], cluster2: list[list[float]]):
        return min(Utils.euclidean_distance(c1, c2) for c1 in cluster1 for c2 in cluster2)

    @staticmethod
    def complete_link(cluster1: list[list[float]], cluster2: list[list[float]]):
        return max(Utils.euclidean_distance(c1, c2) for c1 in cluster1 for c2 in cluster2)

    @staticmethod
    def average_link(cluster1: list[list[float]], cluster2: list[list[float]]):
        distances = (Utils.euclidean_distance(c1, c2) for c1 in cluster1 for c2 in cluster2)
        return sum(distances) / (len(cluster1) * len(cluster2))

    @staticmethod
    def compute_centroid(cluster: list[list[float]]):
        n = len(cluster)
        dim = len(cluster[0])  # how many dimensions each pt have (all the same)
        centroid = [0.0] * dim  # initialize a list of 0s for each dimension
        for point in cluster:
            for i in range(dim):
                centroid[i] += point[i]
        return [x / n for x in centroid]

    @staticmethod
    def centroid_method(cluster1: list[list[float]], cluster2: list[list[float]]):
        def compute_centroid(cluster: list[list[float]]):
            n = len(cluster)
            dim = len(cluster[0])  # how many dimensions each pt have (all the same)
            centroid = [0.0] * dim  # initialize a list of 0s for each dimension
            for point in cluster:
                for i in range(dim):
                    centroid[i] += point[i]
            return [x / n for x in centroid]

        centroid1 = compute_centroid(cluster1)
        centroid2 = compute_centroid(cluster2)
        return Utils.euclidean_distance(centroid1, centroid2)

    @staticmethod
    def prepare_data_for_clustering(file_path):
        df = pd.read_csv(file_path)  # Load the CSV
        df.fillna(0, inplace=True)  # null -> 0
        # df_encoded = pd.get_dummies(df, dtype=int)
        df_encoded = pd.get_dummies(df, drop_first=True,
                                    dtype=int)  # Apply one-hot encoding to categorical columns (reduce one column)
        data = df_encoded.values.tolist()  # Convert DataFrame to list of lists
        # print(data) #test
        return data



    # ========== ASSOCIATION UTILS ==========
    @staticmethod
    def discretize_numeric_columns(df, bins=3, labels=None):
        df = df.copy()
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                try:
                    if labels is None:
                        label_set = ['low', 'medium', 'high'] if bins == 3 else [f"bin{i + 1}" for i in range(bins)]
                    else:
                        label_set = labels
                    df[col] = pd.cut(df[col], bins=bins, labels=label_set)
                except Exception as e:
                    print(f"Warning: Could not discretize column '{col}' — {e}")
        return df

    @staticmethod
    def getDataType(csvFilePath):
        df = pd.read_csv(csvFilePath)
        total_cols = numeric_cols = categorical_cols = other_cols = 0
        for col in df.columns:
            total_cols += 1
            if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
                numeric_cols += 1
            elif pd.api.types.is_string_dtype(df[col]):
                categorical_cols += 1
            elif pd.api.types.is_bool_dtype(df[col]):
                categorical_cols += 1
                df[col] = df[col].map({True: f"{col}=Yes", False: f"{col}=No"})
            else:
                other_cols += 1

        numeric_ratio = numeric_cols / total_cols
        categorical_ratio = categorical_cols / total_cols
        others_ratio = other_cols / total_cols

        if numeric_ratio >= 0.8:
            dataset_type = "numeric"
        elif categorical_ratio >= 0.8:
            dataset_type = "categorical"
        else:
            dataset_type = "mixed"

        return {
            "total_cols": total_cols,
            "numeric_cols": numeric_cols,
            "categorical_cols": categorical_cols,
            "other_cols": other_cols,
            "numeric_ratio": numeric_ratio,
            "categorical_ratio": categorical_ratio,
            "others_ratio": others_ratio,
            "dataset_type": dataset_type
        }

    @staticmethod
    def parse_transactions(source, source_type='manual', delimiter=','):
        from association.Transaction import Transaction
        transactions = []

        if source_type == 'manual':
            lines = source.strip().split("\n")
            for i, line in enumerate(lines):
                items = [item.strip().lower() for item in line.split(delimiter) if item.strip()]
                transactions.append(Transaction(tid=i + 1, items=items))

        elif source_type == 'csv':
            for i, row in source.iterrows():
                items = [f"{col}={str(val)}" for col, val in row.items() if pd.notnull(val)]
                transactions.append(Transaction(tid=i + 1, items=items))

        return transactions
