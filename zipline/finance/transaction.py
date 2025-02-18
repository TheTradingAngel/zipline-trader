#
# Copyright 2015 Quantopian, Inc.
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
from __future__ import division

from copy import copy

from zipline.assets import Asset
from zipline.protocol import DATASOURCE_TYPE
from zipline.utils.input_validation import expect_types


class Transaction(object):
    @expect_types(asset=Asset)
    def __init__(self, asset, amount, dt, price, order_id, take_profit_price=None, stop_loss_price=None):
        self.asset = asset
        self.amount = amount
        self.dt = dt
        self.price = price
        self.order_id = order_id
        self.type = DATASOURCE_TYPE.TRANSACTION
        self.take_profit_price = take_profit_price
        self.stop_loss_price = stop_loss_price

    def __getitem__(self, name):
        return self.__dict__[name]

    def __repr__(self):
        template = (
            "{cls}(asset={asset}, dt={dt},"
            " amount={amount}, price={price}, take_profit_price={tpp}, stop_loss_price={slp})"
        )

        return template.format(
            cls=type(self).__name__,
            asset=self.asset,
            dt=self.dt,
            amount=self.amount,
            price=self.price,
            tpp=self.take_profit_price,
            slp=self.stop_loss_price,
        )

    def to_dict(self):
        py = copy(self.__dict__)
        del py['type']
        del py['asset']

        # Adding 'sid' for backwards compatibility with downstrean consumers.
        py['sid'] = self.asset

        # If you think this looks dumb, that is because it is! We once stored
        # commission here, but haven't for over a year. I don't want to change
        # the perf packet structure yet.
        py['commission'] = None

        return py


def create_transaction(order, dt, price, amount):
    return Transaction(
        asset=order.asset,
        amount=float(amount),
        dt=dt,
        price=price,
        order_id=order.id,
        take_profit_price=order.exit_take_profit_price,
        stop_loss_price=order.exit_stop_loss_price,
    )
