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

from abc import ABCMeta, abstractmethod, abstractproperty
import pandas as pd


class Broker(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_metrics_tracker(self, metrics_tracker):
        pass

    @abstractmethod
    def subscribe_to_market_data(self, asset):
        pass

    def set_minutes_index(self, calendar, tds: pd.DatetimeIndex):
        pass

    @property
    @abstractmethod
    def subscribed_assets(self):
        pass

    @property
    @abstractmethod
    def positions(self):
        pass

    @property
    @abstractmethod
    def portfolio(self):
        pass

    @property
    @abstractmethod
    def account(self):
        pass

    @property
    @abstractmethod
    def time_skew(self):
        pass

    @abstractmethod
    def order(self, asset, amount, style):
        pass

    @abstractmethod
    def update_exit_prices(self, asset, take_profit_price=None, stop_loss_price=None):
        pass

    def is_alive(self):
        pass

    @property
    @abstractmethod
    def orders(self):
        pass

    @property
    @abstractmethod
    def transactions(self):
        pass

    @abstractmethod
    def cancel_order(self, order_param):
        pass

    @abstractmethod
    def get_last_traded_dt(self, asset):
        pass

    @abstractmethod
    def get_spot_value(self, assets, field, dt, data_frequency):
        pass

    @abstractmethod
    def get_realtime_bars(self, assets, frequency, bar_count=None):
        pass
