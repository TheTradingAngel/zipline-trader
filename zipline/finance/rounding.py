#
# Copyright 2016 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import abc

from abc import abstractmethod
from six import with_metaclass

from zipline.utils.math_utils import round_if_near_integer


class OrderRounding(with_metaclass(abc.ABCMeta)):
    """Abstract order amount rounding interface.
    """

    @abstractmethod
    def round_order(self, amount: float) -> float:
        pass


class FullSharesRounding(OrderRounding):
    """Rounding to full shares: represents the original zipline behavior"""

    def round_order(self, amount: float) -> float:
        return int(round_if_near_integer(amount))


class FractionalSharesRounding(OrderRounding):
    """Round to the nearest fractional shares given precision."""

    def __init__(self, precision: float = .01):
        self._precision = precision

    def round_order(self, amount: float) -> float:
        return int(round_if_near_integer(amount/self._precision))*self._precision
