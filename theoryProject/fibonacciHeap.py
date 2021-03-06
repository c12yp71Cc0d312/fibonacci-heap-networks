import math

class FibonacciTree:
    def __init__(self, pc_tuple):
        self.key = pc_tuple[0]
        self.connection_info = pc_tuple[1]
        self.children = []
        self.order = 0

    def add_at_end(self, t):
        self.children.append(t)
        self.order = self.order + 1


class FibonacciHeap:
    numOfElements = 0

    def __init__(self):
        self.trees = []
        self.least = None
        self.count = 0

    def insert(self, pc_tuple):
        new_tree = FibonacciTree(pc_tuple)
        self.trees.append(new_tree)
        if (self.least is None or pc_tuple[0] < self.least.key):
            self.least = new_tree
        self.count = self.count + 1

    def get_min(self):
        if self.least is None:
            return None

        # return self.least.key
        print(self.least.key)
        return self.least.connection_info

    def extract_min(self):
        smallest = self.least
        if smallest is not None:
            for child in smallest.children:
                self.trees.append(child)
            self.trees.remove(smallest)
            if self.trees == []:
                self.least = None
            else:
                self.least = self.trees[0]
                self.consolidate()
            self.count = self.count - 1

            # return smallest.key
            print(smallest.key)
            return smallest.connection_info

    def consolidate(self):
        aux = (floor_log2(self.count) + 1) * [None]

        while self.trees != []:
            x = self.trees[0]
            order = x.order
            self.trees.remove(x)
            while aux[order] is not None:
                y = aux[order]
                if x.key > y.key:
                    x, y = y, x
                x.add_at_end(y)
                aux[order] = None
                order = order + 1
            aux[order] = x

        self.least = None
        for k in aux:
            if k is not None:
                self.trees.append(k)
                if (self.least is None
                        or k.key < self.least.key):
                    self.least = k


def floor_log2(x):
    return math.frexp(x)[1] - 1


def perform_operation(**kwargs):

    fheap = kwargs.get('FHEAP')
    operation = kwargs.get('OPERATION')
    if operation == 'insert':
        pc_tuple = kwargs.get('PC_TUPLE')
        fheap.insert(pc_tuple)
        print(f'inserted priority {pc_tuple[0]}')

    elif operation == 'min get':
        minConInfo = fheap.get_min()
        print(f'Minimum value connection: {minConInfo}')
        return minConInfo

    elif operation == 'min extract':
        minConInfo = fheap.extract_min()
        print(f'Minimum value removed: {minConInfo}')
        return minConInfo

    else:
        print('invalid operation')
