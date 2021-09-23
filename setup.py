#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:	ISC

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fpga-tool-perf",
    version="0.0.1",
    entry_points={
        "console_scripts":
            [
                "fpga-tool-perf-exhaust=exhaust:main",
                "fpga-tool-perf=fpgaperf:main"
            ]
    },
    author="SymbiFlow Authors",
    author_email="symbiflow@lists.librecores.org",
    description="Python library to run FPGA benchmarks on various toolchains",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/SymbiFlow/fpga-tool-perf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License",
        "Operating System :: OS Independent",
    ],
)
