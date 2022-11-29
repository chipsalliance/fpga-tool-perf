var data_{{var_name}} = { {% for device, data in device_data.items() %}
    "{{ device }}": {
        "dates": {{ data["dates"] }},
        "runtime": { {% for runtime in data["runtime"] %}
            "{{ runtime }}": [{% for toolchain, graph_data in data["graph_data"].items() %}
                {
                    "data": {{ graph_data["runtime"][runtime]['data'] }},
                    "label": "{{ toolchain }}",
                    "borderColor": "{{ graph_data["runtime"][runtime]['color'] }}",
                    "fill": false
                },{% endfor %}
            ],{% endfor %}
        },
        "wirelength": [{% for toolchain, graph_data in data["graph_data"].items() %}
            {
                "data": {{ graph_data["wirelength"]['data'] }},
                "label": "{{ toolchain }}",
                "borderColor": "{{ graph_data["wirelength"]['color'] }}",
                "fill": false
            },{% endfor %}
        ],
        "memory": [{% for toolchain, graph_data in data["graph_data"].items() %}
            {
                "data": {{ graph_data["maximum_memory_use"]['data'] }},
                "label": "{{ toolchain }}",
                "borderColor": "{{ graph_data["maximum_memory_use"]['color'] }}",
                "fill": false
            },{% endfor %}
        ],
        "freq": { {% for clock in data["clocks"] %}
            "{{ clock }}": [{% for toolchain, graph_data in data["graph_data"].items() %}
                {
                    "data": {{ graph_data["freq"][clock]['data'] }},
                    "label": "{{ toolchain }}",
                    "borderColor": "{{ graph_data["freq"][clock]['color'] }}",
                    "fill": false
                },{% endfor %}
            ],{% endfor %}
        },
        "synth_resources": { {% for res in data["resources"] %}
            "{{ res|lower }}": [{% for toolchain, graph_data in data["graph_data"].items() %}
                {
                    "data": {{ graph_data["synth_resources"][res|lower]['data'] }},
                    "label": "{{ toolchain }}",
                    "borderColor": "{{ graph_data["synth_resources"][res|lower]['color'] }}",
                    "fill": false
                },{% endfor %}
            ],{% endfor %}
        },
        "impl_resources": { {% for res in data["resources"] %}
            "{{ res|lower }}": [{% for toolchain, graph_data in data["graph_data"].items() %}
                {
                    "data": {{ graph_data["impl_resources"][res|lower]['data'] }},
                    "label": "{{ toolchain }}",
                    "borderColor": "{{ graph_data["impl_resources"][res|lower]['color'] }}",
                    "fill": false
                },{% endfor %}
            ],{% endfor %}
        },
    },{% endfor %}
}
