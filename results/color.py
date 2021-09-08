#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

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
