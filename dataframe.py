#!/usr/bin/env python3

import pandas


def get_clock_dataframe(results):
    designs = []

    # Clock-related lists
    actual_frequency = []
    requested_frequency = []
    hold_violation = []
    setup_violation = []
    clock_met = []
    clock_names = []

    for idx, design in enumerate(results['design']):
        clock = results['max_freq'][idx]
        if clock:
            for key, value in clock.items():
                designs.append(design)
                clock_names.append(key)
                actual_frequency.append(value['actual'] / 1e6)
                requested_frequency.append(value['requested'] / 1e6)
                hold_violation.append(value['hold_violation'])
                setup_violation.append(value['setup_violation'])
                clock_met.append(value['met'])
        else:
            designs.append(design)
            clock_names.append(None)
            actual_frequency.append(None)
            requested_frequency.append(None)
            hold_violation.append(None)
            setup_violation.append(None)
            clock_met.append(None)

    index = pandas.Index(designs)
    return pandas.DataFrame(
        {
            'clock_names': clock_names,
            'clock_actual_frequency': actual_frequency,
            'clock_requested_frequency': requested_frequency,
            'clock_hold_violation': hold_violation,
            'clock_setup_violation': setup_violation,
            'clock_met': clock_met,
        },
        index=index
    )


def get_general_dataframe(results):
    designs = results['design']

    # Get runtimes
    runtimes = dict()
    for runtime in results['runtime']:
        if not runtimes:
            runtimes = {k: [] for k in runtime.keys()}

        for k, v in runtime.items():
            runtimes[k].append(v)

    runtimes_keys = list(runtimes.keys())
    for key in runtimes_keys:
        runtimes["{}_time".format(key)] = runtimes.pop(key)

    # Get resources
    resources = dict()
    for resource in results['resources']:
        if not resources:
            resources = {k: [] for k in resource.keys()}

        for k, v in resource.items():
            resources[k].append(v)

    resources_keys = list(resources.keys())
    for key in resources_keys:
        resources["{}_utilization".format(key)] = resources.pop(key)

    # Get versions
    tools = dict()
    # Initialize versions dictionary with all possible
    # versions of the tools.
    for version in results['versions']:
        for key in version:
            tools[key] = []

    for version in results['versions']:
        for k, v in version.items():
            tools[k].append(v)

        for k in version.keys() ^ tools.keys():
            tools[k].append(None)

    tools_keys = list(tools.keys())
    for key in tools_keys:
        tools["{}_version".format(key)] = tools.pop(key)

    ALREADY_PARSED_KEYS = ['versions', 'max_freq', 'runtime', 'resources']
    general_data = {
        k: results[k]
        for k in results.keys() ^ ALREADY_PARSED_KEYS
    }

    data = {**runtimes, **resources, **general_data, **tools}
    index = pandas.Index(designs)
    return pandas.DataFrame(data, index)


def generate_dataframe(results):
    clock_df = get_clock_dataframe(results)

    general_df = get_general_dataframe(results)

    df = general_df.join(clock_df, how="left")

    return df
