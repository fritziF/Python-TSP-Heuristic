import re
from collections import OrderedDict
import numpy
import matplotlib.pyplot as plt
import networkx as nx

NUMPY_PRECISION = 2
#numpy.set_printoptions(precision=NUMPY_PRECISION)


class Problem:
    def __init__(self, file_path):
        self.meta = OrderedDict()
        self.data = []
        self.max_x = None
        self.max_y = None

        with open(file_path, 'r') as f:
            file_content = f.readlines()

        self.read_meta(file_content)
        self.read_data(file_content)
        self.set_max_values()

    def read_meta(self, file_content):
        meta_reg = re.compile(r"(.*):(.*)")
        for line in file_content[:5]:
            match = re.match(meta_reg, line.lower().strip())
            self.meta[match.group(1).strip()] = match.group(2).strip()

    def read_data(self, file_content):
        data_reg = re.compile(r".* (.*) (.*)")
        for line in file_content[6:]:
            if "EOF" in line or not line.strip():
                break
            match = re.match(data_reg, line.strip())
            self.data.append((float(match.group(1)), float(match.group(2))))

    def set_max_values(self):
        self.max_x = max([x for x, y in self.data])
        self.max_y = max([y for x, y in self.data])

    def calc_dist_matrix(self):
        z = numpy.array([[complex(x, y) for x, y in self.data]])
        return numpy.round(abs(z.T-z), NUMPY_PRECISION)

    def __str__(self):
        return '\n'.join([' : '.join((k, str(self.meta[k]))) for k in self.problem])


if __name__ == "__main__":
    file_path = "../problems/berlin52.tsp"

    problem = Problem(file_path)

    calc_matrix = problem.calc_dist_matrix()

    G = nx.DiGraph()
    G.add_nodes_from(range(0, len(problem.data)))
    G.add_edges_from([(0, 6), (6, 20), (20, 0)])
    nx.draw_networkx_nodes(G, problem.data, node_size=20, node_color='k')
    nx.draw_networkx_edges(G, problem.data, width=0.5, arrows=True, edge_color='r')


    #plt.scatter(*zip(*problem.data), s=10)
    #plt.plot(*zip(*problem.data), color='#bebfcc', linewidth=0.5)
    plt.title(problem.meta['name'])
    plt.xlim(0)
    plt.ylim(0)
    plt.xlabel('X-Axis')
    plt.ylabel('Y-Axis')
    plt.show()


