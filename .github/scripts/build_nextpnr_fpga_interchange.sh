#!/bin/bash

echo '::group::Installing dependencies'
export DEBIAN_FRONTEND=noninteractive
apt update -qq
apt install -y --no-install-recommends \
    ca-certificates \
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
echo '::endgroup::'

echo '::group::Updating CA certificates'
update-ca-certificates
echo '::endgroup::'

echo '::group::Building nextpnr-fpga_interchange'
if [ "$1" == "no_threads" ]; then
THREADS="-DUSE_THREADS=OFF"
fi
cd ./third_party/nextpnr
cmake . ${THREADS} -DARCH=fpga_interchange -DRAPIDWRIGHT_PATH=`realpath ../RapidWright` -DINTERCHANGE_SCHEMA_PATH=`realpath ../fpga-interchange-schema`
make
echo '::endgroup::'
