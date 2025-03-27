"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

directional_movement.py

Dirctional Movement

Indicators:

- Exponential Moving Averages (EMA):
    - Short-term EMA (default period: 10)
    - Mid-term EMA (default period: 20)
    - Long-term EMA (default period: 90)
- Directional Movement Indicators (DMI):
    - Positive Directional Movement (DM+)
    - Negative Directional Movement (DM-)
- Average Directional Index (ADX) and Average Directional Index Rating (ADXR):
    - ADX (default period: 14)
    - ADXR (default period: 14)

Strategy:

1. Moving Average Crossovers: 
   - qx.Buy when the short-term EMA crosses above the long-term EMA.
   - qx.Sell when the short-term EMA crosses below the long-term EMA.
2. Directional Movement:
   - Utilize DM+ and DM- to assess market strength and direction.
   - qx.Buy signals are generated when DM+ is significantly greater than DM-.
   - qx.Sell signals are generated when DM- is significantly greater than DM+.
3. Sideways Market Detection:
   - The bot identifies sideways markets using the slope of the long-term EMA.
   - It employs clustering logic to determine when to enter or exit trades during sideways conditions.
"""


import math
import time

import numpy as np
import qtradex as qx


class DirectionalMovement(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "short_period": 11.592640026040238,
            "mid_period": 21.58509273978805,
            "long_period": 12.987307578622156,
            "dm_period": 40.13268029378086,
            "adx_period": 10.436935163548062,
            "adxr_period": 11.954841773583773,
            "cluster_thresh": 0.10722428771472528,
            "sideways_up": 0.015042995797401927,
            "sideways_down": 0.03924366495290047,
            "minus_dm_thresh": 100.7504494785171,
            "minus_plus_dm_thresh": 67.14110610491225,
            "plus_dm_ratio": 1.1663845194059757,
            "adx_threshold": 20,
            "adx_sideways_threshold": 20,
        }

        self.clamps = [
            [5, 50, 0.5],
            [5, 50, 0.5],
            [5, 50, 0.5],
            [5, 50, 1],
            [5, 50, 1],
            [5, 50, 1],
            [0.0001, 1, 1],
            [0.0001, 1, 1],
            [0.0001, 1, 1],
            [1, 100, 0.5],
            [1, 100, 0.5],
            [0.1, 5, 1],
        ]

    def indicators(self, data):
        """
        Compute and return the necessary indicators
        """
        ma_short = qx.float_period(
            qx.tu.ema, (data["close"], self.tune["short_period"]), (1,)
        )
        ma_mid = qx.float_period(
            qx.tu.ema, (data["close"], self.tune["mid_period"]), (1,)
        )
        ma_long_ptick = qx.float_period(
            qx.tu.ema, (data["close"], self.tune["long_period"]), (1,)
        )
        ma_long = ma_long_ptick[:-1]

        # Directional Movement Indicators (DM+ and DM-)
        plus_dm, minus_dm = qx.tu.dm(data["high"], data["low"], self.tune["dm_period"])

        # ADX and ADXR
        adx = qx.tu.adx(
            data["high"], data["low"], data["close"], self.tune["adx_period"]
        )
        adxr = qx.tu.adxr(
            data["high"], data["low"], data["close"], self.tune["adxr_period"]
        )

        return {
            "ma_short": ma_short,
            "ma_mid": ma_mid,
            "ma_long": ma_long,
            "ma_long_ptick": ma_long_ptick,
            "plus_dm": plus_dm,
            "minus_dm": minus_dm,
            "adx": adx,
            "adxr": adxr,
        }

    def strategy(self, state, indicators):
        ma_short = indicators["ma_short"]
        ma_mid = indicators["ma_mid"]
        ma_long = indicators["ma_long"]
        plus_dm = indicators["plus_dm"]
        minus_dm = indicators["minus_dm"]
        adx = indicators["adx"]

        if state["last_trade"] is None:
            return qx.Buy()  # Initial buy

        buy_last = isinstance(state["last_trade"], qx.Buy)

        # Check for moving average crossovers
        if ma_short > ma_long and ma_mid < ma_long:
            if plus_dm > minus_dm and adx > self.tune["adx_threshold"]:
                if not buy_last:
                    return qx.Buy()
        elif ma_short < ma_long and ma_mid > ma_long:
            if minus_dm > plus_dm and adx > self.tune["adx_threshold"]:
                if buy_last:
                    return qx.Sell()

        # Sideways market logic
        if adx < self.tune["adx_sideways_threshold"]:
            # Implement logic for sideways market
            return None  # No action in sideways market

        return None  # Default to no action

    def plot(self, *args):
        """
        Plot the strategy with moving averages and DM indicators
        """
        qx.plot(
            *args,
            (
                ("ma_short", "Short MA", "white", 0, "Main"),
                ("ma_mid", "Mid MA", "cyan", 0, "Main"),
                ("ma_long", "Long MA", "yellow", 0, "Main"),
                ("plus_dm", "Plus DM", "green", 1, "Secondary"),
                ("minus_dm", "Minus DM", "red", 1, "Secondary"),
                ("adx", "ADX", "blue", 2, "Tertiary"),
                ("adxr", "ADXR", "purple", 2, "Tertiary"),
            ),
        )

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

    bot = DirectionalMovement()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
