"""
Created on Nov 28, 2018

@author: Ahmed Ali-Eldin
SpotWeb Copyright (c) 2019 The SpotWeb team, led by Ahmed Ali-Eldin and Prashant Shenoy at UMass Amherst. 
All Rights Reserved.
# 
# This product is licensed to you under the Apache 2.0 license (the "License").
# You may not use this product except in compliance with the Apache 2.0
# License.
# 
# This product may include a number of subcomponents with separate copyright
# notices and license terms. Your use of these subcomponents is subject to the
# terms and conditions of the subcomponent's license, as noted in the LICENSE
# file.

The code is based the code of CVXPortfolio by Stephen Boyd, Enzo Busseti, Steven Diamond, BlackRock Inc.
Licensed under the Apache License, Version 2.0.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file implements the cost models for both server provisioning and SLA violations.
"""

from abc import abstractmethod

import cvxpy as cvx
import numpy as np
import pandas as pd
import datetime as dt
from optimizationCosts import BaseCost

__all__ = ['FullSigma', 'RobustSigma']


def locator(obj, t):
    """Picks last element before t."""
    try:
        if isinstance(obj, pd.Panel):
            return obj.iloc[obj.axes[0].get_loc(t, method='pad')]

        elif isinstance(obj.index, pd.MultiIndex):
            prev_t = obj.loc[:t, :].index.values[-1][0]
        else:
            return obj#.loc[prev_t, :]

    except AttributeError:  # obj not pandas
        return obj


class BaseRiskModel(BaseCost):

    def __init__(self, **kwargs):
        self.w_bench = kwargs.pop('w_bench', 0.)
        super(BaseRiskModel, self).__init__()
        self.gamma_half_life = kwargs.pop('gamma_half_life', np.inf)

    def weight_expr(self, t, w_plus, z, value):
        self.expression = self._estimate(t, w_plus, z, value)
        return self.gamma * self.expression, []

    @abstractmethod
    def _estimate(self, t, w_plus, z, value):
        return NotImplemented

    def weight_expr_ahead(self, t, tau, w_plus, z, value):
        """Estimate risk model at time tau in the future."""
        if self.gamma_half_life == np.inf:
            gamma_multiplier = 1.
        else:
            decay_factor = 2 ** (-1 / self.gamma_half_life)
            # TODO not dependent on days
            gamma_init = decay_factor ** ((tau - t).days)
            gamma_multiplier = gamma_init * \
                (1 - decay_factor) / (1 - decay_factor)
        return gamma_multiplier * self.weight_expr(t, w_plus, z, value)[0], []

    def optimization_log(self, t):
        if self.expression.value:
            return self.expression.value
        else:
            return np.NaN


class FullSigma(BaseRiskModel):
    """Quadratic risk model with full covariance matrix.

    Args:
        Sigma (:obj:`pd.Panel`): Panel of Sigma matrices,
            or single matrix.

    """

    def __init__(self, Sigma, **kwargs):
        self.Sigma = Sigma  # Sigma is either a matrix or a pd.Panel
        try:
            assert(not pd.isnull(Sigma).values.any())
        except AttributeError:
            assert (not pd.isnull(Sigma).any())
        super(FullSigma, self).__init__(**kwargs)

    def _estimate(self, t, wplus, z, value):
        self.expression = cvx.quad_form(z, locator(self.Sigma, t+dt.timedelta(hours=1)).values)        
        return self.expression






class RobustSigma(BaseRiskModel):
    """Implements covariance forecast error risk."""

    def __init__(self, Sigma, epsilon, **kwargs):
        self.Sigma = Sigma  # pd.Panel or matrix
        self.epsilon = epsilon  # pd.Series or scalar
        super(RobustSigma, self).__init__(**kwargs)

    def _estimate(self, t, wplus, z, value):
        testing=locator(self.Sigma, t)
        
        
        self.expression = cvx.quad_form(wplus, self.Sigma) + \
            locator(self.epsilon, t) * \
            (cvx.abs(wplus).T * np.diag(self.Sigma))**2

        return self.expression


