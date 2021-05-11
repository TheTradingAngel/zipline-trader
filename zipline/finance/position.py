#
# Copyright 2018 Quantopian, Inc.
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

"""
Position Tracking
=================

    +-----------------+----------------------------------------------------+
    | key             | value                                              |
    +=================+====================================================+
    | asset           | the asset held in this position                    |
    +-----------------+----------------------------------------------------+
    | amount          | whole number of shares in the position             |
    +-----------------+----------------------------------------------------+
    | last_sale_price | price at last sale of the asset on the exchange    |
    +-----------------+----------------------------------------------------+
    | cost_basis      | the volume weighted average price paid per share   |
    +-----------------+----------------------------------------------------+

"""

from __future__ import division
from math import copysign
import numpy as np
import logbook

from zipline.assets import Future
import zipline.protocol as zp
from zipline.finance.execution import asymmetric_round_price
from zipline.finance.order import Order

log = logbook.Logger('Performance')


class Position(object):
    __slots__ = 'inner_position', 'protocol_position'

    def __init__(self,
                 asset,
                 amount=0.,
                 cost_basis=0.0,
                 last_sale_price=0.0,
                 last_sale_date=None,
                 take_profit_price=0.,
                 stop_loss_price=0.):
        inner = zp.InnerPosition(
            asset=asset,
            amount=amount,
            cost_basis=cost_basis,
            last_sale_price=last_sale_price,
            last_sale_date=last_sale_date,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
        )
        object.__setattr__(self, 'inner_position', inner)
        object.__setattr__(self, 'protocol_position', zp.Position(inner))

    def __getattr__(self, attr):
        return getattr(self.inner_position, attr)

    def __setattr__(self, attr, value):
        setattr(self.inner_position, attr, value)

    def earn_dividend(self, dividend):
        """
        Register the number of shares we held at this dividend's ex date so
        that we can pay out the correct amount on the dividend's pay date.
        """
        return {
            'amount': self.amount * dividend.amount
        }

    def earn_stock_dividend(self, stock_dividend):
        """
        Register the number of shares we held at this dividend's ex date so
        that we can pay out the correct amount on the dividend's pay date.
        """
        return {
            'payment_asset': stock_dividend.payment_asset,
            'share_count': np.floor(
                self.amount * float(stock_dividend.ratio)
            )
        }

    def handle_split(self, asset, ratio):
        """
        Update the position by the split ratio, and return the resulting
        fractional share that will be converted into cash.

        Returns the unused cash.
        """
        if self.asset != asset:
            raise Exception("updating split with the wrong asset!")

        # adjust the # of shares by the ratio
        # (if we had 100 shares, and the ratio is 3,
        #  we now have 33 shares)
        # (old_share_count / ratio = new_share_count)
        # (old_price * ratio = new_price)

        # e.g., 33.333
        raw_share_count = self.amount / float(ratio)

        # e.g., 33
        full_share_count = np.floor(raw_share_count)

        # e.g., 0.333
        fractional_share_count = raw_share_count - full_share_count

        # adjust the cost basis to the nearest cent, e.g., 60.0
        new_cost_basis = round(self.cost_basis * ratio, 2)

        self.cost_basis = new_cost_basis
        self.amount = full_share_count

        return_cash = round(float(fractional_share_count * new_cost_basis), 2)

        log.info("after split: " + str(self))
        log.info("returning cash: " + str(return_cash))

        # Process exit levels in a similar way to Order.handle_split
        if self.take_profit_price != 0.:
            self.take_profit_price = round(self.take_profit_price * ratio, 2)
        if self.stop_loss_price != 0.:
            self.stop_loss_price = round(self.stop_loss_price * ratio, 2)

        # return the leftover cash, which will be converted into cash
        # (rounded to the nearest cent)
        return return_cash

    def update(self, txn):
        if self.asset != txn.asset:
            raise Exception('updating position with txn for a '
                            'different asset')

        total_shares = self.amount + txn.amount

        if abs(total_shares) < 1e-3:
            self.cost_basis = 0.0
            self.take_profit_price = 0.
            self.stop_loss_price = 0.
        else:
            prev_direction = copysign(1, self.amount)
            txn_direction = copysign(1, txn.amount)

            if prev_direction != txn_direction:
                # we're covering a short or closing a position
                if abs(txn.amount) > abs(self.amount):
                    # we've closed the position and gone short
                    # or covered the short position and gone long
                    self.cost_basis = txn.price
            else:
                prev_cost = self.cost_basis * self.amount
                txn_cost = txn.amount * txn.price
                total_cost = prev_cost + txn_cost
                self.cost_basis = total_cost / total_shares

            # Update the last sale price if txn is
            # best data we have so far
            if self.last_sale_date is None or txn.dt > self.last_sale_date:
                self.last_sale_price = txn.price
                self.last_sale_date = txn.dt

            # Update take profit and stop loss prices if given
            self.update_exit_prices(
                take_profit_price=txn.take_profit_price, stop_loss_price=txn.stop_loss_price, amount=total_shares,
                last_sale_price=self.last_sale_price)

        self.amount = total_shares

    def update_exit_prices(self, take_profit_price=None, stop_loss_price=None, amount=None, last_sale_price=None):
        if amount is None:
            amount = self.amount

        resulting_direction = copysign(1, amount)
        if take_profit_price is not None:
            if self.take_profit_price != 0 and last_sale_price is not None and \
                    resulting_direction*take_profit_price < resulting_direction*last_sale_price:
                raise ValueError('Take profit price should be better than last price: '
                                 'T/P %r < %r' % (take_profit_price, last_sale_price))

            self.take_profit_price = asymmetric_round_price(take_profit_price, not amount > 0, self.asset.tick_size)

        if stop_loss_price is not None:
            if self.stop_loss_price != 0 and last_sale_price is not None and \
                    resulting_direction*stop_loss_price > resulting_direction*last_sale_price:
                raise ValueError('Stop loss price should be worse than last price: '
                                 'S/L %r > %r' % (stop_loss_price, last_sale_price))

            self.stop_loss_price = asymmetric_round_price(stop_loss_price, amount > 0, self.asset.tick_size)

    def get_exit_orders(self):
        # Stop loss and take profit orders have to be separated, because a stop-limit order behaves differently than two
        # separate stop and limit orders
        exit_orders = []
        if self.stop_loss_price != 0:
            exit_orders += [Order(
                self.last_sale_date,
                self.asset,
                -self.amount,
                stop=self.stop_loss_price or None,
            )]

        if self.take_profit_price != 0:
            exit_orders += [Order(
                self.last_sale_date,
                self.asset,
                -self.amount,
                limit=self.take_profit_price or None,
            )]

        return exit_orders

    def adjust_commission_cost_basis(self, asset, cost):
        """
        A note about cost-basis in zipline: all positions are considered
        to share a cost basis, even if they were executed in different
        transactions with different commission costs, different prices, etc.

        Due to limitations about how zipline handles positions, zipline will
        currently spread an externally-delivered commission charge across
        all shares in a position.
        """

        if asset != self.asset:
            raise Exception('Updating a commission for a different asset?')
        if cost == 0.0:
            return

        # If we no longer hold this position, there is no cost basis to
        # adjust.
        if self.amount == 0:
            return

        # We treat cost basis as the share price where we have broken even.
        # For longs, commissions cause a relatively straight forward increase
        # in the cost basis.
        #
        # For shorts, you actually want to decrease the cost basis because you
        # break even and earn a profit when the share price decreases.
        #
        # Shorts are represented as having a negative `amount`.
        #
        # The multiplication and division by `amount` cancel out leaving the
        # cost_basis positive, while subtracting the commission.

        prev_cost = self.cost_basis * self.amount
        if isinstance(asset, Future):
            cost_to_use = cost / asset.price_multiplier
        else:
            cost_to_use = cost
        new_cost = prev_cost + cost_to_use
        self.cost_basis = new_cost / self.amount

    def __repr__(self):
        template = "asset: {asset}, amount: {amount}, cost_basis: {cost_basis}, \
last_sale_price: {last_sale_price}, take_profit_price: {take_profit_price}, stop_loss_price: {stop_loss_price}"
        return template.format(
            asset=self.asset,
            amount=self.amount,
            cost_basis=self.cost_basis,
            last_sale_price=self.last_sale_price,
            take_profit_price=self.take_profit_price,
            stop_loss_price=self.stop_loss_price,
        )

    def to_dict(self):
        """
        Creates a dictionary representing the state of this position.
        Returns a dict object of the form:
        """
        return {
            'sid': self.asset,
            'amount': self.amount,
            'cost_basis': self.cost_basis,
            'last_sale_price': self.last_sale_price,
            'take_profit_price': self.take_profit_price,
            'stop_loss_price': self.stop_loss_price,
        }
