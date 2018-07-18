# goal: run all projects with valid .pcf

prefix=pcf_test

./exhaust.sh --out-prefix $prefix --device lp8k --package cm81 --pcf project/oneblink_lp8k-cm81.pcf --project oneblink

# wrapper based
for project in picorv32-wrap picosoc-simpleuart-wrap picosoc-spimemio-wrap picosoc-wrap vexriscv-verilog ; do
    ./exhaust.sh --out-prefix $prefix --device lp8k --package cm81 --pcf project/wrap_lp8k-cm81.pcf --project $project
done

# special with its own .pcf
./exhaust.sh --out-prefix $prefix --device hx8k --package cm81 --pcf project/picosoc-hx8kdemo-hx8k-ct256.pcf --project picosoc-hx8kdemo

