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

import cvxpy as cvx
import numpy as np
import pandas as pd

from .risks import locator

__all__ = ['LongOnly','MaxOP','MinZ','MaxZ','MaxW','MaxSW']


class BaseConstraint(object):
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.w_bench = kwargs.pop('w_bench', 0.)

    def weight_expr(self, t, w_plus, z, v):
        """Returns a list of trade constraints.

        Args:
          t: time
          w_plus: post-trade weights
          z: trade weights
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
        """Returns a list of holding constraints.

        Args:
          t: time
          w_plus: holdings
        """
#	print "constraint file, w_plus long",w_plus>=0
        return sum(w_plus) > 1



class MaxOP(BaseConstraint):
    """Long-short dollar neutral strategy.
    """

    def __init__(self, **kwargs):
        super(MaxOP, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """Returns a list of holding constraints.

        Args:
          t: time
          w_plus: holdings
        """
	print "con file, w_plus MaxOP", type(w_plus<=2)
	print "second part",type(sum(w_plus)<=1.1)
        return sum(w_plus) <= 1.4



class MinZ(BaseConstraint):
    """Long-short dollar neutral strategy.
    """

    def __init__(self, **kwargs):
        super(MinZ, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """Returns a list of holding constraints.

        Args:
          t: time
          w_plus: holdings
        """
        return z >= 0


class MaxZ(BaseConstraint):
    """Long-short dollar neutral strategy.
    """

    def __init__(self, **kwargs):
        super(MaxZ, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """Returns a list of holding constraints.

        Args:
          t: time
          w_plus: holdings
        """
        return z <= 0.5



class MaxW(BaseConstraint):
    """Long-short dollar neutral strategy.
    """

    def __init__(self, **kwargs):
        super(MaxW, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """Returns a list of holding constraints.

        Args:
          t: time
          w_plus: holdings
        """
        return w_plus <=1

class MaxSW(BaseConstraint):
    """Long-short dollar neutral strategy.
    """

    def __init__(self, **kwargs):
        super(MaxSW, self).__init__(**kwargs)

    def _weight_expr(self, t, w_plus, z, v):
        """Returns a list of holding constraints.

        Args:
          t: time
          w_plus: holdings
        """
        return w_plus >= 0
