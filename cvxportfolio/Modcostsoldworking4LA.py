"""
Copyright 2016 Stephen Boyd, Enzo Busseti, Steven Diamond, BlackRock Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import cvxpy as cvx
from cvxpy import *
import numpy as np
import copy
from expression import Expression
import data_management 
import datetime as dt
#from data_management import null_checker,non_null_data_args,time_matrix_locator

__all__ = ['HcostModelServers','TcostModelServers']

dm=data_management.data_management()

class BaseCost(Expression):

    def __init__(self):
        self.gamma = 1.  # it is changed by gamma * BaseCost()
        

    def weight_expr(self, t, w_plus, z, value):
        cost, constr = self._estimate(t, w_plus, z, value)
        return self.gamma * cost, constr

    def weight_expr_ahead(self, tau, w_plus, z, value,LA,acc):
        cost, constr = self._estimate_ahead(tau, w_plus, z, value,LA,acc)
        return self.gamma * cost, constr

    def __mul__(self, other):
        """Read the gamma parameter as a multiplication."""
        newobj = copy.copy(self)
        newobj.gamma *= other
        return newobj

    def __rmul__(self, other):
        """Read the gamma parameter as a multiplication."""
        return self.__mul__(other)


class HcostModelServers(BaseCost):
    """A model for holding costs.

    Attributes:
      borrow_costs: A dataframe of borrow costs.
      dividends: A dataframe of dividends.
    """

    def __init__(self, penalty,L, pricePerReq,probFail,arrivalRate,oracle=True):
        dm.null_checker(probFail)
        self.failure = probFail
        dm.null_checker(arrivalRate)
        self.Lambda = arrivalRate
        self.penalty=penalty
        self.L=L
        self.oracle=oracle
        self.pricePerReq = pricePerReq
        super(HcostModelServers, self).__init__()
        
            

    def _estimate(self, t, w_plus, z, value,LA,acc):
        """Estimate holding costs.

        Args:
          t: time of estimate
          wplus: holdings
          tau: time to estimate (default=t)
        """
        if self.oracle:
            constr = []
            xyz=0
            try:
		print  "failure", dm.time_locator(self.failure, t),list(self.failure)
		print "Lambda", dm.time_locator(self.Lambda, t).tolist()[0]
		print  "Lambda+dt",dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()
		print  "self.L", self.L
		print "delta lambda", dm.time_locator(self.Lambda, t).tolist()[0]-dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0]
		print "1st part 3rd term",dm.time_locator(self.failure, t).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).multiply(self.L).tolist()[0]) 
		print "2nd part 3rd term",  -(dm.time_locator(self.Lambda, t).tolist()[0]-dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0])
          	if LA==1: #dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0]>0:
			third_term = dm.time_locator(self.failure, t).multiply(dm.time_locator(self.Lambda, t).multiply(self.L).tolist()[0])
			#	+dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0]    #Late requests and failure cost
	                second_term = dm.time_locator(self.pricePerReq,t).multiply(dm.time_locator(self.Lambda, t).tolist()[0])    #Provisioning cost

		elif LA<4:
			third_term = dm.time_locator(self.failure, t+dt.timedelta(hours=1)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).multiply(self.L).tolist()[0])\
				+dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0]    #Late requests and failure cost
	                second_term = dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=1)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0])    #Provisioning cost
			#	+dm.time_locator(self.Lambda, t).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0]    #Late requests and failure cost
#				+ dm.time_locator(self.Lambda, t).tolist()[0]-dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0]    #Late requests and failure cost
		else:
			third_term = dm.time_locator(self.failure, t+dt.timedelta(hours=4)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).multiply(self.L).tolist()[0])\
				+dm.time_locator(self.Lambda, t+dt.timedelta(hours=LA+1)).tolist()[0]- dm.time_locator(self.Lambda, t+dt.timedelta(hours=LA)).tolist()[0] #dm.time_locator(self.Lambda, t).tolist()[0]    #Late requests and failure cost
	                second_term = dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=1)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0])    #Provisioning cost
			#	+dm.time_locator(self.Lambda, t).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0]    #Late requests and failure cost
#				+ dm.time_locator(self.Lambda, t).tolist()[0]-dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0]    #Late requests and failure cost
			
		print "third term b4 multiplication", third_term.tolist()
                third_term*=self.penalty
		print "penalty", self.penalty
		print "pricePerReq",dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=1)), list(self.pricePerReq)
#                second_term = dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=1)).multiply(dm.time_locator(self.Lambda, t).tolist()[0])    #Provisioning cost
		#print "third term b4 we add 2nd", third_term.all
		print "second term b4 we add 2nd", second_term.tolist()
		third_term+=second_term
		third_term*=1
		print "Total", third_term.tolist()
		xyz+=1
            except Exception as e:
                print "Exception in estimate", t, xyz
                print str(e)
            # no trade conditions
	    #print "Third Term estimate with 2nd term", third_term.all
            if np.isscalar(third_term):
                if np.isnan(third_term):
                    constr += [z == 0]
                    third_term = 0
                    print "SLA violation Costs converged to zero due to NANs"
            else:  # it is a pd series
                #print "third_term.isnull()",sum(third_term) 
                no_trade = third_term.index[third_term.isnull()]
                print "no_trade", no_trade
                third_term[no_trade] = 0
                print "Third Term is not a scalar"
    
            third_term[third_term<0]=0
            try:
		#print w_plus.value, type(third_term)
                self.expression = third_term.multiply(cvx.abs(z))
            except TypeError:
                self.expression = third_term.values.multiply(cvx.abs(w_plus))
                print "Error when Multiplying Third Term with allocation"
    	   # print "gen expression",sum(self.expression)
            return sum(self.expression), []
        else:
            print "Non Oracle mode not implemented"

    def _estimate_ahead(self, tau, w_plus, z, value,LA,acc):
        return self._estimate(tau, w_plus, z, value,LA,acc)

    def value_expr(self, t, h_plus, u,LA,acc):
	u[u<0]=0
        u_nc = u
        if LA==1: #dm.time_locator(self.Lambda, t+dt.timedelta(hours=1)).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0]>0:
	       	if dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0]>0:
			third_term = dm.time_locator(self.failure, t+dt.timedelta(hours=4)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).multiply(self.L).tolist()[0])\
				+dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0]    #Late requests and failure cost
		        second_term = dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=4)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).tolist()[0])    #Provisioning cost
			print "Debugging Calcu",LA,t, third_term*u, second_term*u, sum(third_term*u),sum(second_term*u)
			print "error in prediction",dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).tolist()[0]- dm.time_locator(self.Lambda, t).tolist()[0],"LLLL", self.L
		else:
			third_term = dm.time_locator(self.failure, t+dt.timedelta(hours=4)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).multiply(self.L).tolist()[0])
	                second_term = dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=4)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).tolist()[0])    #Provisioning cost
			print "Debugging Calcu", LA,t, third_term*u, second_term*u, sum(third_term*u),sum(second_term*u),"LLLLL",self.L


	else:
			third_term = dm.time_locator(self.failure, t+dt.timedelta(hours=4)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).multiply(self.L).tolist()[0])\
				+(dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).tolist()[0]-dm.time_locator(self.Lambda, t).tolist()[0])*acc
	                second_term = dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=4)).multiply(dm.time_locator(self.Lambda, t+dt.timedelta(hours=4)).tolist()[0])    #Provisioning cost
			print "Debugging Calcu", LA,t, third_term*u, second_term*u, sum(third_term*u),sum(second_term*u), "LLLLL",self.L
			print "Accuracy", acc
        third_term*=self.penalty
	#print "ThirdTermCalc", third_term*u_nc, third_term
	#print "SecondtermCalc", second_term*u_nc, second_term

	third_term+=second_term

        self.last_cost = third_term*u_nc  #np.abs(u_nc) * self.penalty *(self.L*dm.time_locator(self.failure, t).multiply(

        return  sum(self.last_cost)

    def optimization_log(self, t):
	return self.expression.values

    def simulation_log(self, t):
        return self.last_cost


class TcostModelServers(BaseCost):
    """A model for transaction costs.
    Added by Ahmed Ali, UMass, Amherst
    all rights reserved
    """
    def __init__(self, arrival=200, pricePerReq=1.,oracle=True):
        MachinePrices=super(TcostModelServers, self).__init__()
        dm.null_checker(arrival)
        self.Lambda = arrival
        dm.null_checker(pricePerReq)
        self.pricePerReq = pricePerReq
        self.oracle=oracle
        

    def _estimate(self, t, w_plus, z, value):
        if self.oracle:
            try:
                z = z[z.index != self.cash_key]
                z = z.values
            except AttributeError:
                z = z[:-1]  # TODO fix when cvxpy pandas ready
    
            constr = []
            xyz=0
            try:
                second_term = dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=1)).multiply(dm.time_locator(self.Lambda, t).tolist()[0])    #Provisioning cost
                xyz+=1
            except Exception as e:
                #print "Now to second term",t, xyz
                print e

            if np.isscalar(second_term):
                if np.isnan(second_term):
                    constr += [z == 0]
                    second_term = 0
                else:  # it is a pd series
                    no_trade = second_term.index[second_term.isnull()]
                    second_term[no_trade] = 0
                    constr += [z[second_term.index.get_loc(tick)] == 0
                               for tick in no_trade]
            self.expression = second_term[:-1].multiply(cvx.abs(z))
    	    #print "Here is the second term",type(self.expression),"sec part", type(sum(self.expression))
            return sum(self.expression), []
        else:
            print "Non Oracle mode not implemented"

    def value_expr(self, t, h_plus, u):
        '''u is the trades (not cash)
        hplus is the  current portfolio+the trades
        '''

        u_nc = u.iloc[:-1]
        self.tmp_tcosts = (np.abs(u_nc) * dm.time_locator(self.pricePerReq,t+dt.timedelta(hours=1)).multiply(dm.time_locator(self.Lambda, t).tolist()[0]))

        return self.tmp_tcosts.sum()

    def optimization_log(self, t):
        try:
            return self.expression.value
        except AttributeError:
            return np.nan

    def simulation_log(self, t):
        # TODO find another way
        return self.tmp_tcosts

    def _estimate_ahead(self, t, tau, w_plus, z, value):
        """Returns the estimate at time t of tcost at time tau.
        Gets called in the Base_cost class
        """
        return self._estimate(t, w_plus, z, value)

    def est_period(self, t, tau_start, tau_end, w_plus, z, value):
        """Returns the estimate at time t of tcost over given period.
        """
        K = (tau_end - tau_start).hours   #Changed to hours instead of days.
        tcost, constr = self.eight_expr(t, None, z / K, value)
        return tcost * K, constr
'''
Created on Nov 28, 2018

@author: ahmeda
'''
