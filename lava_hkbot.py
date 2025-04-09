"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

lava_hk.py

Lava HK

Indicators:

   - The bot calculates two exponential moving averages (EMAs) with different periods:
     - `ma1`: A faster-moving average with a period specified by the "ma1" tuning parameter.
     - `ma2`: A slower-moving average with a period specified by the "ma2" tuning parameter.
   - Additionally, the bot computes the OHLC4 value, which is the average of the open, high, low, and close prices.

Strategy:

   - The bot compares two values, `eq1` (start) and `eq2` (close), to determine the market mode:
     - **Bullish (1)**: When `eq2` > `eq1`, indicating an upward market trend.
     - **Bearish (-1)**: When `eq2` < `eq1`, indicating a downward market trend.
     - **Neutral (0)**: When `eq2` == `eq1`, indicating a stable or sideways market.

"""


import math
import time

import qtradex as qx


class LavaHK(qx.BaseBot):
    def __init__(self):
        # Initialize tuning parameters
        self.tune = {
            "ma1_period": 12.579159259860445,
            "ma2_period": 15.015159069473613,
        }
        # Initialize clamps (if needed for tuning parameters)
        self.clamps = {
            "ma1_period": [5, 12.579159259860445, 100, 0.5],
            "ma2_period": [10, 15.015159069473613, 150, 0.5],
        }

        self.state = {}  # To store state information (like hkopen, ohlc4, etc.)

    def indicators(self, data):
        """
        Define the indicators using QX's indicators system.
        """
        ma1 = qx.ti.ema(data["close"], self.tune["ma1_period"])
        ma2 = qx.ti.ema(data["close"], self.tune["ma2_period"])

        # OHLC4 calculation
        ohlc4 = (data["open"] + data["high"] + data["low"] + data["close"]) / 4
        return {"ma1": ma1, "ma2": ma2, "ohlc4": ohlc4}

    def strategy(self, state, indicators):
        """
        Decision making: determine whether to buy, sell, or hold.
        """
        eq1 = indicators["ohlc4"]
        eq2 = indicators["ohlc4"]  # or use another indicator for comparison if needed

        # Determine market mode
        if eq2 > eq1:
            mode = 1  # Bullish
        elif eq2 < eq1:
            mode = -1  # Bearish
        else:
            mode = 0  # Neutral

        # Example of action decision based on mode and available funds
        action = 0
        if mode == 1:  # Bullish
            if state["currency"] > (eq1 * 0.12):
                action = 1  # qx.Buy signal
        elif mode == -1:  # Bearish
            if state["assets"] > 0.12:
                action = -1  # qx.Sell signal

        # Return qx.Buy/qx.Sell actions
        if action == 1:
            return qx.Buy()
        elif action == -1:
            return qx.Sell()
        return None  # No action if conditions are not met

    def plot(self, *args):
        """
        Plot the indicators for visual feedback.
        """
        qx.plot(
            *args,
            (
                ("ma1", "MA 1", "white", 0, "Main"),
                ("ma2", "MA 2", "cyan", 0, "Main"),
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

    bot = LavaHK()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
