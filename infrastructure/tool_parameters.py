#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import itertools
import os
import yaml


class ToolParametersHelper:
    def __init__(self, toolchain, params_file='params.yaml'):
        self.params_path = os.path.join(
            os.getcwd(), 'tool_parameters', toolchain, params_file
        )
        self.params = None

        assert os.path.exists(
            self.params_path
        ), "Parameters file {} does not exist.".format(self.params_path)

        with open(self.params_path, 'r') as params_file:
            self.params = yaml.safe_load(params_file)

    def get_all_params_combinations(self):
        all_params = []

        param_prefix = self.params['param_prefix']

        for param, values in self.params['params'].items():
            param_combinations = []

            for value in values:
                param_combinations.append(
                    "{}{} {}".format(param_prefix, param, value)
                )

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
