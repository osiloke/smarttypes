#exafmm_solver
self.exafmm_solver = ctypes.CDLL("%s/libcoulomb.so" % self.graphreduce_dir)

def reduce_with_exafmm(self):
    #helper functions specific to this method
    def x_to_reduction(x):
        list_of_coordinates = []
        for i in range(self.G.number_of_nodes()):
            x_cord = x[i * 3]
            y_cord = x[i * 3 + 1]
            list_of_coordinates.append([x_cord, y_cord])
        self.reduction = np.array(list_of_coordinates)

    def reduction_to_x():
        x = []
        for row in self.reduction:
            x.append(row[0])
            x.append(row[1])
            x.append(0)  # exafmm is 3d
        return np.array(x)

    #params
    iterations = 200
    attractive_force_factor = .5
    repulsive_force_factor = .00005
    potential_force_factor = 0.0

    #coordinates
    self.reduction = []
    if len(self.reduction):
        x = reduction_to_x()
    else:
        x = np.random.random(3 * self.n) * 10
    x[2::3] = 0  # make sure z is 0 for 2d
    q = np.ones(self.n) * repulsive_force_factor  # charges
    p = np.ones(self.n) * potential_force_factor  # potential
    f = np.zeros(3 * self.n)  # force

    energy_status_msg = 0
    for i in range(iterations):
        #repulsion
        # self.exafmm_solver.FMMcalccoulomb(self.n, x.ctypes.data, q.ctypes.data,
        #     p.ctypes.data, f.ctypes.data, 0)

        #attraction and move
        attraction_repulsion_factors = []
        for j in range(self.n):
            node_id = self.layout_ids[j]
            node_f = f[3 * j: 3 * j + 2]
            node_x = x[3 * j: 3 * j + 2]
            node_following = set(self.G.successors(node_id))

            #attraction
            attraction_f = np.array([0.0, 0.0])
            for following_id in node_following:
                following_idx = self.id_to_idx_map[following_id]
                following_x = x[3 * following_idx: 3 * following_idx + 2]
                following_following = set(self.G.successors(following_id))
                in_common = len(node_following.intersection(following_following))

                delta_x = following_x - node_x
                following_delta_x_norm = np.linalg.norm(delta_x)
                if following_delta_x_norm > EPS:
                    attraction_f += delta_x * np.log(1 + following_delta_x_norm) \
                        * attractive_force_factor * (in_common / 5.0)
            
            #compare attraction + repulsion forces
            repulsion_f_norm = np.linalg.norm(node_f)
            attraction_f_norm = np.linalg.norm(attraction_f)
            attraction_repulsion_factor = (attraction_f_norm / repulsion_f_norm)
            attraction_repulsion_factors.append(attraction_repulsion_factor)

            #combine attraction + repulsion forces
            node_f += attraction_f

            #move
            node_f_norm = np.linalg.norm(node_f)
            energy_status_msg += node_f_norm
            if node_f_norm < EPS:
                delta_x = 0
            else:
                delta_x = node_f / np.sqrt(node_f_norm)
            x[3 * j: 3 * j + 2] += delta_x * .35

        #clear spent force
        f = np.zeros(3 * self.n)

        #status msg
        if i % 1 == 0:
            x_to_reduction(x)
            self.normalize_reduction()
            self.find_dbscan_groups()
            print "iteration %s of %s -- energy: %s -- groups: %s -- att-rep-factor: %s" % (
                i, iterations,
                energy_status_msg if energy_status_msg else '?',
                self.n_groups,
                np.mean(attraction_repulsion_factors))

        #clear energy status msg
        energy_status_msg = 0

    #all done
    x_to_reduction(x)
    self.normalize_reduction()
    self.figure_out_reduction_distances()
    self.find_dbscan_groups()