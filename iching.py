"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

iching.py

I Ching

Indicators:

    For each EMA, the code calculates its slope by deriving the rate of change in price 
    using the qx.derivative and indicators.tulipy.ema functions.
    These slopes are then used to form a "hexagram" (a 6-dimensional binary array), 
    which represents the combination of slopes for each EMA.
    The hexagram helps in determining the action (buy/sell/no action) using a binary string.

Strategy:

    The strategy decides on whether to buy or sell based on the most recent hexagram.
    The hexagram (a 6-dimensional binary vector) is converted into a binary string, 
    which is used to lookup a corresponding action in self.tune. The action is then either to:
        qx.Buy if the action is 1
        qx.Sell if the action is -1
        No action if the action is 0

"""


import math
import time

import numpy as np
import qtradex as qx


class IChing(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "ma1_period": 5.0,
            "ma2_period": 10.0,
            "ma3_period": 20.0,
            "ma4_period": 40.0,
            "ma5_period": 80.0,
            "ma6_period": 100.0,
        }

        # Add 64 ternary flags (-1 = sell, 0 = no action, 1 = buy) to the tune dict
        for i in range(64):  # 64 flags
            self.tune[
                bin(i)[2:].rjust(6, "0")
            ] = 0  # np.random.choice([-1, 0, 1])  # Randomly assign -1, 0, or 1

        self.clmps = [
            *[[5.0, 100.0, 0.5] for _ in range(6)],
            *[[-1, 1, 1] for _ in range(64)],
        ]

    def autorange(self):
        return max(math.ceil(i) for i in self.tune.values()) + 1

    def indicators(self, data):
        ema_values = {
            f"ma{i}_slope": qx.derivative(
                qx.ti.ema(data["close"], self.tune[f"ma{i}_period"])
            )
            for i in range(1, 7)
        }

        # Ensure all EMA arrays are the same length
        ema_lists = qx.truncate(*[ema_values[f"ma{i}_slope"] for i in range(1, 7)])
        ema_values.update({f"ma{i}_slope": ema_lists[i - 1] for i in range(1, 7)})

        # Create slope vector with 64 possible combinations of slopes
        hexagram = np.array(
            [
                [1 if ema_values[f"ma{i}_slope"][j] > 0 else 0 for i in range(1, 7)]
                for j, _ in enumerate(ema_values["ma1_slope"])
            ]
        )

        return {**ema_values, "hexagram": hexagram}

    def plot(self, *args):
        qx.plot(
            *args,
            tuple(
                (f"ma{idx}_slope", f"MA {idx} Slope", color, 1, "Slope")
                for idx, color in enumerate(
                    ["white", "cyan", "green", "yellow", "red", "blue"], start=1
                )
            ),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()

        # Convert the hexagram to a binary number (decimal)
        hexagram = indicators["hexagram"]  # Get the first (or current) vector
        binary_string = "".join(
            str(x) for x in hexagram
        )  # Convert list to binary string

        # Look up the corresponding ternary value in the tune dictionary
        action = self.tune.get(
            binary_string, 0
        )  # Default to no action (0) if out of bounds

        if action == -1:
            return qx.Sell()  # Vote for qx.Sell
        elif action == 0:
            return None  # No Action
        elif action == 1:
            return qx.Buy()  # Vote for qx.Buy
        return None  # Default no action if none of the cases match

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
        # end="2023-01-01",
    )
    dta = qx.public.utilities.fetch_composite_data(data, 60 * 30)

    bot = IChing()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
