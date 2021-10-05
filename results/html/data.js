
var data = { {% for project, device_data in devices_data.items() %}
    "{{ project }}": { {% for device, data in device_data.items() %}
        "{{ device }}": {
            "dates": {{ data["dates"] }},
            "runtime": [{% for toolchain, graph_data in data["graph_data"].items() %}
                {
                    "data": {{ graph_data["runtime"]["total"]['data'] }},
                    "label": "{{ toolchain }}",
                    "borderColor": "{{ graph_data["runtime"]['total']['color'] }}",
                    "fill": false
                },{% endfor %}
            ],
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
            "resources": { {% for res in data["resources"] %}
                "{{ res|lower }}": [{% for toolchain, graph_data in data["graph_data"].items() %}
                    {
                        "data": {{ graph_data["resources"][res|lower]['data'] }},
                        "label": "{{ toolchain }}",
                        "borderColor": "{{ graph_data["resources"][res|lower]['color'] }}",
                        "fill": false
                    },{% endfor %}
                ],{% endfor %}
            },
        },{% endfor %}
    },{% endfor %}
}
