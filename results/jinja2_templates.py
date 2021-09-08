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

import jinja2

jinja2_datasets_template_str = """
    [
        {% for cfg in datasets %}
            {
                data: [ {{ datasets[cfg]["data"] }} ],
                label: "{{ cfg }}" ,
                borderColor: "{{ datasets[cfg]["color"] }}",
                fill: false
            },
        {% endfor %}
    ] """

jinja2_datasets_template: jinja2.Template = \
    jinja2.Template(jinja2_datasets_template_str,
                    trim_blocks=True, lstrip_blocks=True)


def gen_datasets_def(datasets):
    return jinja2_datasets_template.render(datasets=datasets)
