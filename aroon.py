"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

aroon.py

Aroon

Indicators and Strategy for Bot

Indicators:
1. **Aroon Oscillator**:
   - The bot uses the Aroon Oscillator (Aroon Osc) to identify the strength of a trend.
   - The Aroon Oscillator is calculated using the high and low prices over a specified period (`aroon_period`).
   - The Aroon Oscillator is a momentum indicator that ranges between -100 and +100, where:
     - Positive values indicate that the asset is in an uptrend.
     - Negative values indicate that the asset is in a downtrend.
   - The Aroon Oscillator is used to determine the potential buy or sell points based on whether 
   the oscillator crosses certain threshold values (`buy_thresh` and `sell_thresh`).

Strategy:
1. **Aroon Oscillator Strategy**:
   - The bot utilizes the Aroon Oscillator to identify market conditions and make trading decisions 
   based on specific threshold values.
   
   - **qx.Buy Signal**: 
     - The bot triggers a buy when the Aroon Oscillator value is below the specified `buy_thresh` 
     (e.g., -50), indicating that the market is in a potential uptrend.


   - **qx.Sell Signal**:
     - The bot triggers a sell when the Aroon Oscillator value is above the specified `sell_thresh` 
     (e.g., +50), indicating that the market is in a potential downtrend.
"""


import math
import time

import numpy as np
import qtradex as qx


class Aroon(qx.BaseBot):
    def __init__(self):
        self.tune = {"aroon_period": 15.0, "sell_thresh": 50.0, "buy_thresh": 50.0}
        self.tune = {
            "aroon_period": 18.23944232459082,
            "sell_thresh": 2.512268085738901,
            "buy_thresh": 1.150776158276998,
        }

        self.clamps = [
            # min, max, strength
            [5, 50, 1],
            [1, 100, 1],
            [1, 100, 1],
        ]

    def indicators(self, data):
        # tulip indicators are exposed via qx.indicators.tulipy
        # and cached on backend for optimization speed
        return {
            "aroon_osc": qx.float_period(
                qx.tu.aroonosc,
                (data["high"], data["low"], self.tune["aroon_period"]),
                (2,),
            ),
        }

    def plot(self, data, states, indicators, block):
        qx.plot(
            data,
            states,
            indicators,
            block,
            (("aroon_osc", "Aroon Oscillator", "green", 1, "Osc"),),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()
        if indicators["aroon_osc"] < -self.tune["sell_thresh"] and isinstance(
            state["last_trade"], qx.Buy
        ):
            return qx.Sell()
        if indicators["aroon_osc"] > self.tune["buy_thresh"] and isinstance(
            state["last_trade"], qx.Sell
        ):
            return qx.Buy()
        return None

    def fitness(self, states, raw_states, asset, currency):
        return ["roi", "sharpe"], {}


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

    bot = Aroon()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
