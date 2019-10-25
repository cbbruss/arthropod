"""
"""
import json
import requests
import time
from typing import List
from collections import Counter
import numpy as np

from src.graph_embeddings import api_config


class MalwareGraph(object):

    def __init__(self, path_to_edge_file, num_nodes=50):
        self.path_to_edge_file = path_to_edge_file
        self.responses = []
        self.scanned_nodes = []
        self._generate_edge_lists(num_nodes)

    def get_vt_attributes(self, path_to_scans=None):
        if path_to_scans:
            with open(path_to_scans) as f:
                self.responses = json.load(f)
            self.scanned_nodes = [x['resource'] for x in self.responses if x in self.files]
        else:
            path_to_scans = 'VT_Scans.json'

        url = 'https://www.virustotal.com/vtapi/v2/file/report'
        api_key = api_config.vt_api_key

        for node in self.files:
            if node not in self.scanned_nodes:
                params = {'apikey': api_key, 'resource': node, 'allinfo': 'true'}
                response = requests.get(url, params=params)

                if response.status_code == 204:
                    time.sleep(60)
                    response = requests.get(url, params=params)
                self.scanned_nodes.append(node)
                self.responses.append(response.json())

        with open(path_to_scans, 'w', encoding='utf-8') as f:
            json.dump(self.responses, f, ensure_ascii=False, indent=4)

    def get_scan_dict(self):
        kas_dict = {}
        sym_dict = {}
        responses_with_labels = []
        labeled_nodes = []
        for scan, node in zip(self.responses, self.scanned_nodes):
            if 'scans' in scan:
                kaspersky = scan['scans'].get('Kaspersky')
                symantec = scan['scans'].get('Symantec')
                if kaspersky:
                    k_result = kaspersky['result']
                else:
                    k_result = None
                kas_dict[node] = k_result
                if symantec:
                    s_result = symantec['result']
                else:
                    s_result = None
                sym_dict[node] = s_result
                if k_result or s_result:
                    responses_with_labels.append(scan)
                    labeled_nodes.append(node)
        return kas_dict, sym_dict, responses_with_labels, labeled_nodes

    def compute_numeric_features(self, responses_with_labels, num_sections=10):
        top_sections = self._get_top_sections(responses_with_labels, num_sections)

        numeric_node_feats = {}

        for response in responses_with_labels:
            node_features = np.zeros((len(top_sections) + 1) * 4)
            if 'additional_info' in response:
                if 'exiftool' in response['additional_info']:
                    exif = response['additional_info']['exiftool']
                    uds = exif.get('UninitializedDataSize', 0)
                    cs = exif.get('CodeSize', 0)
                    ids = exif.get('InitializedDataSize', 0)
                    node_features[0] = uds
                    node_features[1] = cs
                    node_features[2] = ids
                if 'sections' in response['additional_info']:
                    section_data = np.zeros((len(top_sections), 4))
                    sections = response['additional_info']['sections']
                    num_sections = len(sections)
                    for sect in sections:
                        if sect[0] in top_sections:
                            section_data[top_sections.index(sect[0])] = sect[1:5]
                    section_data = section_data.reshape(len(top_sections) * 4, )
                    node_features[4:] = section_data
            numeric_node_feats[response['resource']]=node_features
        return numeric_node_feats

    def _get_top_sections(self, responses_with_labels, num_sections):
        section_counter = Counter()
        for response in responses_with_labels:
            if 'additional_info' in response:
                if 'sections' in response['additional_info']:
                    sections = response['additional_info']['sections']
                    section_counter.update([x[0] for x in sections])
        top_sections = [x[0] for x in section_counter.most_common(num_sections)]
        return top_sections

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
