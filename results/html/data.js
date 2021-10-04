
var data = {
{% for project, device_data in devices_data.items() %}
    "{{ project }}": {
    {% for device, data in device_data.items() %}
        "{{ device }}": {
            "dates": {{ data["dates"] }},
            "runtime": [
            {% for toolchain, graph_data in data["graph_data"].items() %}
                {
                    "data": [{{ graph_data["runtime"]["total"]['data'] }}],
                    "label": "{{ device }}-{{ toolchain }}",
                    "borderColor": "{{ graph_data["runtime"]['total']['color'] }}",
                    "fill": false
                },
            {% endfor %}
            ],
        },
    {% endfor %}
    },
{% endfor %}
}
