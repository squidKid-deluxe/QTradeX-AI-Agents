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
            "threshold": 1.0,
        }
        # optimizer clamps (min, initial, max, strength)
        self.clamps = {
            "ma1_period": [5, 5, 100, 1],
            "ma2_period": [10, 10.0, 150, 1],
            "threshold": [1.0, 1.0, 1.1, 1],
        }

    def indicators(self, data):
        # tulip indicators are exposed via qx.indicators.tulipy
        # and cached on backend for optimization speed
        ma1 = qx.ti.sma(data["close"], self.tune["ma1_period"])
        return {
            "top": ma1 * self.tune["threshold"],
            "bottom": ma1 / self.tune["threshold"],
            "ma2": qx.ti.sma(data["close"], self.tune["ma2_period"]),
        }

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            (
                # key, name, color, index, title
                ("top", "MA 1 Top", "white", 0, "Main"),
                ("bottom", "MA 1 Bottom", "white", 0, "Main"),
                ("ma2", "MA 2", "cyan", 0, "Main"),
            ),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()
        if indicators["bottom"] > indicators["ma2"] and isinstance(
            state["last_trade"], qx.Sell
        ):
            return qx.Buy()
        if indicators["top"] < indicators["ma2"] and isinstance(
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
    # data = qx.Data(
    #     exchange="kucoin",
    #     asset=asset,
    #     currency=currency,
    #     begin="2021-01-01",
    #     end="2025-01-01",
    # )

    # asset, currency = "TSLA", "USD"
    # wallet = qx.PaperWallet({asset: 0, currency: 1})
    # data = qx.Data(
    #     exchange="yahoo",
    #     asset=asset,
    #     currency=currency,
    #     begin="2020-02-01",
    #     end="2025-01-01",
    # )

    asset, currency = "KS11", "KRW"
    wallet = qx.PaperWallet({asset: 0, currency: 1})
    data = qx.Data(
        exchange="finance data reader",
        asset=asset,
        currency=currency,
        begin="2022-01-01",
        end="2022-12-31",
    )

    bot = EmaCross()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
