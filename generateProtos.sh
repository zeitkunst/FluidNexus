#!/bin/bash

SRC_DIR="FluidNexus"

protoc -I=$SRC_DIR --python_out=$SRC_DIR $SRC_DIR/FluidNexus.proto
protoc -I=$SRC_DIR --java_out=../FluidNexusAndroid/src $SRC_DIR/FluidNexus.proto

