"""
"""
from typing import List


class EdgeList(object):

    def __init__(self, path_to_edge_file, num_nodes=50):
        self.path_to_edge_file = path_to_edge_file
        self._generate_edge_lists(num_nodes)


    def _generate_edge_lists(self, num_nodes):
        self.file_dlls = []
        self.file_dlls = []
        self.func_dlls = []
        self.file_funcs = []
        self.files = []
        self.funcs = []
        self.dlls = []

        with open(self.path_to_edge_file) as file:
            for line in file:
                line_split = line.split(",")
                if len(line_split) == 4 and line_split[3] == ' "NAME"\n':
                    line_split = [x.strip() for x in line_split]
                    line_split = [x.strip('"') for x in line_split]
                    file, dll, func = line_split[0:3]
                    func = "{}_{}".format(dll, func)
                    
                    if len(self.files) < num_nodes:
                        self.file_dlls.append((file, dll))
                        self.func_dlls.append((func, dll))
                        self.file_funcs.append((file, func))

                        if file not in self.files:
                            self.files.append(file)

                        if dll not in self.dlls:
                            self.dlls.append(dll)

                        if func not in self.funcs:
                            self.funcs.append(func)
        self.file_dlls = list(set(self.file_dlls))
        self.func_dlls = list(set(self.func_dlls))
        self.file_funcs = list(set(self.file_funcs))

# class NodeAttributes(object):
