# Build sockshop base image

This folder contains scripts for building the base image used in the sockshop experiment.

## Prerequisite

[Packer](https://www.packer.io/) is a automated image building tool developed by HashiCorp. You need to have Packer installed in order to run the build script. To install Packer, follow the following instructions:

1. Download the latest version from https://www.packer.io/downloads.html.

2. Extract the prebuilt binary.

3. Copy the extracted binary under `/usr/local/packer/`. 

   > In fact this binary can be put anywhere on your system, but `/usr/local/packer/` is the path assumed in the build script (`run.sh`). If you want to put the binary in a different place please change `run.sh` accordingly.

4. Test your install using `/usr/local/packer/packer -v`. This command should output the version of the installed Packer.

For much information, refer to the official documentation of Packer: https://www.packer.io/docs/install/index.html.

## Build

`run.sh` will run the whole building process. See the comments in `run.sh` for more detail. After building completed the built image is at `output-qemu/sockshop-base` and the format is `qcow2`.

