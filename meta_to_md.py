import os







def main():
    import argparse

    print("Parsing Arguments......")
    parser = argparse.ArgumentParser(
        description=
        'compare two runs through MarkDown tables'
    )

    parser.add_argument(
        '--file1', default=None, help='Use custom tool parameters'
    )
    parser.add_argument(
        '--file2', default=None, help='Use custom tool parameters'
    )
    args = parser.parse_args()

    if args.file1:
        file1="/home/student/fpga-tool-perf/build/{file1}/meta.json"
        print("\nFirst file is .....")

if __name__ == '__main__':
    main()