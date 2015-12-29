# -*- coding: utf-8 -*-

import os
import re
from collections import OrderedDict
import numpy
from datetime import datetime
from PyQt4.QtCore import QThread, SIGNAL

NUMPY_PRECISION = 2
numpy.set_printoptions(precision=NUMPY_PRECISION)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class Problem(QThread):
    def __init__(self, file_path):
        QThread.__init__(self)
        self.meta = OrderedDict()
        self.data = []

        self.dist_matrix = None
        self.iterations = 0
        self.runtime = ""
        self.solutions = []
        self.best_solution = None

        with open(file_path, 'r') as f:
            file_content = f.readlines()

        self.read_meta(file_content)
        self.read_data(file_content)

        self.logfile = os.path.join(ROOT_DIR, 'log', self.meta['name'] + '.csv')
        if not os.path.isfile(self.logfile):
            with open(self.logfile, 'w') as f:
                f.write("timestamp;runtime;iterations;best-iteration;trip-distance;figure\n")

    def reset(self):
        self.iterations = 0
        self.runtime = ""
        self.solutions = []
        self.best_solution = None
        self.best_iteration = 0

    def read_meta(self, file_content):
        meta_reg = re.compile(r"(.*):(.*)")
        for line in file_content[:5]:
            match = re.match(meta_reg, line.lower().strip())
            self.meta[match.group(1).strip()] = match.group(2).strip()

    def read_data(self, file_content):
        data_reg = re.compile(r"\s*\d+\s*([\d.e\+]+)?\s*([\d.]+)?")
        for line in file_content[6:]:
            if "EOF" in line or not line.strip():
                break
            match = re.match(data_reg, line.strip())
            self.data.append((float(match.group(1).strip()),
                              float(match.group(2).strip())))

    def calc_dist_matrix(self):
        z = numpy.array([[complex(x, y) for x, y in self.data]])
        return numpy.round(abs(z.T - z), NUMPY_PRECISION)

    def greedy_tsp(self, distance_matrix):
        unvisited = range(1, len(self.data))
        current_node = 0
        trip = []
        distance_list = []

        while unvisited:
            min_unvisited = numpy.argmin([distance_matrix[current_node][i] for i in unvisited])
            next_node = unvisited[min_unvisited]
            unvisited.remove(next_node)
            trip.append((current_node, next_node))
            distance_list.append(distance_matrix[current_node, next_node])
            current_node = next_node

        trip.append((current_node, 0))
        distance_list.append(distance_matrix[current_node, 0])
        return trip, distance_list

    def run(self):
        if not numpy.any(self.dist_matrix):
            self.dist_matrix = self.calc_dist_matrix()

        self.reset()
        start = datetime.now()
        best_trip_distance = 0

        # loop goes here :)

        solution, distance_list = self.greedy_tsp(self.dist_matrix)
        trip_distance = sum(distance_list)
        iteration = self.iterations
        self.solutions.append((trip_distance, solution))

        if self.iterations == 0:
            best_solution = solution
            best_trip_distance = trip_distance
            best_iteration = iteration
        elif trip_distance < best_trip_distance:
            best_solution = solution
            best_trip_distance = trip_distance
            best_iteration = iteration

        self.iterations += 1

        # loop ends here :)


        self.best_solution = best_solution
        self.best_iteration = best_iteration
        self.trip_distance = best_trip_distance
        self.runtime = datetime.now() - start

        self.img = os.path.join(ROOT_DIR, 'log', 'figures', "{0}_{1}_{2}.png".format(
                self.meta['name'], str(self.best_iteration + 1), str(self.trip_distance)))
        self.log_run(start)

    def log_run(self, start):
        with open(self.logfile, 'a') as f:
            f.write(";".join([str(start),
                              str(self.runtime),
                              str(self.iterations),
                              str(self.best_iteration),
                              str(self.trip_distance),
                              os.path.basename(self.img)]) + '\n')

    def __str__(self):
        return '\n'.join([' : '.join((k, str(self.meta[k]))) for k in self.problem])
