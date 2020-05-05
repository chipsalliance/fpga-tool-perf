class DataFrame(object):
    """Holds helper functions to query the data frame containing
    the results of a run."""
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_columns(self):
        return self.dataframe.columns

    def get_designs_list(self):
        return sorted(set(self.dataframe.loc[:, 'project']))

    def get_project_data(self, column, callback, project=None):
        project_df = self.dataframe.set_index('project')

        projects = [project] if project else get_project_list(self.dataframe)

        data = dict()

        for prj in projects:
            data[prj] = dict()
            prj_data = project_df.loc[prj, ['toolchain', 'board', column]]

            for idx, row_data in prj_data.iterrows():
                board = row_data['board']
                if board not in data[prj].keys():
                    data[prj][board] = []

                element = callback(row_data[column])
                element['toolchain'] = row_data['toolchain']

                data[prj][board].append(element)

        return data

    def get_runtime(self, project=None):
        def runtime_callback(data):
            element = dict()
            element['runtime'] = dict()

            for k, v in data.items():
                if type(v) == type(dict()):
                    for k1, v1 in v.items():
                        element['runtime'][k1] = ("%0.3f" % v1)
                else:
                    element['runtime'][k] = ("%0.3f" % v)

            return element

        return self.get_project_data('runtime', runtime_callback, project)

    def get_resources(self, project=None):
        def resource_utilization_callback(data):
            element = dict()
            element['resources'] = dict()

            for k, v in data.items():
                element['resources'][k] = v

            return element

        return self.get_project_data(
            'resources', resource_utilization_callback, project
        )

    def get_max_freq(self, project=None):
        def max_freq_callback(data):
            element = dict()
            element['max_freq'] = dict()

            if type(data) is float:
                element['max_freq'] = ("%0.3f MHz" % (data / 1e6))
            elif type(data) is dict:
                for cd in data:
                    element['max_freq']['actual'] = "%0.3f MHz" % (
                        data[cd]['actual'] / 1e6
                    )
                    element['max_freq']['requested'] = "%0.3f MHz" % (
                        data[cd]['requested'] / 1e6
                    )
                    element['max_freq']['met'] = data[cd]['met']
                    element['max_freq']['s_violation'] = (
                        "%0.3f ns" % data[cd]['setup_violation']
                    )
                    element['max_freq']['h_violation'] = (
                        "%0.3f ns" % data[cd]['hold_violation']
                    )

            return element

        return self.get_project_data('max_freq', max_freq_callback, project)
