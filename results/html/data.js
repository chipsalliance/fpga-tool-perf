var data = { {%- for project, name in var_name.items() %}
	"{{project}}": data_{{name}},
{%- endfor %}
}
