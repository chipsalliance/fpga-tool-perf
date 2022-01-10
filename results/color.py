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

import math


def hsl_to_rgb(h: float, s: float, l: float):
    r, g, b = 0.0, 0.0, 0.0
    c = 1.0 - abs(2.0 * l - 1.0) * s
    j = h * 3.0 / math.pi
    x = c * (1.0 - abs(math.fmod(j, 2.0) - 1.0))
    cj = math.floor(j)
    if cj == 0:
        r = c
        g = x
        b = 0.0
    elif cj == 1:
        r = x
        g = c
        b = 0.0
    elif cj == 2:
        r = 0.0
        g = c
        b = x
    elif cj == 3:
        r = 0.0
        g = x
        b = c
    elif cj == 4:
        r = x
        g = 0.0
        b = c
    elif cj == 5:
        r = c
        g = 0.0
        b = x
    else:
        r = 0.0
        g = 0.0
        b = 0.0
    m = l - c * 0.5
    r += m
    g += m
    b += m

    return min(max(r, 0.0), 1.0), min(max(g, 0.0), 1.0), min(max(b, 0.0), 1.0)


def rgb_to_hex(r, g, b):
    return '#' + \
           format(math.ceil(r * 255.0), '02x') + \
           format(math.ceil(g * 255.0), '02x') + \
           format(math.ceil(b * 255.0), '02x')
