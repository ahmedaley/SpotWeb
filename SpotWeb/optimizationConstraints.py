"""
Created on May 29, 2019

@author: Ahmed Ali-Eldin
SpotWeb Copyright (c) 2019 The SpotWeb team, led by Dr. Ahmed Ali-Eldin and Prof. Prashant Shenoy at UMass Amherst. 
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

import cvxpy as cvx
import numpy as np
import pandas as pd

from .risks import locator

__all__ = ['LongOnly','MaxOP','MinZ']


class BaseConstraint(object):
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.w_bench = kwargs.pop('w_bench', 0.)

    def weight_expr(self, t, w_plus, z, v):
        """Returns a list of  constraints.

        Args:
          t: time
          w_plus: post-optimization weights
          z: optimization weights
          v: portfolio value
        """
        if w_plus is None:
            return self._weight_expr(t, None, z, v)
        return self._weight_expr(t, w_plus - self.w_bench, z, v)

    @abstractmethod
    def _weight_expr(self, t, w_plus, z, v):
	return NotImplemented



class LongOnly(BaseConstraint):
    """A long only constraint.
    """

    def __init__(self, **kwargs):
        x=super(LongOnly, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """returns a constraint where the Sum of the server capacity should be greater than x, where z here is equal 1.

        Args:
          t: time
          w_plus: Server Allocations
        """
        return sum(w_plus) > 1



class MaxOP(BaseConstraint):
    """Maximum over provisioning allowed in the system.
    """

    def __init__(self, **kwargs):
        super(MaxOP, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """returns a constraint where the Sum of the server capacity should be less than x, where x here is equal 2.

        Args:
          t: time
          w_plus: holdings
        """

        return sum(w_plus) <= 2


class MinZ(BaseConstraint):
    """Minimum allocation for any given market. This value should mostly by zero.
    """

    def __init__(self, **kwargs):
        super(MinZ, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """Returns a cosntraint on the minimum possible allocation for any market. It can not be less than zero for servers.

        Args:
          t: time
          w_plus: holdings
        """
        return z >= 0


class MaxZ(BaseConstraint):
    """Maximum allocation for any given market. This value allows the user to increase diversification by setting a minimum allocation
    value for a given market that can not be violated
    """

    def __init__(self, **kwargs):
        super(MaxZ, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """Maximum allocation for a given market set to 0.5, i.e., no server market should serve more than 50% of all the requests.

        Args:
          t: time
          w_plus: holdings
        """
        return z <= 0.5
