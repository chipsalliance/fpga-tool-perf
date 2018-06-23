rm -rf build

python3 main.py --toolchain arachne --project blinky
python3 main.py --toolchain vpr --project blinky

python3 main.py --toolchain arachne --project picosoc-hx8kdemo --verbose
# SB_IO issue
# python3 main.py --toolchain vpr --project picosoc-hx8kdemo --verbose


