usage() {
    echo "Exhaustively run all projects with valid .pcf"
    echo "usage: pcf_test.sh"
    echo "--out-prefix <dir>        output directory prefix (default: build)"
}

prefix=pcf_test

ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
    --out-prefix)
        prefix=$2
        shift
        shift
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Unrecognized argument"
        usage
        exit 1
        ;;
    esac
done

# Verify all projects are covered
if [ "$(python3 fpgaperf.py --list-projects |md5sum |cut -d ' '  -f 1)" != "ac6dcfea606f706dacd27e07d1b77170" ] ; then
    echo "Unexpected project list"
    exit 1
fi

# TODO: change to case loop
# for project in $(python3 fpgaperf.py --list-projects) ; do
# case "$project" in

./exhaust.sh --out-prefix $prefix --device lp8k --package cm81 --pcf project/oneblink_lp8k-cm81.pcf --project oneblink

# wrapper based
for project in picorv32-wrap picosoc-simpleuart-wrap picosoc-spimemio-wrap picosoc-wrap vexriscv-verilog ; do
    ./exhaust.sh --out-prefix $prefix --device lp8k --package cm81 --pcf project/wrap_lp8k-cm81.pcf --project $project
done

# special with its own .pcf
./exhaust.sh --out-prefix $prefix --device hx8k --package cm81 --pcf project/picosoc-hx8kdemo-hx8k-ct256.pcf --project picosoc-hx8kdemo

