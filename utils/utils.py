def get_columns(df):
  return ", ".join(df.columns)

def get_designs_list(df):
  return sorted(set(df.loc[:,'design']))

def get_project_data(df, column, callback, project=None):
  project_df = df.set_index('project')

  projects = [project] if project else get_project_list(df)

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

def resource_utilization_callback(data):
  element = dict()
  element['resources'] = dict()

  for k, v in data.items():
    element['resources'][k] = v

  return element


def max_freq_callback(data):
  element = dict()
  element['max_freq'] = dict()

  if type(data) is float:
    element['max_freq'] = ("%0.3f MHz" % (data / 1e6))
  elif type(data) is dict:
    for cd in data:
      element['max_freq']['actual'] = "%0.3f MHz" % (data[cd]['actual'] / 1e6)
      element['max_freq']['requested'] = "%0.3f MHz" % (data[cd]['requested'] / 1e6)
      element['max_freq']['met'] = data[cd]['met']
      element['max_freq']['s_violation'] = ("%0.3f ns" % data[cd]['setup_violation'])
      element['max_freq']['h_violation'] = ("%0.3f ns" % data[cd]['hold_violation'])

  return element
