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

run_project(){
    project=$1
    pcf_gen=$2
    pcf_rad=$3

    # command will fail on radiant
    ./exhaust.sh --out-prefix $prefix --device lp8k --package cm81 --pcf "$pcf_gen" --project "$project"
    # retry project with radiant in mind
    for toolchain in radiant-synpro radiant-lse ; do
        ./exhaust.sh --out-prefix $prefix --device up5k --package sg48 --pcf "$pcf_rad" --project "$project" --toolchain "$toolchain"
    done
}

run_project oneblink project/oneblink_lp8k-cm81.pcf project/oneblink_up5k-sg48.pcf

# wrapper based
for project in picorv32-wrap picosoc-simpleuart-wrap picosoc-spimemio-wrap picosoc-wrap vexriscv-verilog ; do
    run_project $project oneblink project/wrap_lp8k-cm81.pcf project/wrap_up5k-sg48.pcf
done

# special with its own .pcf
# currently no radiant version
./exhaust.sh --out-prefix $prefix --device hx8k --package cm81 --pcf project/picosoc-hx8kdemo-hx8k-ct256.pcf --project picosoc-hx8kdemo

