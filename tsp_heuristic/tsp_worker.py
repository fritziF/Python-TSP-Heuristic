# -*- coding: utf-8 -*-

import os
import re
import random
from collections import OrderedDict
import numpy
from itertools import combinations
from datetime import datetime
from PyQt4.QtCore import QThread

NUMPY_PRECISION = 2
numpy.set_printoptions(precision=NUMPY_PRECISION)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def randomize_tour(length):
    tour = []
    tour.append(0)
    random_tour = range(1, length)
    random.shuffle(random_tour)
    tour += random_tour
    return tour


class Problem(QThread):
    def __init__(self, file_path):
        QThread.__init__(self)
        self.meta = OrderedDict()
        self.data = []
        self.iteration_limit = 200
        self.alternative = False
        self.idle_limit = 50

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
                f.write("timestamp;total-runtime;runtime-til-best;iterations;best-iteration;tour-distance;iteration-limit;use-no-improve;idle-limit;figure\n")

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

    def setParameters(self, iteration_limit, alternative, idle_limit):
        self.iteration_limit = iteration_limit
        self.idle_limit = idle_limit
        self.alternative = alternative

    def calc_dist_matrix(self):
        z = numpy.array([[complex(x, y) for x, y in self.data]])
        return numpy.round(abs(z.T - z), NUMPY_PRECISION)

    def run(self):
        if not numpy.any(self.dist_matrix):
            self.dist_matrix = self.calc_dist_matrix()

        self.reset()

        start = datetime.now()
        self.best_solution = self.iterated_local_search(self.iteration_limit, self.idle_limit, start)
        self.runtime = datetime.now() - start

        self.log_run(start)

    def log_run(self, start):
        alt_suffix = '' if not self.alternative else 'alt_'
        self.img = os.path.join(ROOT_DIR, 'log', 'figures', "{0}_{1}{2}_{3}.png".format(
                self.meta['name'],
                alt_suffix,
                str(self.best_solution['distance']),
                str(self.best_solution['iteration'] + 1)))
        with open(self.logfile, 'a') as f:
            f.write(";".join([str(start),
                              str(self.runtime),
                              str(self.best_solution['runtime']),
                              str(self.iterations),
                              str(self.best_solution['iteration']),
                              str(self.best_solution['distance']),
                              str(self.iteration_limit),
                              str(self.alternative),
                              str(self.idle_limit),
                              os.path.basename(self.img)]) + '\n')

    def iterated_local_search(self, iteration_limit, idle_limit, start_timestamp):
        """Source: Algorithm3 from http://www.scielo.br/scielo.php?script=sci_arttext&pid=S2238-10312014000400010"""
        solution = {'tour': [], 'distance': 0, 'iteration': 0}
        # initial solution starting at 0
        solution['tour'] = randomize_tour(len(self.data))
        solution['distance'] = self.calculate_tour_distance(solution['tour'])

        solution = self.local_search_wrapper(solution)
        solution['iteration'] = 1
        solution['runtime'] = datetime.now() - start_timestamp
        self.solutions.append(solution)
        self.iterations += 1

        for i in range(1, iteration_limit):
            new_solution = self.perturbation(solution)
            new_solution = self.local_search_wrapper(new_solution)
            if new_solution['distance'] < solution['distance']:
                solution = new_solution
                solution['iteration'] = i + 1
                solution['runtime'] = datetime.now() - start_timestamp
            self.solutions.append(new_solution)
            self.iterations += 1
        return solution

    def get_edge_list(self, tour):
        # create all edges as tuples beginning at 0 and ending at 0
        edges = [(tour[i], tour[i + 1]) for i in range(0, len(tour) - 1)]
        edges.append((tour[len(tour) - 1], tour[0]))
        return edges

    def calculate_tour_distance(self, tour):
        edges = self.get_edge_list(tour)
        distance = 0
        for a, b in edges:
            distance += self.dist_matrix[a, b]
        return distance

    def local_search_wrapper(self, solution):
        """this wrapper is used to change local search mode"""
        if not self.alternative:
            return self.local_search(solution)
        else:
            return self.local_search_alt(solution, self.idle_limit)

    def local_search(self, solution):
        local_opt = solution
        for a, b in combinations(range(len(solution['tour'])), 2):
            if abs(a-b) in (1, len(solution['tour'])-1):
                continue
            tour = self.stochastic_two_opt(solution['tour'], a, b)
            distance = self.calculate_tour_distance(tour)
            if distance < local_opt['distance']:
                local_opt['tour'] = tour
                local_opt['distance'] = distance

        return local_opt

    def local_search_alt(self, solution, idle_limit):
        idle_counter = 0

        while idle_counter < idle_limit:
            tour = self.stochastic_two_opt_random(solution['tour'])
            distance = self.calculate_tour_distance(tour)
            if distance < solution['distance']:
                idle_counter = 0
                solution['tour'] = tour
                solution['distance'] = distance
            else:
                idle_counter += 1
        return solution

    def stochastic_two_opt(self, tour, c1, c2):
        """Delete 2 Edges and reverse everything between them
        Source: http://www.cleveralgorithms.com/nature-inspired/stochastic/iterated_local_search.html"""
        tour = tour[:]
        # make sure c1 < c2
        if c2 < c1:
            c1, c2 = c2, c1
        rev = tour[c1:c2]
        rev.reverse()
        tour[c1:c2] = rev
        tour.reverse()
        return tour

    def stochastic_two_opt_random(self, tour):
        """2-opt by randomly selecting 2 points"""
        tour = tour[:]
        c1 = random.randint(0, len(tour))
        c2 = random.randint(0, len(tour))
        exclude = [c1]
        if c1 == 0:
            exclude.append(len(tour) - 1)
        else:
            exclude.append(c1 - 1)
        if c2 == len(tour) - 1:
            exclude.append(0)
        else:
            exclude.append(c1 + 1)

        while c2 in exclude:
            c2 = random.randint(0, len(tour))

        # make sure c1 < c2
        if c2 < c1:
            c1, c2 = c2, c1
        rev = tour[c1:c2]
        rev.reverse()
        tour[c1:c2] = rev
        tour.reverse()
        return tour

    def perturbation(self, solution):
        new_solution = {}
        new_solution['tour'] = self.double_bridge_move(solution['tour'])
        new_solution['distance'] = self.calculate_tour_distance(new_solution['tour'])
        return new_solution

    def double_bridge_move(self, tour):
        """Split tour in 4 and reorder them.
        (a,b,c,d) --> (a,d,c,b)
        Source: https://www.comp.nus.edu.sg/~stevenha/database/viz/TSP_ILS.cpp"""
        pos1 = 1 + random.randint(0, len(tour) / 4)
        pos2 = pos1 + 1 + random.randint(0, len(tour) / 4)
        pos3 = pos2 + 1 + random.randint(0, len(tour) / 4)
        return tour[0:pos1] + tour[pos3:] + tour[pos2:pos3] + tour[pos1:pos2]
