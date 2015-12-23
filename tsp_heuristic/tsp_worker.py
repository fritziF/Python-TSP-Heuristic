# -*- coding: utf-8 -*-

import re
from collections import OrderedDict
import numpy
from datetime import datetime
from PyQt4.QtCore import QThread, SIGNAL


NUMPY_PRECISION = 2
numpy.set_printoptions(precision=NUMPY_PRECISION)


class Problem(QThread):
    def __init__(self, file_path):
        QThread.__init__(self)
        self.meta = OrderedDict()
        self.data = []

        self.iterations = 0
        self.runtime = ""
        self.tsp_solution = None

        with open(file_path, 'r') as f:
            file_content = f.readlines()

        self.read_meta(file_content)
        self.read_data(file_content)

    def read_meta(self, file_content):
        meta_reg = re.compile(r"(.*):(.*)")
        for line in file_content[:5]:
            match = re.match(meta_reg, line.lower().strip())
            self.meta[match.group(1).strip()] = match.group(2).strip()

    def read_data(self, file_content):
        data_reg = re.compile(r"\s*\d+\s*([\d.]+)?\s*([\d.]+)?")
        for line in file_content[6:]:
            if "EOF" in line or not line.strip():
                break
            match = re.match(data_reg, line.strip())
            self.data.append((float(match.group(1).strip()),
                              float(match.group(2).strip())))

    def calc_dist_matrix(self):
        z = numpy.array([[complex(x, y) for x, y in self.data]])
        return numpy.round(abs(z.T-z), NUMPY_PRECISION)

    def solve_tsp(self, dist_matrix):


        solution = self.greedy_tsp(dist_matrix)


        return solution

    def greedy_tsp(self, distance_matrix):
        unvisited = range(1, len(self.data))
        current_node = 0
        trip = []
        self.iterations += 1

        while unvisited:
            min_unvisited = numpy.argmin([distance_matrix[current_node][i] for i in unvisited])
            next_node = unvisited[min_unvisited]
            unvisited.remove(next_node)
            trip.append((current_node, next_node))
            current_node = next_node

        trip.append((current_node, 0))

        return trip

    def run(self):
        dist_matrix = self.calc_dist_matrix()

        start = datetime.now()
        self.tsp_solution = self.greedy_tsp(dist_matrix)
        self.runtime = str(datetime.now() - start)


    def __str__(self):
        return '\n'.join([' : '.join((k, str(self.meta[k]))) for k in self.problem])


