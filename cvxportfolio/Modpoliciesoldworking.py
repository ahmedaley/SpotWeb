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

from abc import ABCMeta, abstractmethod
import pandas as pd
import numpy as np
import logging
import cvxpy as cvx
from cvxpy import *
from osqp import *
from cvxportfolio.Modcostsoldworking import BaseCost
from cvxportfolio.Modreturnsoldworking import BaseReturnsModel
from cvxportfolio.constraintsow import BaseConstraint
import data_management
import time
dm=data_management.data_management()


__all__ = ['Hold', 'FixedTrade', 'PeriodicRebalance', 'AdaptiveRebalance',
           'SinglePeriodOpt', 'MultiPeriodOpt', 'ProportionalTrade',
           'RankAndLongShort']


class BasePolicy(object):
    """ Base class for a trading policy. """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.costs = []
        self.constraints = []
    @abstractmethod
    def get_trades(self, portfolio, t=pd.datetime.today()):
        """Trades list given current portfolio and time t.
        """
        return NotImplemented

    def _nulltrade(self, portfolio):
        return pd.Series(index=portfolio.index, data=0.)

    def get_rounded_trades(self, portfolio, prices, t):
        """Get trades vector as number of shares, rounded to integers."""
        return np.round(self.get_trades(portfolio,
                                        t) / dm.time_locator(prices, t))[:-1]


class SinglePeriodOpt(BasePolicy):
    """Single-period optimization policy.

    Implements the model developed in chapter 4 of our paper
    https://stanford.edu/~boyd/papers/cvx_portfolio.html
    """

    def __init__(self,  costs, constraints,return_forecast=None, solver=None,
                 solver_opts=None):

        super(SinglePeriodOpt, self).__init__()

        for cost in costs:
            print type(cost), type(BaseCost)
            assert isinstance(cost, BaseCost)
            self.costs.append(cost)

        for constraint in constraints:
	    print type(constraint)
            assert isinstance(constraint, BaseConstraint)
#	    print "policies single", type(constraint)
            self.constraints.append(constraint)

        self.solver = solver
        self.solver_opts = {} if solver_opts is None else solver_opts

    def get_trades(self, portfolio, t=None):
        """
        Get optimal trade vector for given portfolio at time t.

        Parameters
        ----------
        portfolio : pd.Series
            Current portfolio vector.
        t : pd.timestamp
            Timestamp for the optimization.
        """

        if t is None:
            t = pd.datetime.today()

        value = sum(portfolio)
        w = portfolio / value
        z = cvx.Variable(w.size)  # TODO pass index
        wplus = w.values + z

        if isinstance(self.return_forecast, BaseReturnsModel):
            alpha_term = self.return_forecast.weight_expr(t, wplus)
        else:
            alpha_term = cvx.sum(cvx.multiply(
                dm.time_locator(self.return_forecast, t, as_numpy=True), wplus))

        assert(alpha_term.is_concave())

        costs, constraints = [], []

        for cost in self.costs:
            cost_expr, const_expr = cost.weight_expr(t, wplus, z, value)
            costs.append(cost_expr)
            constraints += const_expr

        constraints += [item for item in (con.weight_expr(t, wplus, z, value)
                                          for con in self.constraints)]

        for el in costs:
            assert (el.is_convex())

        for el in constraints:
            assert (el.is_dcp())

        self.prob = cvx.Problem(
            cvx.Minimize(alpha_term - sum(costs)),
            [cvx.sum(z) == 0] + constraints)
        try:
            self.prob.solve(solver=self.solver, **self.solver_opts)

            if self.prob.status == 'unbounded':
                logging.error(
                    'The problem is unbounded. Defaulting to no trades')
                return self._nulltrade(portfolio)

            if self.prob.status == 'infeasible':
                logging.error(
                    'The problem is infeasible. Defaulting to no trades')
                return self._nulltrade(portfolio)

            return pd.Series(index=portfolio.index, data=(z.value * value))
        except cvx.SolverError:
            logging.error(
                'The solver %s failed. Defaulting to no trades' % self.solver)
            return self._nulltrade(portfolio)


class MultiPeriodOpt(SinglePeriodOpt):

    def __init__(self, trading_times,
                 lookahead_periods, accuracy, *args, **kwargs):
        """
        trading_times: list, all times at which get_trades will be called
        lookahead_periods: int or None. if None uses all remaining periods
        """
        # Number of periods to look ahead.
        self.lookahead_periods = lookahead_periods
        self.trading_times = trading_times
	self.acc=accuracy
	self.prevz=[]
	self.counter=0
        # Should there be a constraint that the final portfolio is the bmark?
#        self.terminal_weights = terminal_weights
        super(MultiPeriodOpt, self).__init__(*args, **kwargs)

    def get_trades(self, portfolio, t=pd.datetime.today()):
	#print self.counter, self.lookahead_periods, portfolio
	if self.lookahead_periods==1:
		self.counter+=1
		if self.counter>10000000:  #when to stop calculating for SPO
			return pd.Series(index=portfolio.index,data=self.prevz)
        value = sum(portfolio)
        assert (value > 0.)
        w = cvx.Constant(portfolio.values / value)
        ppp = cvx.Constant(portfolio.values / value)
#	ppp=
        prob_arr = []
        z_vars = []
	t1=time.time()
        for tau in \
                self.trading_times[self.trading_times.index(t):
                                   self.trading_times.index(t) +
                                   self.lookahead_periods]:
            z = cvx.Variable(*w.size)
            wplus = z
	    self.prevz=wplus

            costs, constr = [], []
            for cost in self.costs:
                cost_expr, const_expr = cost.weight_expr_ahead(tau, wplus, z, value,self.lookahead_periods,self.acc)
                costs.append(cost_expr)
                constr += const_expr

            obj = sum(costs)
            constr += [sum(z) >= 0]
            constr += [con.weight_expr(t, wplus, z, value)
                       for con in self.constraints]
            prob = cvx.Problem(cvx.Minimize(obj), constr)
            prob_arr.append(prob)
            z_vars.append(z)
            w = wplus

        sumprob=sum(prob_arr)
	solution=sumprob.solve(solver=SCS, max_iters=40000000)
	t2=time.time()
	self.foo=open("SimO.out","w")
	if z.value is None:
		print "Solver failed, with only high precision but 30M iterations, returning previous value"
		print>>self.foo, "solver failed"
		print "zzzzz", w.size,t,z.value, t2-t1,self.lookahead_periods
		print>>self.foo,w.size,t,z.value, t2-t1, self.lookahead_periods
		self.foo.close()
		print "prevz",self.prevz 
		return pd.Series(index=portfolio.index,data=self.prevz)
	else:
		xx=z_vars[0].value # * value
		print xx
		xx=xx.tolist()
		xx=[ll[0] for ll in xx]
		print "zzzzz", w.size,t,xx, t2-t1,self.lookahead_periods
		self.prevz=xx
		print>>self.foo,w.size,t,z.value.tolist(), t2-t1, self.lookahead_periods
		out=pd.Series(index=portfolio.index,data=xx)
		print "Delta Porrt",(pd.Series(index=portfolio.index,data=ppp[0].value)- pd.Series(index=portfolio.index,data=xx)).abs().sum()
		self.foo.close()
        	return out #pd.Series(index=portfolio.index,data=xx)
