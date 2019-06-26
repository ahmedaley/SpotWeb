'''
Created on May 29, 2019

@author: Jonathan Westin and Ahmed Ali-Eldin
'''

#  SpotWeb
# 
#  Copyright (c) 2019 The SpotWeb team, led by Ahmed Ali-Eldin and Prashant Shenoy at UMass Amherst. All Rights Reserved.
# 
# This product is licensed to you under the Apache 2.0 license (the "License").
# You may not use this product except in compliance with the Apache 2.0
# License.
# 
# This product may include a number of subcomponents with separate copyright
# notices and license terms. Your use of these subcomponents is subject to the
# terms and conditions of the subcomponent's license, as noted in the LICENSE
# file.
# This module provides an interface to AWS web service to start and stop instances based on the predicted workload
#To create the AMIs, please use the Wikipedia image baseImageWithMemCacheOnly.qcow2 available here :http://zenky.cs.umu.se/PEAS/
# 
import json

import boto3

#Your AWS credentials
SG_GROUP = "sg-xx"
SUBNET = "subnet-xx"

ACCESS_KEY ="xx"
SECRET_KEY = "xx"
KEY_NAME = "myname"
LBAMI = "ami-xx"
WIKIAMI = "ami-xx"
LB = {}


class InstanceType:
    def __init__(self, name, request_per_second):
        self.name = name
        self.rps = request_per_second

    def __str__(self):
        return "%s - %d" % (self.name, self.rps)

    def __repr__(self):
        return self.__str__()

class Cluster:
    client = boto3.client('ec2',
                          aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY
                          # aws_session_token=SESSION_TOKEN,
                          )
    nodes = []
    load_balance = None
    haproxy_load = []
    types = []

    def __init__(self):
        self._getClusterInfo()

    def add_instance_types(self, name, request_per_second):
        self.types.append(InstanceType(name, request_per_second))

    def _getClusterInfo(self):
        response = self.client.describe_instances()
        for r in response["Reservations"]:
            r = r["Instances"][0]
            try:
                i = Instance(r)
                if i.nodetype == "LOADBALANCER":
                    if self.load_balance is None:
                        self.load_balance = LoadBalancer(r)
                elif i not in self.nodes:
                    self.nodes.append(i)
                    h = HaproxyLoad("%s-%s" %(i.instance_type, i.priv_ip), i.priv_ip, -1)
                    self.haproxy_load.append(h)
            except ValueError:
                pass
        self._update_load()

    def print_lb(self):
        return self.load_balance.as_string()

    def _update_load(self):
        tmp = []
        for l in self.haproxy_load:
            if l.weight != 0:
                tmp.append(l)

    def update_load(self, a):
        self.print_lb()
        a = input("Select server to change weight (enter to go back)...")
        if a.isdigit() and 0 < int(a) <= len(self.haproxy_load)-1:
            a = input("Select new weight")
            if a.isdigit() and int(a) >= 0:
                #TODO
                self.load_balance["Backend"][0][i - 1]["Weight"] = a
                self.load_balance.updateLB(self.load_balance)
                self.load_balance.print_lb()

    def get_nodes(self, printnodes=False):
        self._getClusterInfo()
        self.nodes = sorted(self.nodes, key=lambda x: (x.nodetype, x.instance_type))
        if self.load_balance is None:
            print("No load-balancing configuration set")
            l = []
            for n in nodes:
                if n.type == "WORKER":
                    #TODO
                    lbn = {}
                    lbn["Name"] = "%s-%s" % (n.instance_type, n.priv_ip)
                    lbn["Endpoint"] = "%s:80" % n.priv_ip
                    lbn["Weight"] = int(n.vt_cpu) * int(n.cpu)
                    l.append(lbn)
            load_balance = {}
            load_balance["Backend"] = l
            self.updateLB(load_balance)
        else:
            ba = self.load_balance["Backend"]
            for n in nodes:
                if n.type != "WORKER":
                    continue
                found = False
                name_string = "%s-%s" % (n.instance_type, n.priv_ip)
                for l in ba:
                    if name_string == l["Name"]:
                        found = True
                if not found:
                    print("Not found %s" % name_string)
                    #TODO
                    lbn = {}
                    lbn["Name"] = "%s-%s" % (n.instance_type, n.priv_ip)
                    lbn["Endpoint"] = "%s:80" % n.priv_ip
                    lbn["Weight"] = int(n.vt_cpu) * int(n.cpu)
                    self.load_balance["Backend"].append(lbn)
                    self.updateLB(self.load_balance)

        return self.nodes

    def createSpot(self, type_of_instance):
        if type_of_instance in self.types:
            print(type_of_instance)
            response = self.client.request_spot_instances(
                DryRun=False,
                InstanceCount=1,
                Type='one-time',
                LaunchSpecification={
                    'ImageId': WIKIAMI,
                    "KeyName": KEY_NAME,
                    'InstanceType': type_of_instance.name,
                    "NetworkInterfaces": [
                        {
                            "DeviceIndex": 0,
                            "SubnetId": SUBNET,
                            "Groups": [SG_GROUP],
                            "AssociatePublicIpAddress": True
                        }
                    ]

                }
            )
            print(response)
            instance_request = response["SpotInstanceRequests"][0]
            if "SpotInstanceRequestId" not in instance_request or instance_request["SpotInstanceRequestId"] == "":
                raise Exception("No instance id is returned, fault code: {}, message: {}".format(
                    instance_request["Status"]["Code"], instance_request["Status"]["Message"]))

            try:
                waiter = self.client.get_waiter('spot_instance_request_fulfilled')
                waiter.wait(SpotInstanceRequestIds=[instance_request["SpotInstanceRequestId"]],
                            WaiterConfig={"Delay": 1, "MaxAttempts": 60})
            except Exception as e:
                # Cleanup before raise exception
                self.client.cancel_spot_instance_requests(SpotInstanceRequestIds=[instance_request["SpotInstanceRequestId"]])
                print("timeout, request cancelled")

            response = self.client.describe_spot_instance_requests(
                SpotInstanceRequestIds=[instance_request["SpotInstanceRequestId"]])
            print(response)
            # instance = client.Instance(response["SpotInstanceRequests"][0]["InstanceId"])
            # instance.wait_until_running()

    def createOnDemand(self, type_of_instance):
        if type_of_instance in self.types:
            print(type_of_instance)
            response = self.client.run_instances(
                ImageId=WIKIAMI,
                KeyName=KEY_NAME,
                MaxCount=1,
                MinCount=1,
                InstanceType=type_of_instance.name,
                NetworkInterfaces=[
                        {
                            "DeviceIndex": 0,
                            "SubnetId": SUBNET,
                            "Groups": [SG_GROUP],
                            "AssociatePublicIpAddress": True
                        }
                    ],
            )
            print(response)


    def __str__(self):
        self.get_nodes()
        strbuilder = ""
        strbuilder += "%s\n" % self.load_balance
        for n in self.nodes:
            strbuilder += "%s\n" %n
        return strbuilder

    '''def __getitem__(self, item):
        if self.type == "LOADBALANCER" and item == "LOADBALANCER":
            return self
        if self.type == "WORKER" and type[item] == self.instance_type:
            return self
        if self.type == "WORKER" and item == self.instance_type:
            return self
    '''


