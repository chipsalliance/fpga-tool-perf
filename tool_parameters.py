#!/usr/bin/env python3

import os
import json
import itertools

class ToolParametersHelper:

    def __init__(self, toolchain, params_file='params.json'):
        self.params_path = os.path.join(os.getcwd(), 'tool_parameters', toolchain, params_file)
        self.params = None

        assert os.path.exists(self.params_path), "Parameters file {} does not exist.".format(params_file)

        with open(self.params_path, 'r') as params_file:
            self.params = json.load(params_file)

    def get_all_params_combinations(self):
        all_params = []

        param_prefix = self.params['param_prefix']

        for param, values in self.params['params'].items():
            param_combinations = []

            for value in values:
                param_combinations.append("{}{} {}".format(param_prefix, param, value))

            all_params.append(param_combinations)

        return list(itertools.product(*all_params))

    def add_param(self, param, values=[], overwrite=True):
        if param in self.params and overwrite:
            self.params[param] = values
        else:
            print("param {} cannot be overwritten.".format(param))

    def add_param_values(self, param, values=[]):
        old_values = self.params[param]
        new_values = list(set(old_values | values))
        self.add_params(param, new_values)

    def remove_param(self, param):
        self.params.pop(param, None)
