# sockshop-experiment

This repo contains code and documentation for running *microservices demo* (sockshop) in a VM cluster.

## Build Base Image
First we need to build a base image for all our VMs. This base image is based on the [Ubuntu Cloud Images](https://cloud-images.ubuntu.com/) with the following stuff pre-deployed:

1. Install docker engine community edition.
2. Clone [our sockshop repo](https://github.com/Jerry-BinWang/microservices-demo) whcih is a fork of the [official sockshop repo](https://github.com/microservices-demo/microservices-demo).
3. Pull all the services of sockshop to decrease startup latency.

For more information about how to build the base image, refer to the [README.MD](https://github.com/Jerry-BinWang/sockshop-experiment/blob/master/imgbuild/README.MD) in the imgbuild folder.

## Generate VM domain definition files and disk files.

For each vm we will generate a libvrit domain definition file and two disk file (one base data disk and one cloud-init config drive). This is done in two steps: 1) define the machines we will be using in `conf.yml`, 2) using the `preprocess` program to generate the files.

### `conf.yml`
This file may look like this:
```
baseImg: "/home/binwang/sock-shop-experiment/imgbuild/output-qemu/sockshop_base"
basePath: "/home/binwang/sock-shop-experiment/temp"
VMs:
  - name: "manager"
    memory: 1024
    vcpu: 1
    address: "192.168.245.240"
  - name: "application"
    memory: 8192
    vcpu: 4
    address: "192.168.245.241"
  - name: "database"
    memory: 4096
    vcpu: 4
address: "192.168.245.242"
```
This file currently specifies the following things:

1. `baseImg`: the location of the base image file.
2. `basePath`: where should the generated domain definition files and disk files be put.
3. `VMs`: the name, vCPU count, memory size, and IP address (as we use bride [`Public Bridge`](http://www.linux-kvm.org/page/Networking#Public_Bridge) as the networking method) of each VM.

### `preprocess`
The `preprocess` program translates the `conf.yml` into domain definition files and disk files. To build this program, use
```
go build preprocess.go config.go
```
This requires 1) installing the golang environment, 2) setting up `GOPATH` environment variable, and 3) installing prerequisite packages (see the import section in `preprocess.go` and `config.go`). 

After building use `./preprocess` to generate the files.

## Start the VMs
Go to the location of the `basePath` specified in `conf.yml`. You should see several `.xml` files. Use `virsh create vmName.xml` to create the VM.

To run commands inside a VM, you can either use `virsh console vmName` or ssh to the VM IP address from the host.

## Setup docker swarm
First init `docker swarm` on the manager machine using
```
docker swarm init
```
The output should look like this
```
Swarm initialized: current node (x2nr20pjyiwe3bxey72xfrpfn) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-2lz7nr485d18lbyj4qxk9v7zarqixbu8huunxxcz2ub1ranjqw-6j5e9uz0vbtia0do2p7v0wwr2 192.168.245.240:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```
Then copy the command starting with `docker swarm join` from the out put and run it in the worker nodes. When done, run `docker node ls` in the manager to view all the nodes in the swarm.

## Assign label to the workers
Label are used to separate spot instances (which run stateless containers) and regular instances (which run stateful containers). 
```
docker node update --label-add role=application applicationVM
docker node update --label-add role=database databaseVM
```
Replace the `applicationVM` and `databaseVM` with the real VM name.

To list labels of nodes, refer to [this SO question](https://stackoverflow.com/questions/42414703/how-to-list-docker-swarm-nodes-with-labels).

## Deploy the `sockshop` service
When building the base image, the `sockshop` repo has already been downloaded at the home directory. Run the following command on manager machine to deploy:
```
cd microservices-demo/deploy/docker-swarm/ && docker stack deploy --compose-file docker-compose.yml sockshop
```

Use `docker service ls` to confirm the services have been deployed successfully.

After application nodes joins or leaves we no longer need to use `docker service scale` to manually scale up/down the number of service replicas thanks to the [`global` deploy mode](https://docs.docker.com/engine/swarm/how-swarm-mode-works/services/#replicated-and-global-services). However we still need to add label to a new added node otherwise no services will be deployed on that node. 
