# Load-Balancer

This folder contains  code related to the SpotWeb modifications to HAProxy to support managing spot instances. 

The LB consist of three main components:

1- The first is the instance of haproxy, used as a docker container.

2- The second part written in java/kotlin needs to be installed to run on the docker container. This code is used for updating the
configuration of HAProxy. 
To build this part you need to run:

`java -jar build/libs/load-balancer-1.0-SNAPSHOT-all.jar /home/ubuntu/load-balancer/haproxy-docker/haproxy/haproxy.cfg &`

3- The third part is the interface needed to fetch information from the HAProxy via a REST-API

