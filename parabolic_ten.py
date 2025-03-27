"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

harmonica.py

6 SAR Harmonica

Indicators:

### Parabolic SAR Setup:
- The bot calculates 6 different Parabolic SAR values, each with a different scalar to adjust 
  the sensitivity of the SAR indicator. The SAR indicator helps track price trends and detect 
  potential reversals.

### Exponential Moving Averages (EMA):
- The strategy uses 4 different EMA values with varying periods (10, 60, and 90) to smooth out 
  price data and identify the overall trend direction.

Strategy:

- **Sell** conditions:
    1. If the majority of SAR values are above the signal EMA, indicating a bearish trend.
    2. If the price has increased significantly, with a certain threshold set for the SAR relative to the trade price.
    3. If other bearish indicators are present, such as a bearish moving average crossing

- **Buy** conditions:
    1. If the majority of SAR values are below the signal EMA, indicating a bullish trend.
    2. If the price is trending upwards, confirmed by a bullish moving average crossing.
    3. The bot will only buy if the portfolio has sufficient USD balance to make the trade.
"""
import math
import time

import numpy as np
import qtradex as qx


class ParabolicSARBot(qx.BaseBot):
    def __init__(self):
        # Parameters for the SAR and moving averages
        self.tune = {
            # SAR params
            "SAR_initial": 0.02005274490409851,
            "SAR_acceleration": 0.2300077824125609,
            # SAR scalars
            "scalar_1": 1.0,
            "scalar_2": 2.0,
            "scalar_3": 3.0,
            "scalar_4": 4.0,
            "scalar_5": 5.0,
            "scalar_6": 6.0,
            "scalar_7": 7.0,
            "scalar_9": 8.0,
            "scalar_10": 9.0,
            # EMA period
            "signal_period": 2.0,
            # Integer
            "ago": 1,
            "sell": 5,
            "buy": 5,
        }

        self.clamps = [
            # min, max, strength
            # sar initial + acceleration
            [0.001, 1.0, 0.5],
            [0.001, 1.0, 0.5],
            # sar scalars
            [1, 200, 1],
            [1, 200, 1],
            [1, 200, 1],
            [1, 200, 1],
            [1, 200, 1],
            [1, 200, 1],
            [1, 200, 1],
            [1, 200, 1],
            [1, 200, 1],
            [1, 200, 1],
            [2, 30, 0.5],
            [1, 100, 1],
            [1, 10, 1],
            [1, 10, 1],
        ]

        # Initialize storage for trade details
        self.storage = {"hold": 0}

    def reset(self):
        self.storage = {"hold": 0}

    def indicators(self, data):
        """
        Calculate the Parabolic SAR and moving averages for strategy.
        """
        # Calculate the SAR values for different scalars using self.tune
        sars = np.array(
            [
                qx.tu.psar(
                    data["high"],
                    data["low"],
                    self.tune["SAR_initial"] / self.tune[f"scalar_{h}"],
                    self.tune["SAR_acceleration"] / self.tune[f"scalar_{h}"],
                )
                for h in range(1, 8)  # Iterates over scalars 1 to 7
            ]
        ).T

        # Calculate the signal (simple moving average of close prices)
        signal = qx.float_period(
            qx.tu.ema, (data["close"], self.tune["signal_period"]), (1,)
        )

        return {
            "sars": sars[self.tune["ago"] :],
            "signal": signal[self.tune["ago"] :],
        }

    def plot(self, *args):
        qx.plot(
            *args,
            (
                ("sars", "SARs", "teal", 0, "SAR Harmonica"),
                ("signal", "Signal", "tomato", 0, "SAR Harmonica"),
            ),
        )

    def strategy(self, state, indicators):
        """
        Main strategy for handling buy/sell actions based on indicators.
        """
        sars = indicators["sars"]
        signal = indicators["signal"]

        market = sum(1 for sar in sars if sar < signal)

        if market < self.tune["sell"]:
            return qx.Sell()

        if market > self.tune["buy"]:
            return qx.Buy()

        # Otherwise, do nothing
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

    bot = ParabolicSARBot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
