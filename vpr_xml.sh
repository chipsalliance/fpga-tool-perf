set -ex

if [ '!' -d "$SFAD_DIR" ] ; then
    echo "SFAD_DIR invalid. Expect symbiflow-arch-defs directory"
    exit 1
fi

cd $SFAD_DIR/ice40/tests/blink || cd $SFAD_DIR/tests/ice40/blink

# tim: maybe run make route instead of bit

# hx1k (about 3 min on carbon x1)
make BOARD=icestick bit
# hx8k (about 15 min on carbon x1)
make BOARD=tinyfpga-b2 bit

# up5k
touch test-upk5-uwg30.pcf
make BOARD=test-upk5-uwg30 DEVICE=up5k PACKAGE=uwg30 PROG_TOOL=/dev/null bit

