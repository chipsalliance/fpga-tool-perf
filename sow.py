#!/usr/bin/env python3

import json


def merge(a, b):
    for key in b:
        if key in a:
            a[key].append(b[key])
        else:
            a[key] = [b[key]]
    return a


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Merge B json file into A json file'
    )
    parser.add_argument('fn_a', help='A json file')
    parser.add_argument('fn_b', help='B json file')
    args = parser.parse_args()

    fa = open(args.fn_a, 'r')
    fb = open(args.fn_b, 'r')
    ja = json.load(fa)
    jb = json.load(fb)
    fa.close()
    fb.close()

    # Merge b into a
    ja = merge(ja, jb)

    # Truncate file and write merged json
    fout = open(args.fn_a, 'w')
    json.dump(merged_dict, fout)


if __name__ == '__main__':
    main()
