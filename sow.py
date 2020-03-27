#!/usr/bin/env python3

import json

merged_dict = {}

class display(object):
    """Display HTML representation of multiple objects"""
    template = """<div style="float: left; padding: 10px;">
    <p style='font-family:"Courier New", Courier, monospace'>{0}</p>{1}
    </div>"""
    def __init__(self, *args):
        self.args = args

    def _repr_html_(self):
        return '\n'.join(self.template.format(a, eval(a)._repr_html_())
                                                    for a in self.args)
                                
    def __repr__(self):
        return '\n\n'.join(a + '\n' + repr(eval(a))
                                for a in self.args)

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            a[key].append(b[key])
        else:
            a[key] = [b[key]]
    return a

def run(fin, fout, verbose=False):
    jsons = fin.read().split()
    for js in jsons:
        input_dict = json.load(open(js))
        merge(merged_dict, input_dict)

    json.dump(merged_dict, fout)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Process multiple .json seed rows into min/max rows'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('fn_in', help='')
    parser.add_argument('fn_out', help='')
    args = parser.parse_args()

    run(open(args.fn_in, 'r'), open(args.fn_out, 'w'), verbose=args.verbose)


if __name__ == '__main__':
    main()
