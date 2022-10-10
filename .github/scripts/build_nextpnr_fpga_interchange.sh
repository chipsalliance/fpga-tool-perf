#!/bin/bash

echo Building nextpnr-fpga_interchange-experimental
    
echo Installing dependencies
export DEBIAN_FRONTEND=noninteractive
apt update -qq
apt install -y --no-install-recommends \
    python3-dev \
    libboost-dev \
    libboost-filesystem-dev \
    libboost-thread-dev \
    libboost-program-options-dev \
    libboost-iostreams-dev \
    libboost-dev \
    libeigen3-dev \
    capnproto \
    libcapnp-dev \
    build-essential \
    tcl8.6-dev \
    cmake
cp ./third_party/capnproto-java/compiler/src/main/schema/capnp/java.capnp /usr/include/capnp/java.capnp
    
echo Building nextpnr-fpga_interchange
cd ./third_party/nextpnr
cmake . -DARCH=fpga_interchange -DRAPIDWRIGHT_PATH=./third_party/RapidWright -DINTERCHANGE_SCHEMA_PATH=./third_party/fpga-interchange-schema
make

echo Installing nextpnr-fpga_interchange-experimental
cp ./third_party/nextpnr/nextpnr-fpga_interchange /usr/bin/nextpnr-fpga_interchange-experimental
