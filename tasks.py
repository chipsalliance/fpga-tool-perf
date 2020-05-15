#!/usr/bin/env python3

import os
from itertools import product

from fpgaperf import get_projects, get_toolchains


def get_device_info(constraint):
    """Returns the device information:
        - FPGA family
        - FPGA part
        - board
    """
    full_info, extension = os.path.splitext(constraint)
    return full_info.split('_') + [extension.lstrip('.')]


class Tasks:
    """Class to generate and hold the task lists that needs to be run
    exhaustively by FPGA tool perf."""
    def __init__(self, src_dir):
        self.src_dir = src_dir
        self.MANDATORY_CONSTRAINTS = {
            "vivado": "xdc",
            "vpr": "pcf",
            "vivado-yosys": "xdc",
            "nextpnr": "xdc",
        }

        self.tasks = self.iter_options()

    def iter_options(self):
        """Returns all the possible combination of:
            - projects,
            - toolchains,
            - families,
            - devices,
            - packages
            - boards.

        Example:
        - path structure:    src/<project>/<toolchain>/<family>_<device>_<package>_<board>.<constraint>
        - valid combination: src/oneblink/vpr/xc7_a35t_csg324-1_arty.pcf
        """

        projects = get_projects()
        toolchains = get_toolchains()

        combinations = set()
        for project, toolchain in list(product(projects, toolchains)):
            constraint_path = os.path.join(
                self.src_dir, project, 'constr', toolchain
            )

            if toolchain not in self.MANDATORY_CONSTRAINTS.keys():
                continue

            if not os.path.exists(constraint_path):
                continue

            for constraint in os.listdir(constraint_path):
                family, device, package, board, extension = get_device_info(
                    constraint
                )

                if extension not in self.MANDATORY_CONSTRAINTS[toolchain]:
                    continue

                combinations.add(
                    (project, toolchain, family, device, package, board)
                )

        return combinations

    def get_tasks(self, args):
        """Returns all the tasks filtering out the ones that do not correspond
        to the selected criteria"""

        tasks = []

        for task in self.tasks:
            take_task = True
            for arg in args.values():
                if arg is None:
                    continue

                if not any(value in arg for value in task):
                    take_task = False
                    break

            if take_task:
                tasks.append(task)

        return tasks
