'''
Created on May 29, 2019

@author: Bin Wang @UMass Amherst
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
import itertools
import os
import shutil
import subprocess
import sys

from string import Template

client_num_tests = [5]
request_num_tests = [10000]
app_server_vcpu_tests = [1, 2, 4, 8]
app_server_memory_tests = [1024, 2048, 4096, 8192]
results_folder = os.path.join(os.getcwd(), "results")

if __name__ == "__main__":
    if os.path.exists(results_folder):
        sys.exit("results folder exists")

    for client_num, request_num, app_server_vcpu, app_server_memory in itertools.product(client_num_tests, request_num_tests, app_server_vcpu_tests, app_server_memory_tests):
        d = {"client_num": client_num,
             "request_num": request_num,
             "app_server_vcpu": app_server_vcpu,
             "app_server_memory": app_server_memory}
        print(d)

        fin = open("conf.yml.template")
        src = Template(fin.read())
        result = src.substitute(d)
        with open("conf.yml", "w") as fout:
            print(result, file=fout)

        subprocess.call("./preprocess")
        subprocess.call("./runexperiment")

        output_folder = "{client_num}_{request_num}_{app_server_vcpu}_{app_server_memory}".format(**d)
        output_folder = os.path.join(results_folder, output_folder)
        os.makedirs(output_folder)
        shutil.move("stats.out", os.path.join(output_folder, "stats.out"))
        shutil.move("docker.out", os.path.join(output_folder, "docker.out"))
        shutil.move("conf.yml", os.path.join(output_folder, "conf.yml"))
