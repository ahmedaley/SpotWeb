import os
import re
import subprocess
from datetime import datetime

from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
srv_halog_filename = "/shared-lb-mount/srv_halog_output.log"
pct_halog_filename = "/shared-lb-mount/pct_halog_output.log"


def time_diff(last, now):
    fmt = '%Y-%m-%d-%H:%M:%S.%f'
    tstamp1 = datetime.strptime(last, fmt)
    tstamp2 = datetime.strptime(now, fmt)

    if tstamp1 > tstamp2:
        td = tstamp1 - tstamp2
    else:
        td = tstamp2 - tstamp1
    return int(td.total_seconds() * 1000)


def get_key_from_list(idx, list):
    key = "UNKWN COL(idx:%d)" % idx
    if len(list) > idx:
        key = list[idx]
    return key


def get_line(desc, l):
    l = l.decode().replace("\t", " ")
    l = l.replace("\n", "")
    l = l.replace("#", "")
    l = re.sub(' +', ' ', l)
    line_val = {}
    for idx, val in enumerate(l.split(" ")):
        key = get_key_from_list(idx, desc)
        if len(val) == 0:
            continue
        if val.isdigit():
            val = int(val)
        line_val[key] = val
    return line_val


def get_prec(timestamp):
    proc = subprocess.Popen(['grep', timestamp, pct_halog_filename], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    desc = ["Timestamp", "Percentile"]
    ret = {}
    retfind = ["95.0", "98.0", "99.0", "99.9", "100.0"]
    for l in lines:
        line_val = get_line(desc, l)
        line_val.pop("Timestamp", None)
        retkey = get_key_from_list(1, desc)
        retkey = line_val[retkey]
        line_val.pop("Percentile", None)

        if retkey in retfind:
            if not retkey in ret:
                ret[retkey] = []
            ret[retkey].append(line_val)
    for r in ret:
        totsum = 0
        for pr in ret[r]:
            sum = 0
            for pro in pr.values():
                sum += int(pro)
            pr["sum"] = sum

            totsum += sum

        #ret["totsun"] = totsum
    return ret


def get_unique_servers(logfilename):
    #tail -n +2 ~/www-19/scripts/t2.txt | sort -uk2,2 | awk '{ print $2 }'
    p1 = subprocess.Popen(['tail',  '-n', '+2', logfilename], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['tac'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['sort', '-uk2,2'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p4 = subprocess.Popen(['awk', "{ print $2 }"], stdin=p3.stdout, stdout=subprocess.PIPE)
    return p4.stdout.readlines()


class Halog(Resource):
    def get(self, noOfLines=1):
        global srv_halog_filename, pct_halog_filename

        # Get headers
        desc = (open(srv_halog_filename).readline())
        desc = re.sub(' +', ' ', desc).replace("#","").strip().split(' ')


        servers = get_unique_servers(srv_halog_filename)
        ret = {}
        for server in servers:
            server = server.decode().replace("\n", "")

            ret[server] = []
            #grep http-in/server-1 t2.txt | tail -n 2

            p1 = subprocess.Popen(['grep', server, srv_halog_filename], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['tail', '-n', str(int(noOfLines)+1)], stdin=p1.stdout, stdout=subprocess.PIPE)
            lines = p2.stdout.readlines()
            print(lines)

            # if someone is trying to get more than exists in the file and we got first line
            if (get_line(desc, lines[0])[desc[0]]) == desc[0]:
                lines = lines[1:]

            # pop one so we get last timestamp, note one more from tail in p2.
            first = get_line(desc, lines[0])[desc[0]]
            last_timestamp = str(first)

            # The rest
            for l in lines[1:]:
                line_val = get_line(desc, l)
                timestamp = str(line_val[desc[0]])
                the_diff = str(time_diff(last_timestamp, timestamp))
                line_val["ms_since_last_entry"] = int(the_diff)
                last_timestamp = timestamp
                line_val["percentile"] = get_prec(timestamp)
                line_val.pop("srv_name", None)
                ret[server].append(line_val)

        return ret


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')
api.add_resource(Halog, '/halog/<int:noOfLines>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
