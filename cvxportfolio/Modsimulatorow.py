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

import copy
import logging
import time
import inspect

import multiprocess
import numpy as np
import pandas as pd
import cvxpy as cvx

from Modreturnsoldworking import MultipleReturnsForecasts

from resultoldworking import SimulationResult
from Modcostsoldworking import BaseCost

# TODO update benchmark weights (?)
# Also could try jitting with numba.


class MarketSimulator():
    logger = None

    def __init__(self, costs,failures): #cash_key='cash'):
        """Provide market returns object and cost objects."""
        #self.market_returns = market_returns
        self.failures=failures
       # if market_volumes is not None:
        #    self.market_volumes = market_volumes[
         #       market_volumes.columns.difference([cash_key])]
       # else:
        #    self.market_volumes = None
        
        print inspect.stack()[1]
        self.costs = costs
        for cost in self.costs:
            print "cost in sim.py", type(cost), self.costs
            assert (isinstance(cost, BaseCost))

#        self.cash_key = cash_key

    def propagate(self, h, u, t, LA, acc):
        """Propagates the portfolio forward over time period t, given trades u.

        Args:
            h: padas Series object describing current portfolio
            u: n vector with the stock trades (not cash)
            t: current time

        Returns:
            h_next: portfolio after returns propagation
            u: trades vector with simulated cash balance
        """
        assert (u.index.equals(h.index))
        hplus = u
	print "hplus", LA,t,hplus
        costs = [cost.value_expr(t, h_plus=hplus, u=u,LA=LA,acc=acc) for cost in self.costs]
        for cost in costs:
           assert(not pd.isnull(cost))
           assert(not np.isinf(cost))
	print "Cost", costs, acc
        h_next =  hplus

        assert (not h_next.isnull().values.any())
        assert (not u.isnull().values.any())
        return h_next, u

    def run_backtest(self, initial_portfolio, start_time, end_time,
                     policy, loglevel=logging.WARNING):
        """Backtest a single policy.
        """
        logging.basicConfig(level=loglevel)

        results = SimulationResult(initial_portfolio=copy.copy(initial_portfolio), policy=policy, simulator=self)
        h = initial_portfolio
	print "Modsimulator run+backtest"
        simulation_times = self.failures.index[
            (self.failures.index >= start_time) &
            (self.failures.index <= end_time)]
        logging.info('Backtest started, from %s to %s' %
                     (simulation_times[0], simulation_times[-1]))

        for t in simulation_times:
            logging.info('Getting trades at time %s' % t)
            start = time.time()
	    print "Modsimulator t",type(t), t
            try:
                u = policy.get_trades(h, t)
		print "debugging", u
            except cvx.SolverError as e:
                logging.warning(
                    'Solver failed on timestamp %s. Default to no trades.' % t)
                raise e
		u = pd.Series(index=h.index, data=0.)
            end = time.time()
            assert (not pd.isnull(u).any())
            results.log_policy(t, end - start)
            logging.info('Propagating portfolio at time %s' % t, u)
            start = time.time()
            h, u = self.propagate(h, u, t,policy.lookahead_periods,policy.acc)
            end = time.time()
            assert (not h.isnull().values.any())
            results.log_simulation(t=t, u=u, h_next=h,
                                   risk_free_return=None,
                                   exec_time=end - start)
	
        logging.info('Backtest ended, from %s to %s' %
                     (simulation_times[0], simulation_times[-1]))
        return results

    def run_multiple_backtest(self, initial_portf, start_time,
                              end_time, policies,
                              loglevel=logging.WARNING, parallel=True):
        """Backtest multiple policies.
        """

        def _run_backtest(policy):
            return self.run_backtest(initial_portf, start_time, end_time,
                                     policy, loglevel=loglevel)

        num_workers = min(multiprocess.cpu_count(), len(policies))
        if parallel:
            workers = multiprocess.Pool(num_workers)
            results = workers.map(_run_backtest, policies)
            workers.close()
            return results
        else:
            return list(map(_run_backtest, policies))

    def what_if(self, time, results, alt_policies, parallel=True):
        """Run alternative policies starting from given time.
        """
        # TODO fix
        initial_portf = copy.copy(results.h.loc[time])
        all_times = results.h.index
        alt_results = self.run_multiple_backtest(initial_portf,
                                                 time,
                                                 all_times[-1],
                                                 alt_policies, parallel)
        for idx, alt_result in enumerate(alt_results):
            alt_result.h.loc[time] = results.h.loc[time]
            alt_result.h.sort_index(axis=0, inplace=True)
        return alt_results

    @staticmethod
    def reduce_signal_perturb(initial_weights, delta):
        """Compute matrix of perturbed weights given initial weights."""
        perturb_weights_matrix = \
            np.zeros((len(initial_weights), len(initial_weights)))
        for i in range(len(initial_weights)):
            perturb_weights_matrix[i, :] = initial_weights / \
                (1 - delta * initial_weights[i])
            perturb_weights_matrix[i, i] = (1 - delta) * initial_weights[i]
        return perturb_weights_matrix

    def attribute(self, true_results, policy,
                  selector=None,
                  delta=1,
                  fit="linear",
                  parallel=True):
        """Attributes returns over a period to individual alpha sources.

        Args:
            true_results: observed results.
            policy: the policy that achieved the returns.
                    Alpha model must be a stream.
            selector: A map from SimulationResult to time series.
            delta: the fractional deviation.
            fit: the type of fit to perform.
        Returns:
            A dict of alpha source to return series.
        """
        # Default selector looks at profits.
        if selector is None:
            def selector(result):
                return result.v - sum(result.initial_portfolio)

        alpha_stream = policy.return_forecast
        assert isinstance(alpha_stream, MultipleReturnsForecasts)
        times = true_results.h.index
        weights = alpha_stream.weights
        assert np.sum(weights) == 1
        alpha_sources = alpha_stream.alpha_sources
        num_sources = len(alpha_sources)
        Wmat = self.reduce_signal_perturb(weights, delta)
        perturb_pols = []
        for idx in range(len(alpha_sources)):
            new_pol = copy.copy(policy)
            new_pol.return_forecast = MultipleReturnsForecasts(alpha_sources,
                                                               Wmat[idx, :])
            perturb_pols.append(new_pol)
        # Simulate
        p0 = true_results.initial_portfolio
        alt_results = self.run_multiple_backtest(p0, times[0], times[-1],
                                                 perturb_pols, parallel)
        # Attribute.
        true_arr = selector(true_results).values
        attr_times = selector(true_results).index
        Rmat = np.zeros((num_sources, len(attr_times)))
        for idx, result in enumerate(alt_results):
            Rmat[idx, :] = selector(result).values
        Pmat = cvx.Variable((num_sources, len(attr_times)))
        if fit == "linear":
            prob = cvx.Problem(cvx.Minimize(0), [Wmat * Pmat == Rmat])
            prob.solve()
        elif fit == "least-squares":
            error = cvx.sum_squares(Wmat * Pmat - Rmat)
            prob = cvx.Problem(cvx.Minimize(error),
                               [Pmat.T * weights == true_arr])
            prob.solve()
        else:
            raise Exception("Unknown fitting method.")
        # Dict of results.
        wmask = np.tile(weights[:, np.newaxis], (1, len(attr_times))).T
        data = pd.DataFrame(columns=[s.name for s in alpha_sources],
                            index=attr_times,
                            data=Pmat.value.T * wmask)
        data['residual'] = true_arr - np.matrix((weights * Pmat).value).A1
        data['RMS error'] = np.matrix(
            cvx.norm(Wmat * Pmat - Rmat, 2, axis=0).value).A1
        data['RMS error'] /= np.sqrt(num_sources)
        return data
