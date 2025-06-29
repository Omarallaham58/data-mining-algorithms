from utils.utils import Utils

class Hierarchical:
    def __init__(self, data, nb_clusters, linkage_type):
        self.data = data # list[float]
        self.nb_clusters = nb_clusters
        self.linkage_type = linkage_type
        self.clusters = {}
        self.distance_matrix = {}
        self.dendo_data = []

    #assign corresponding function to a variable
    def get_linkage_method(self):
        if self.linkage_type == 'single':
             return Utils.single_link
        elif self.linkage_type == 'complete':
            return Utils.complete_link
        elif self.linkage_type == 'average':
            return Utils.average_link
        else: return Utils.centroid_method

    def compute_distance_matrix(self):
        for i in range(len(self.clusters)):
            for j in range(i+1, len(self.clusters)):
                self.distance_matrix[(i,j)] = Utils.euclidean_distance(self.clusters[i][0], self.clusters[j][0])
                #first time we only have one list of values in each cluster (a point)
                # so we need to access it by index 0 since the function takes list[float] as param

    #algorithm
    def hierarchical(self):
        distance = self.get_linkage_method()
        cluster_id_map = {}

        for i, point in enumerate(self.data):
            self.clusters[i] = [point] # wrap each pt in a list for later clustering
            # dictionary of clusters [ cluster i:[ list of points[ ] ]
            cluster_id_map[i] = i
        next_linkage_id = len(self.data)

        if len(self.clusters)==1:
            return self.clusters, self.dendo_data

        self.compute_distance_matrix()

        while len(self.clusters) > 1:
            min_distance = float('inf') #infinity
            to_merge = (None,None) #tuple

            for (i,j), dis in self.distance_matrix.items(): #get both key and value
                if dis < min_distance:
                    min_distance = dis
                    to_merge = (i,j)
            a,b = to_merge

            new_cluster = []
            for point in self.clusters[a]:
                new_cluster.append(point)
            for point in self.clusters[b]:
                new_cluster.append(point)

            self.dendo_data.append([cluster_id_map[a], cluster_id_map[b], min_distance, len(new_cluster)])
            # the dendrogram function takes data as form: cluster_a id, cluster_b id, distance, nb of clusters in both

            self.clusters[next_linkage_id] = new_cluster
            cluster_id_map[next_linkage_id] = next_linkage_id

            #remove merged entries from dictionary
            self.clusters.pop(a)
            self.clusters.pop(b)

            #remove every key containing a or b from the matrix table
            keys_to_remove = []
            for key in self.distance_matrix.keys(): #get only keys ( , )
                if a in key or b in key:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.distance_matrix[key]

            #compute new distances
            for i in self.clusters.keys():
                if i != next_linkage_id:
                    self.distance_matrix[(i, next_linkage_id)] = distance(self.clusters[i], self.clusters[next_linkage_id])

            next_linkage_id += 1

        return self.clusters, self.dendo_data
