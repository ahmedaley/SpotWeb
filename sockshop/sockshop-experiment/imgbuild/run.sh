#!/usr/bin/env bash

# Remove cached cloud image
if [ -d packer_cache ]; then
    sudo rm -rf packer_cache/
fi

# Remove output folder from last build
if [ -d output-qemu ]; then
    sudo rm -rf output-qemu/
fi

# remove existing data disk image
if [ -f my-seed.img ]; then
    rm -f my-seed.img
fi

# Because we use the cloud image as the base image we need to provide a disk image containing
# user data/meta data to cloud-init, such as hostname, password, ssh authorized key, etc.
# For more information, refer to:
# 1. https://cloudinit.readthedocs.io/en/latest/topics/debugging.html?highlight=cloud-localds#analyze-quickstart-kvm
# 2. http://cloudinit.readthedocs.io/en/latest/topics/examples.html
cloud-localds my-seed.img user_data.yml

# sudo privilege is needed because KVM accelerator is used
sudo PACKER_LOG=1 /usr/local/packer/packer build sock-shop-base.json
