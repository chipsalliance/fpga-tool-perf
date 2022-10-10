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
    tcl8.6-dev \
    build-essential \
    cmake \
    wget
cp ./third_party/capnproto-java/compiler/src/main/schema/capnp/java.capnp /usr/include/capnp/java.capnp
    
echo Building nextpnr-fpga_interchange
cd ./third_party/nextpnr
cmake . -DARCH=fpga_interchange -DRAPIDWRIGHT_PATH=`realpath ../RapidWright` -DINTERCHANGE_SCHEMA_PATH=`realpath ../fpga-interchange-schema`
make

