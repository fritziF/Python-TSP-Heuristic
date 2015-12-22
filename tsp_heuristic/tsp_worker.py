import re
from collections import OrderedDict
import numpy


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
        data_reg = re.compile(r"\s*\d+\s*([\d.]+)?\s*([\d.]+)?")
        for line in file_content[6:]:
            if "EOF" in line or not line.strip():
                break
            match = re.match(data_reg, line.strip())
            self.data.append((float(match.group(1).strip()),
                              float(match.group(2).strip())))

    def set_max_values(self):
        """this was intended for normalizing graph, but not needed"""
        self.max_x = max([x for x, y in self.data])
        self.max_y = max([y for x, y in self.data])

    def calc_dist_matrix(self):
        z = numpy.array([[complex(x, y) for x, y in self.data]])
        return numpy.round(abs(z.T-z), NUMPY_PRECISION)

    def solve_tsp(self):
        #dummy tsp for graph
        dummy = [(i, i+1) for i in range(0, len(self.data) - 1)]
        dummy.append((len(self.data) - 1, 0))
        return dummy


    def __str__(self):
        return '\n'.join([' : '.join((k, str(self.meta[k]))) for k in self.problem])


