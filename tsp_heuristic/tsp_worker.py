# -*- coding: utf-8 -*-

import os
import re
import random
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
        self.best_solution = {}

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
        self.best_solution = {}

    def read_meta(self, file_content):
        meta_reg = re.compile(r"(.*):(.*)")
        for line in file_content[:5]:
            match = re.match(meta_reg, line.lower().strip())
            self.meta[match.group(1).strip()] = match.group(2).strip()

    def read_data(self, file_content):
        data_reg = re.compile(r"\s*\d+\s*([\d.e+-]+)?\s*([\d.e+-]+)?")
        for line in file_content[6:]:
            if "EOF" in line or not line.strip():
                break
            match = re.match(data_reg, line.strip())
            self.data.append((float(match.group(1).strip()),
                              float(match.group(2).strip())))

    def calc_dist_matrix(self):
        z = numpy.array([[complex(x, y) for x, y in self.data]])
        return numpy.round(abs(z.T - z), NUMPY_PRECISION)

    #def greedy_tsp(self, distance_matrix):
    #    unvisited = range(1, len(self.data))
    #    current_node = 0
    #    trip = []
    #    distance_list = []
    #    trip.append(current_node)
    #    while unvisited:
    #        min_unvisited = numpy.argmin([distance_matrix[current_node][i] for i in unvisited])
    #        next_node = unvisited[min_unvisited]
    #        unvisited.remove(next_node)
    #        trip.append(next_node)
    #        distance_list.append(distance_matrix[current_node, next_node])
    #        current_node = next_node
    #    trip.append(0)
    #    distance_list.append(distance_matrix[current_node, 0])
    #    return trip, distance_list

    def run(self):
        if not numpy.any(self.dist_matrix):
            self.dist_matrix = self.calc_dist_matrix()

        self.reset()

        start = datetime.now()
        self.best_solution = self.iterated_local_search()
        self.runtime = datetime.now() - start

        self.log_run(start)

    def log_run(self, start):
        self.img = os.path.join(ROOT_DIR, 'log', 'figures', "{0}_{1}_{2}.png".format(
                self.meta['name'], str(self.best_solution['distance']), str(self.best_solution['iteration'] + 1)))
        with open(self.logfile, 'a') as f:
            f.write(";".join([str(start),
                              str(self.runtime),
                              str(self.iterations),
                              str(self.best_solution['iteration']),
                              str(self.best_solution['distance']),
                              os.path.basename(self.img)]) + '\n')

    def iterated_local_search(self, iteration_limit=200, idle_limit=50):
        solution = {'trip': [], 'distance': 0, 'iteration': 0}
        #initial solution starting at 0
        solution['trip'].append(0)
        random_trip = range(1, len(self.data))
        random.shuffle(random_trip)
        solution['trip'] += random_trip
        solution['distance'] = self.calculate_trip_distance(solution['trip'])
        solution = self.local_search(solution, idle_limit)
        solution['iteration'] = 1
        self.solutions.append(solution)
        self.iterations += 1

        for i in range(1, iteration_limit):
            new_solution = self.perturbation(solution)
            new_solution = self.local_search(new_solution, idle_limit)
            new_solution['iteration'] = i + 1
            if new_solution['distance'] < solution['distance']:
                solution = new_solution
            self.solutions.append(new_solution)
            self.iterations += 1
        return solution

    def calculate_trip_distance(self, solution):
        # create all edges as tuples beginning at 0 and ending at 0
        edges = [(solution[i], solution[i+1]) for i in range(0, len(solution)-1)]
        edges.append((solution[len(solution)-1], solution[0]))
        distance = 0
        for a, b in edges:
            distance += self.dist_matrix[a, b]
        return distance

    def local_search(self, solution, idle_limit):
        idle_counter = 0
        while idle_counter < idle_limit:
            trip = self.stochastic_two_opt(solution['trip'])
            distance = self.calculate_trip_distance(trip)
            if distance < solution['distance']:
                idle_counter = 0
                solution['trip'] = trip
                solution['distance'] = distance
            else:
                idle_counter += 1
        return solution

    def stochastic_two_opt(self, trip):
        trip = trip[:]
        c1 = random.randint(0, len(trip))
        c2 = random.randint(0, len(trip))
        exclude = [c1]
        if c1 == 0:
            exclude.append( len(trip) - 1)
        else:
            exclude.append( c1 - 1)

        if c2 == len(trip) - 1:
            exclude.append( 0)
        else:
            exclude.append( c1 + 1 )

        while c2 in exclude:
            c2 = random.randint(0, len(trip))

        c1, c2 = [c2, c1] if c2 < c1 else [c1, c2]
        c1c2_rev = trip[c1:c2]
        c1c2_rev.reverse()
        trip[c1:c2] = c1c2_rev
        trip.reverse()
        return trip

    def perturbation(self, solution):
        new_solution = {}
        new_solution['trip'] = self.double_bridge_move(solution['trip'])
        new_solution['distance'] = self.calculate_trip_distance(new_solution['trip'])
        return new_solution

    def double_bridge_move(self, trip):
        first_pos = 1 + random.randint(0, len(trip)/4)
        second_pos = first_pos + 1 + random.randint(0, len(trip)/4)
        third_pos = second_pos + 1 + random.randint(0, len(trip)/4)
        return trip[0:first_pos] + trip[third_pos:] + trip[second_pos:third_pos] + trip[first_pos:second_pos]