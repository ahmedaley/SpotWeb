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
