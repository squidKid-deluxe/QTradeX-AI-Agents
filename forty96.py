"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

forty96.py

4096 Ternary Parameter Trader

Indicators:

    For each EMA, the code calculates its value and slope (rate of change in price)
    using the qx.tu.ema and qx.derivative functions. The values and slopes are then
    used to form a "hexagram" (a 12-dimensional dictionary), which represents the
    combination of conditions based on the price and EMAs.

    The hexagram helps in determining the action (buy/sell/no action) using a binary
    string derived from the conditions defined in the hexagram.

Strategy:

    The strategy decides on whether to buy or sell based on the most recent hexagram.
    The hexagram (a 12-dimensional dictionary) is evaluated to create a binary string,
    which is used to look up a corresponding action in self.tune. The action is then either to:
        qx.Buy if the action is 1
        qx.Sell if the action is -1
        No action if the action is 0

Tuning:

    The bot maintains a tuning dictionary with 4096 ternary flags (-1 = sell, 0 = no action, 1 = buy)
    that can be adjusted based on performance metrics. The tuning parameters include the periods
    for the three EMAs.

Fitness Evaluation:

    The fitness method evaluates the bot's performance based on metrics such as gross ROI,
    Sortino ratio, and trade win rate, allowing for assessment and potential adjustments to the strategy.
"""

import math
import time

import numpy as np
import qtradex as qx


class Forty96(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "ma1_period": 5.0,
            "ma2_period": 10.0,
            "ma3_period": 20.0,
        }

        # Add 4096 ternary flags (-1 = sell, 0 = no action, 1 = buy) to the tune dict
        for i in range(4096):  # 2^12 flags
            self.tune[bin(i)[2:].rjust(12, "0")] = 0  # Initialize with no action

        # self.tune = TUNE

        self.clamps = [
            *[[5.0, 100.0, 0.5] for _ in range(3)],
            *[[-1, 1, 1] for _ in range(4096)],
        ]

    def autorange(self):
        return max(math.ceil(i) for i in self.tune.values()) + 1

    def indicators(self, data):
        ema_values = {
            f"ma{i}": qx.tu.ema(data["close"], self.tune[f"ma{i}_period"])
            for i in range(1, 4)
        }
        ema_slopes = {
            f"ma{i}_slope": qx.derivative(
                qx.float_period(
                    qx.tu.ema,
                    (data["close"], self.tune[f"ma{i}_period"]),
                    (1,),
                )
            )
            for i in range(1, 4)
        }

        minlen = min(map(len, [*ema_values.values(), *ema_slopes.values()]))

        ema_values = {k: v[:minlen] for k, v in ema_values.items()}
        ema_slopes = {k: v[:minlen] for k, v in ema_slopes.items()}

        # Combine EMA values and slopes into a single dictionary
        indicators = {**ema_values, **ema_slopes}

        # Create hexagram as a dictionary
        price = data["close"][-1]  # Get the latest price
        hexagram = np.array(
            [
                price > ema_values["ma1"],
                price > ema_values["ma2"],
                price > ema_values["ma3"],
                ema_values["ma1"] > ema_values["ma2"],
                ema_values["ma1"] > ema_values["ma3"],
                ema_values["ma2"] > ema_values["ma3"],
                0 > ema_slopes["ma1_slope"],
                0 > ema_slopes["ma2_slope"],
                0 > ema_slopes["ma3_slope"],
                ema_slopes["ma1_slope"] > ema_slopes["ma2_slope"],
                ema_slopes["ma1_slope"] > ema_slopes["ma3_slope"],
                ema_slopes["ma2_slope"] > ema_slopes["ma3_slope"],
            ]
        )

        indicators["hexagram"] = hexagram.T
        return indicators

    def plot(self, *args):
        qx.plot(
            *args,
            tuple(
                [
                    (f"ma{idx}", f"MA {idx} Value", color, 0, "Value")
                    for idx, color in enumerate(["white", "cyan", "green"], start=1)
                ]
                + [
                    (f"ma{idx}_slope", f"MA {idx} Slope", color, 1, "Slope")
                    for idx, color in enumerate(["red", "blue", "yellow"], start=1)
                ],
            ),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()

        # Convert the hexagram to a binary number (decimal)
        hexagram = indicators["hexagram"]  # Get the hexagram dictionary
        # print(hexagram)
        binary_string = "".join(
            str(int(hexagram[i])) for i in range(12)
        )  # Convert to binary string

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
        end="2023-01-01",
    )

    bot = Forty96()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
