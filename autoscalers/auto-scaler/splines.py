'''
Created on May 24, 2019

@author: Ahmed Ali-Eldin, UMass Amherst.
'''


#  SpotWeb
# 
#  Copyright (c) 2019 The SpotWeb team, led by Ahmed Ali-Eldin and Prof. Prashant Shenoy at UMass Amherst. All Rights Reserved.
# 
# This product is licensed to you under the Apache 2.0 license (the "License").
# You may not use this product except in compliance with the Apache 2.0
# License.
# 
# This product may include a number of subcomponents with separate copyright
# notices and license terms. Your use of these subcomponents is subject to the
# terms and conditions of the subcomponent's license, as noted in the LICENSE
# file.
# This predictor wraps the cubic splines predictor. It can be used either in simulation mode where a Requests file containing a timestamp and a number of requests
# is used to replay  the workload or where the new load measurement is supplied to the REST interface.
#Requires:
# models.in: A file with the data to be used for intializing the model
#The REST interface is set to localhost with port number 5012 
# To test usage: curl -i -H "Content-Type: application/json" -X POST -d '{"load":"5"}' http://localhost:5012/splines/v1.0/monitoring
# Returns 5 future predictions using the cubic splines model
#Can be used to replay a trace using the replayWorkloadsimulation method

import rpy2.robjects as robjects
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib
from scipy.stats import norm
import sys

import os, math
import time
import operator
from flask import Flask,request,jsonify
import csv

app = Flask(__name__)

matplotlib.rcParams.update({'font.size': 16})

Requests=open("models.in","r")
#ind=open("AggReq.out",'r')

# load r-object and R-file.
r_source = robjects.r['source']
r_source("predictor.R")

# Load predictor with data
r_load = robjects.r["pred_load_data"]
r_load(robjects.StrVector(["AggReq.out"]))
predict = robjects.r["pred_predict"]
r5=[]

def replayWorkloadsimulation(startTime,endTime):
    ReqList=[]
    predList=[]
    for line in Requests.readlines()[startTime:endTime]:
        l=line.split()
        req=float(l[-1])
        ReqList+=[req]
        r5 = predict(robjects.IntVector([req]), robjects.IntVector([5]))[:]
        predList+= [(r3[0] , r3[1] , r3[2] , r3[3] , r3[4]+r3[5])]
    wl=pd.Series(ReqList)
    sns.lineplot(data=wl)
    plt.xlabel("Time")
    plt.ylabel("Number of Requests")
    plt.savefig('WLPredictorAcc.pdf', bbox_inches='tight')
    plt.show()

    Errors1=[]
    Errors2=[]
    Errors3=[]
    Errors4=[]
    Errors5=[]
    
    for i in range(len(predList)-5):
        Errors1+=[(predList[i][0]-ReqList[i+1])/ReqList[i+1]]
        Errors2+=[(predList[i][1]-ReqList[i+2])/ReqList[i+2]]
        Errors3+=[(predList[i][2]-ReqList[i+3])/ReqList[i+3]]
        Errors4+=[(predList[i][3]-ReqList[i+4])/ReqList[i+4]]
        Errors5+=[(predList[i][4]-ReqList[i+5])/ReqList[i+5]]    
    
    e1=pd.Series(Errors1)
    e2=pd.Series(Errors2)
    e3=pd.Series(Errors3)
    e4=pd.Series(Errors4)
    e5=pd.Series(Errors5)
    
    print e1.std(), e1.median(), e1.mean(), e1.max(),e1.min()
    print e2.std(), e2.median(), e2.mean(),e2.max()
    print e3.std(), e3.median(), e3.mean()
    print e4.std(), e4.median(), e4.mean()
    print e5.std(), e5.median(), e5.mean()
    
    sns.distplot(e1, norm_hist=True,fit=norm)
    plt.xlabel("Prediction Error")
    plt.ylabel("Probability")
    plt.savefig('Wiki_LA1.pdf', bbox_inches='tight')
    
    sns.distplot(e2, norm_hist=True,fit=norm)
    plt.xlabel("Prediction Error")
    plt.ylabel("Probability")
    plt.savefig('Wiki_LA2.pdf', bbox_inches='tight')
    
    sns.distplot(e3, norm_hist=True,fit=norm)
    plt.xlabel("Prediction Error")
    plt.ylabel("Probability")
    plt.savefig('Wiki_LA3.pdf', bbox_inches='tight')
    
    sns.distplot(e4, norm_hist=True,fit=norm)
    plt.xlabel("Prediction Error")
    plt.ylabel("Probability")
    plt.savefig('Wiki_LA4.pdf', bbox_inches='tight')
    
    sns.distplot(e5, norm_hist=True,fit=norm)
    plt.xlabel("Prediction Error")
    plt.ylabel("Probability")
    plt.savefig('Wiki_LA5.pdf', bbox_inches='tight')

    wl=pd.Series(ReqList)
    sns.lineplot(data=wl)
    plt.xlabel("Time")
    plt.ylabel("Number of Requests")
    plt.savefig('WLPredictorAcc.pdf', bbox_inches='tight')

@app.route('/splines/v1.0/monitoring', methods=['POST'])
def run_splines():
    global r3
    load=float(request.json['load'])
    r3 = predict(robjects.IntVector([load]), robjects.IntVector([5]))[:]
    predList= [float(r3[0]) , float(r3[1]) , float(r3[2]),float(r3[3]),float(r3[4])]
    return jsonify({'prediction': predList}), 201

if __name__ == '__main__':
        app.run(debug=True,host='127.0.0.1', port=5012)
