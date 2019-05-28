#!/bin/bash

service rsyslog start

/usr/local/etc/halog-scripts/restlogandsave.sh & #this isnt right, exec --detach should work but dos'nt? Why?

exec haproxy -db -W -f /usr/local/etc/haproxy/haproxy.cfg

