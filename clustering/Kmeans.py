import random
from utils.utils import Utils


class Kmeans:
    def __init__(self, data, nb_clusters):
        self.data = data
        self.nb_clusters = nb_clusters

    def kmeans(self):
        if self.nb_clusters == 1:
            return [{
                'data': self.data,
                'centroid': Utils.compute_centroid(self.data)
            }]

        clusters = []
        # get random numbers to initialize the centroids
        nums = random.sample(range(len(self.data)), self.nb_clusters)

        for index in nums:
            clusters.append({
                'data': [self.data[index]],
                'centroid': self.data[index]
            })

        if self.nb_clusters == len(self.data):
            return clusters

        old_centroids = []
        for cluster in clusters:
            old_centroids.append(cluster['centroid'])

        while True:
            for cluster in clusters:
                cluster['data'] = []

            for point in self.data:
                closest_cluster_index = 0
                min_distance = Utils.euclidean_distance(point, clusters[0]['centroid'])
                for i in range(1, len(clusters)):
                    distance = Utils.euclidean_distance(point, clusters[i]['centroid'])
                    if distance < min_distance:
                        min_distance = distance
                        closest_cluster_index = i
                # add the point to the closest cluster
                clusters[closest_cluster_index]['data'].append(point)

            new_centroids = []
            # update the centroids
            for cluster in clusters:
                new_centroid = Utils.compute_centroid(cluster['data'])
                cluster['centroid'] = new_centroid
                new_centroids.append(new_centroid)

            # stop the algorithm if the centroids have not changed
            if new_centroids == old_centroids:
                return clusters

            old_centroids = new_centroids
