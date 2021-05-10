.. image:: https://readthedocs.org/projects/zipline-trader/badge/?version=latest
   :target: https://zipline-trader.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://github.com/shlomikushchi/zipline-trader/workflows/Zipline%20CI%20(Ubuntu)/badge.svg
   :target: https://github.com/shlomikushchi/zipline-trader/workflows/Zipline%20CI%20(Ubuntu)/badge.svg
   :alt: Github Actions
.. image:: https://github.com/shlomikushchi/zipline-trader/workflows/Zipline%20CI%20(Windows)/badge.svg
   :target: https://github.com/shlomikushchi/zipline-trader/workflows/Zipline%20CI%20(Windows)/badge.svg
   :alt: Github Actions
.. image:: https://github.com/shlomikushchi/zipline-trader/workflows/Zipline%20CI%20(macOS)/badge.svg
   :target: https://github.com/shlomikushchi/zipline-trader/workflows/Zipline%20CI%20(macOS)/badge.svg
   :alt: Github Actions

|

.. image:: ./images/zipline-live2.small.png
    :target: https://github.com/shlomikushchi/zipline-trader
    :width: 212px
    :align: center
    :alt: zipline-live

zipline-trader
==============

Welcome to zipline-trader, the on-premise trading platform built on top of Quantopian's
`zipline <https://github.com/quantopian/zipline>`_.

This project is meant to be used for backtesting/paper/live trading with one the following brokers:
 * Interactive Brokers
 * Alpaca


Please `Read The Docs <https://zipline-trader.readthedocs.io/en/latest/index.html#>`_

And you could find us on `slack <https://join.slack.com/t/zipline-live/shared_invite/zt-mrsrfhky-usB0SEU4st1SuMUCErUevA>`_

Zipline Trader Modifications
================

Zipline Trader has been modified in the following ways:

- Support for fractional shares
- Correction of order fill behavior for stop-limit orders
- Support for setting exit stop loss and take profit levels on the position

Installation for development
----------------------------

.. code-block:: bash

    conda create --name zipline_dev python=3.6
    conda activate zipline_dev
    conda install -c conda-forge bcolz=1.2.1 psycopg2=2.8.6 numpy scipy h5py=2.10.0
    pip install -e .
