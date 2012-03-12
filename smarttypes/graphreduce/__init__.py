
import os
from collections import defaultdict
import numpy as np
from scipy.spatial import distance
from sklearn.cluster import DBSCAN, MeanShift, estimate_bandwidth
import networkx
import ctypes
EPS = 1e-6


class GraphReduce(object):

    def __init__(self, reduction_id, initial_follower_followies_map):

        self.reduction_id = reduction_id
        self.initial_follower_followies_map = initial_follower_followies_map
        self.reduction = []
        self.groups = []
        self.n_groups = 0

        self.G = self.get_networkx_graph()
        self.n = self.G.number_of_nodes()
        print "Running graph_reduce on %s nodes." % self.n
        self.A = networkx.to_numpy_matrix(self.G)
        self.A = np.asarray(self.A)  # adjacency matrix

        self.layout_ids = []
        self.id_to_idx_map = {}
        i = 0
        for node_id in self.G.nodes():
            self.layout_ids.append(node_id)
            self.id_to_idx_map[node_id] = i
            i += 1

        self.in_degrees = self.A.sum(axis=0)
        for node_id, in_degree in self.G.in_degree_iter():
            i = self.id_to_idx_map[node_id]
            if in_degree != self.in_degrees[i]:
                raise Exception('This is not good. This should not happen.')

        ##file paths
        self.graphreduce_dir = os.path.dirname(os.path.abspath(__file__))
        self.graphreduce_io_dir = '%s/io' % self.graphreduce_dir
        if not os.path.exists(self.graphreduce_io_dir):
            os.makedirs(self.graphreduce_io_dir)
        self.reduction_file_name = 'reduction_%s.txt' % self.reduction_id
        self.reduction_file_path = '%s/%s' % (self.graphreduce_io_dir, self.reduction_file_name)
        self.linloglayout_input_file_name = 'linloglayout_input_%s.txt' % self.reduction_id
        self.linloglayout_input_file_path = '%s/%s' % (self.graphreduce_io_dir,
            self.linloglayout_input_file_name)

        # #load last reduction if it's there
        # if os.path.exists(self.reduction_file_path):
        #     self.load_reduction_from_file()

    def get_networkx_graph(self):
        if not '_G' in self.__dict__:
            self._G = networkx.DiGraph()
            edges = []
            for follower, followies in self.initial_follower_followies_map.items():
                for followie in followies:
                    if followie in self.initial_follower_followies_map:
                        edges.append((follower, followie))
            self._G.add_edges_from(edges)
        return self._G

    def load_reduction_from_file(self):
        f = open(self.reduction_file_path)
        list_of_coordinates = [[0,0]] * (self.n + 1)
        groups = [0] * (self.n + 1)
        for line in f:
            line_pieces = line.split(' ')
            node_id = line_pieces[0]
            node_idx = self.id_to_idx_map[node_id]
            x_value = float(line_pieces[1])
            y_value = float(line_pieces[2])
            group_num = int(line_pieces[4])
            list_of_coordinates[node_idx] = [x_value, y_value]
            groups[node_idx] = group_num
        self.reduction = np.array(list_of_coordinates)
        self.groups = np.array(groups) - 1
        self.n_groups = len(set(self.groups)) - (1 if -1 in self.groups else 0)

    def normalize_reduction(self):
        x_mean = np.mean(self.reduction[:,0])
        y_mean = np.mean(self.reduction[:,1])
        x_standard_deviation = np.std(self.reduction[:,0])
        y_standard_deviation = np.std(self.reduction[:,1])
        x_floor = x_mean - x_standard_deviation
        y_floor = y_mean - y_standard_deviation
        if x_floor < y_floor:
            print "mean: %s -- standard_deviation: %s" % (x_mean, x_standard_deviation)
            self.reduction -= x_floor
            self.reduction /= x_mean + x_standard_deviation * 2
        else:
            print "mean: %s -- standard_deviation: %s" % (y_mean, y_standard_deviation)
            self.reduction -= y_floor
            self.reduction /= y_mean + y_standard_deviation * 2

    def figure_out_reduction_distances(self):
        self.reduction_distances = distance.squareform(distance.pdist(self.reduction))

    def reduce_with_linloglayout(self):
        input_file = open(self.linloglayout_input_file_path, 'w')
        for node_id in self.layout_ids:
            for following_id in self.G.successors(node_id):
                input_file.write('%s %s \n' % (node_id, following_id))
        input_file.close()
        #to recompile
        #$ cd smarttypes/smarttypes/graphreduce/LinLogLayout/src/
        #$ javac -d ../bin LinLogLayout.java
        os.system('cd %s/LinLogLayout; java -cp bin LinLogLayout 2 %s %s;' % (
            self.graphreduce_dir,
            self.linloglayout_input_file_path,
            self.reduction_file_path
        ))
        self.load_reduction_from_file()
        self.normalize_reduction()
        #self.find_dbscan_groups()

    def reduce_with_particle_filter_simulation():
        """
        use the following objective function:
        - produce groups with a lot of link density
        """

    def generate_objective_score(self):
        """
        are goal is to is to find a lot of dense link communities

        we're also interested in the linlog objective:

         - http://www.smarttypes.org/blog/graph_reduction_linlog_nbody_simulation

        need to also look at groups from a high level, related groups 
        should be close together

        high-level we're interested in link prediction
        """
        all_distances_sum = np.sum(self.reduction_distances)
        connected_distances_sum = 1 #use in_degrees here
        obj_measure = all_distances_sum - np.log(connected_distances_sum)
        return obj_measure

    def find_dbscan_groups(self, eps=0.42, min_samples=12):
        self.figure_out_reduction_distances()
        S = 1 - (self.reduction_distances / np.max(self.reduction_distances))
        db = DBSCAN().fit(S, eps=eps, min_samples=min_samples)
        self.groups = db.labels_
        self.n_groups = len(set(self.groups)) - (1 if -1 in self.groups else 0)

