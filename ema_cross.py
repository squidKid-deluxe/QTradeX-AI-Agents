"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

ema_cross.py

Ema Cross

Indicators:

1. **Exponential Moving Averages (EMA)**:
   - The bot uses two exponential moving averages (EMAs) with customizable periods (`ma1` and `ma2`).
   - `ma1` and `ma2` are calculated using the Tulip Indicators (via the `tulipy.ema` function).

   - **`ma1` (short-term EMA)**: A faster-moving average, typically more responsive to price changes.
   - **`ma2` (long-term EMA)**: A slower-moving average, typically used to capture the general trend.

2. **Indicator Calculation**:
   - The EMAs are calculated using the closing prices of the asset over specified periods (`ma1` and `ma2`).
   - The `qx.float_period` function is used to compute the values of the EMAs on the given price data.

Strategy:

1. **Moving Average Crossover Strategy**:
   - The bot uses a basic moving average crossover strategy to generate buy and sell signals.
   - The core logic of the strategy is:
     - **qx.Buy Signal**: When `ma1` (short-term EMA) crosses above `ma2` (long-term EMA),
     - **qx.Sell Signal**: When `ma1` (short-term EMA) crosses below `ma2` (long-term EMA), 
"""


import math
import time

import numpy as np
import qtradex as qx


class EmaCross(qx.BaseBot):
    def __init__(self):
        # tune values (moving averages)
        self.tune = {
            "ma1_period": 5,
            "ma2_period": 10.0,
        }
        # optimizer clamps (min, max, strength)
        self.clamps = [
            [5, 100, 1],  # For ma1
            [10, 150, 1],  # For ma2
        ]

    def indicators(self, data):
        # tulip indicators are exposed via qx.indicators.tulipy
        # and cached on backend for optimization speed
        return {
            "ma1": qx.float_period(
                qx.tu.ema,
                (data["close"], self.tune["ma1_period"]),
                (1,),
            ),
            "ma2": qx.float_period(
                qx.tu.ema,
                (data["close"], self.tune["ma2_period"]),
                (1,),
            ),
        }

    def plot(self, *args):
        qx.plot(
            *args,
            (
                # key, name, color, index, title
                ("ma1", "MA 1", "white", 0, "Main"),
                ("ma2", "MA 2", "cyan", 0, "Main"),
            ),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()
        if indicators["ma1"] > indicators["ma2"] and isinstance(
            state["last_trade"], qx.Sell
        ):
            return qx.Buy()
        if indicators["ma1"] < indicators["ma2"] and isinstance(
            state["last_trade"], qx.Buy
        ):
            return qx.Sell()
        return None

    def fitness(self, states, raw_states, asset, currency):
        return [
            "roi_gross",
            "sortino_ratio",
            "trade_win_rate",
        ], {}


def main():
    asset, currency = "BTC", "USDT"
    wallet = qx.PaperWallet({asset: 0, currency: 1})
    data = qx.Data(
        exchange="kucoin",
        asset=asset,
        currency=currency,
        begin="2021-01-01",
        end="2023-01-01",
    )

    bot = EmaCross()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
