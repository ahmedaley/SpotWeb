#!/bin/bash

inputfile=/var/log/haproxy-access.log
srv_output_file=/var/log/srv_halog_output.log
pct_output_file=/var/log/pct_halog_output.log


truncate_inputfile(){
    truncate --size 0 $inputfile
}

halog_file(){
    aa=$(< ${inputfile})
    timetaken=$(date '+%Y-%m-%d-%H:%M:%S.%3N')
    truncate_inputfile
    echo "$aa" | halog -srv | tail -n +2 | sed "s/^/$timetaken /" >> $srv_output_file
    echo "$aa" | halog -pct | tail -n +2  | sed "s/^/$timetaken /" >> $pct_output_file
    #echo "$aa" | halog -pct | column -t -s ' ' | tail -n +2 | while IFS= read -r line; do printf '%s %s\n' "$(date '+%Y-%m-%d-%H:%M:%S.%3N')" "$line"; done >> $pct_output_file
    #echo "$aa" | halog -pct | column -t -s ' ' | tail -n +2 | while IFS= read -r line; do printf '%s %s\n' "$(date '+%Y-%m-%d-%H:%M:%S.%3N')" "$line"; done >> $pct_output_file
}




#reset log file
header=$(echo "" | halog -srv | head -n 1)
header="timestamp $header"
echo "$header" > $srv_output_file

header=$(echo "" | halog -pct | head -n 1)
header="timestamp $header"
echo "$header" > $pct_output_file

#echo "req err ttot tavg oktot okavg url" | column -t > $outputfile

#srv_name 1xx  2xx  3xx  4xx  5xx  other  tot_req  req_ok  pct_ok  avg_ct  avg_rt

#reset input haproxy file.
truncate_inputfile

while true; do
    sleep 5
    halog_file
done
