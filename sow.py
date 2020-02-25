#!/usr/bin/env python3


def run(fin, fout, verbose=False):
    row = fin.readline().strip()
    seedpos = row.split(',').index('Seed')
    fout.write(row + '\n')

    lines_raw = {}
    nlines = 0
    # Aggregate when all that differs is the seed
    #Family,Device,Package,Project,Toolchain,Strategy,Seed,Freq (MHz),Build (sec),#LUT,#DFF,#BRAM,#CARRY,#GLB,#PLL,#IOB
    for l in fin:
        nlines += 1
        parts = l.strip().split(',')
        # key: Family,Device,Package,Project,Toolchain,Strategy
        key = parts[0:seedpos]
        lines_raw.setdefault(tuple(key), []).append(parts)

    # Now aggregate any keys that appear twice (multiple seeds
    lines_out = []
    for k, vs in lines_raw.items():
        if len(vs) == 1:
            lines_out.append(vs[0])
            continue
        # Create two lines: one min line and one max line
        # Resources are a bit misleading...oh well
        minstate = []
        maxstate = []
        cols = len(vs[0])
        for i in xrange(seedpos + 1, cols):
            minstate.append(min([v[i] for v in vs]))
            maxstate.append(max([v[i] for v in vs]))
        lines_out.append(list(k) + ['min'] + minstate)
        lines_out.append(list(k) + ['max'] + maxstate)

    print('%u lines in => %u lines out' % (nlines, len(lines_out)))
    for l in sorted(lines_out):
        fout.write(','.join(l) + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Process multiple .csv seed rows into min/max rows'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('fn_in', help='')
    parser.add_argument('fn_out', help='')
    args = parser.parse_args()

    run(open(args.fn_in, 'r'), open(args.fn_out, 'w'), verbose=args.verbose)


if __name__ == '__main__':
    main()
