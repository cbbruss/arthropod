"""
"""
import json
import requests
import time
from typing import List

from src.graph_embeddings import api_config


class MalwareGraph(object):

    def __init__(self, path_to_edge_file, num_nodes=50):
        self.path_to_edge_file = path_to_edge_file
        self.response = []
        self.scanned_nodes = []
        self._generate_edge_lists(num_nodes)

    def get_vt_attributes(self, path_to_scans=None):
        if path_to_scans:
            with open(path_to_scans) as f:
                self.responses = json.load(f)
            self.scanned_nodes = [x['resource'] for x in self.responses]
        else:
            path_to_scans = 'VT_Scans.json'

        url = 'https://www.virustotal.com/vtapi/v2/file/report'
        api_key = api_config.vt_api_key

        for node in self.files:
            if node not in self.scanned_nodes:
                params = {'apikey': api_key, 'resource': node}
                response = requests.get(url, params=params)

                if response.status_code == 204:
                    time.sleep(60)
                    response = requests.get(url, params=params)
                self.scanned_nodes.append(node)
                self.responses.append(response.json())

        with open(path_to_scans, 'w', encoding='utf-8') as f:
            json.dump(self.responses, f, ensure_ascii=False, indent=4)

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