class Instance:
    def __init__(self, instance_json):
        r = instance_json
        self.weight = -1
        self.image = r["ImageId"]

        self.nodetype = "UNDEFINED"
        if self.image == WIKIAMI:
            self.nodetype = "WORKER"
        if self.image == LBAMI:
            self.nodetype = "LOADBALANCER"

        self.state = r["State"]
        self.state = self.state["Name"]
        if self.state != "running":
            raise ValueError("not running instance")

        self.instanceid = r["InstanceId"]
        self.priv_ip = r["PrivateIpAddress"]
        self.pub_ip = r["PublicIpAddress"]
        self.instance_type = r["InstanceType"]
        self.spot_req_id = ""
        cpu = r["CpuOptions"]
        self.vt_cpu = cpu["ThreadsPerCore"]
        self.cpu = cpu["CoreCount"]
        spot_req_id = ""
        if "SpotInstanceRequestId" in r:
            spot_req_id = r["SpotInstanceRequestId"]
        self.spot_req_id = spot_req_id

    def __eq__(self, other):
        if isinstance(other, Instance):
            return self.instanceid == other.instanceid
        return False

    def __hash__(self):
        return self.instanceid

    def __str__(self):
        return ("%s %s %s %s %s %s %s %s %s %s" % (
                str(self.weight).ljust(4),
                self.nodetype.ljust(12),
                self.image.ljust(22),
                self.instanceid.ljust(22),
                self.instance_type.ljust(12),
                self.priv_ip.ljust(16),
                self.pub_ip.ljust(16),
                self.spot_req_id.ljust(22),
                str(self.cpu).ljust(2),
                str(self.vt_cpu).ljust(2)))


class LoadBalancer(Instance):

    def __init__(self, instance_json):
        super().__init__(instance_json)


    def updateLB(self, data=None):
        if False:
            print(json.dumps(data))
        r = requests.post("http://%s:4567/update" % LB["EIP"], data=json.dumps(data))
        print("LB-response:" + r.text)





class HaproxyLoad():

    def __init__(self, name, endpoint, weight, port=80):
        self.name = name
        self.endpoint = endpoint
        self.weight = weight
        self.port = port

    def get_string(self):
        return '"Name": %s, "Endpoint": "%s:%d", "Weight": %d' % (self.name, self.endpoint, self.port, self.weight)

    def set_weight(self, new_weight):
        self.weight = new_weight

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name > other.name



if __name__ == '__main__':
    
    cluster = Cluster()
    cluster.add_instance_types("m4.large", 0)
    cluster.add_instance_types("m4.xlarge", 1)
    cluster.add_instance_types("m4.2xlarge", 2)
    cluster.add_instance_types("m4.4xlarge", 3)
    cluster.add_instance_types("m4.10xlarge", 4)
    cluster.add_instance_types("m4.16xlarge", 5)
    
    cluster.add_instance_types("c5.large", 6)
    cluster.add_instance_types("c5.4xlarge", 7)
    cluster.add_instance_types("c5.18xlarge", 8)
    
    
    while True:
        print("%s %s %s %s %s %s %s %s %s" % (
            "wht".ljust(4),
            "nodetype".ljust(12),
            "image".ljust(22),
            "instanceId".ljust(22),
            "instanceType".ljust(12),
            "priv_ip".ljust(16),
            "pub_ip".ljust(16),
            "spot_req_id".ljust(22),
            "cpu".ljust(2)))
    
    
        print(cluster)
    
        a = input("Press Enter to continue...")
    
        if a == "spot":
            print(cluster.types)
            a = input("select type (0 - %d)..." % (len(cluster.types)-1))
            if a.isdigit() and 0 <= int(a) < len(cluster.types):
                cluster.createSpot(cluster.types[int(a)])
            else:
                print("Invalid selection" + a)
    
        if a == "od":
            print(cluster.types)
            a = input("select type (0 - %d)..." % (len(cluster.types)-1))
            if a.isdigit() and 0 <= int(a) < len(cluster.types):
                cluster.createOnDemand(cluster.types[int(a)])
            else:
                print("Invalid selection" + a)
    
        if a == "lb":
            cluster.print_lb()
