"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

harmonica.py

6 SAR 4 EMA Harmonica

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
        self.drop = {
            "SAR_initial": 0.02,
            "SAR_acceleration": 0.2,
            "scalar_1": 2.0,
            "scalar_2": 4.0,
            "scalar_3": 8.0,
            "scalar_4": 10.0,
            "scalar_5": 12.0,
            "scalar_6": 14.0,
            "scalar_7": 16.0,
            "ma1_period": 5.0,
            "ma2_period": 8.0,
            "ma3_period": 12.0,
            "ma4_period": 15.0,
            "signal_period": 5.0,
            "sar_thresh": 4.0,
            "signal_thresh": 5.0,
            "signal_thresh_old": 1.0,
            "signal_thresh_sell": 0.9,
            "rest_multiplier": 1.0,
            "min_rest": 1.0,
            "buy_rest": 1.0,
            "ago": 3,
        }

        self.tune = {
            "SAR_initial": 0.03025733047647713,
            "SAR_acceleration": 0.19039874671925122,
            "scalar_1": 2.7964677019042297,
            "scalar_2": 4.630479397953835,
            "scalar_3": 12.100260747395472,
            "scalar_4": 14.235088994316875,
            "scalar_5": 12.288907433576485,
            "scalar_6": 14.209363904790804,
            "scalar_7": 18.158550465916008,
            "ma1_period": 5.345417974023874,
            "ma2_period": 9.73247818092897,
            "ma3_period": 15.535815413295927,
            "ma4_period": 19.436484306474657,
            "signal_period": 3.5984353787739525,
            "sar_thresh": 2.444131549529109,
            "signal_thresh": 3.687078101749861,
            "signal_thresh_old": 1.9764105725674108,
            "signal_thresh_sell": 1.0409730161049788,
            "rest_multiplier": 1.4046953312186636,
            "min_rest": 1.9212598575580446,
            "buy_rest": 1.1354573628750735,
            "ago": 62,
        }

        self.tune = {
            "SAR_initial": 0.04573,
            "SAR_acceleration": 0.3197,
            "scalar_1": 10.34,
            "scalar_2": 8.739,
            "scalar_3": 138.1,
            "scalar_4": 3.867,
            "scalar_5": 1.721,
            "scalar_6": 2.081,
            "scalar_7": 20.61,
            "ma1_period": 17.54,
            "ma2_period": 47.93,
            "ma3_period": 34.97,
            "ma4_period": 7.784,
            "signal_period": 2.97,
            "sar_thresh": 2.55,
            "signal_thresh": 5.046,
            "signal_thresh_old": 5.8,
            "signal_thresh_sell": 2.009,
            "rest_multiplier": 0.4077,
            "min_rest": 2.789,
            "buy_rest": 2.772,
            "ago": 24,
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
            # moving averages
            [5, 90, 0.5],
            [5, 90, 0.5],
            [5, 90, 0.5],
            [5, 90, 0.5],
            [2, 10, 0.5],
            # magic numbers and thresholds
            [1, 6, 1],
            [0.1, 20, 1],
            [0.1, 20, 1],
            [0.1, 20, 1],
            [0.1, 20, 1],
            [1, 100, 1],
            [1, 100, 1],
            [0, 100, 1],
        ]

        # Initialize storage for trade details
        self.storage = {"hold": 0}

    def reset(self):
        self.storage = {"hold": 0}

    def autorange(self):
        return super().autorange() + self.tune["ago"]

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
        ma1 = qx.float_period(qx.tu.ema, (data["close"], self.tune["ma1_period"]), (1,))
        ma2 = qx.float_period(qx.tu.ema, (data["close"], self.tune["ma2_period"]), (1,))
        ma3 = qx.float_period(qx.tu.ema, (data["close"], self.tune["ma3_period"]), (1,))
        signal = qx.float_period(
            qx.tu.ema, (data["close"], self.tune["signal_period"]), (1,)
        )
        ma4 = qx.float_period(qx.tu.ema, (data["close"], self.tune["ma4_period"]), (1,))

        return {
            "sars": sars,
            "ma1": ma1,
            "ma2": ma2,
            "ma3": ma3,
            "ma4": ma4,
            "ma4_ago": qx.lag(ma4, self.tune["ago"]),
            "signal": signal,
        }

    def plot(self, *args):
        qx.plot(
            *args,
            (
                ("ma1", "MA 1", "white", 0, "SAR Harmonica"),
                ("ma2", "MA 2", "cyan", 0, "SAR Harmonica"),
                ("ma3", "MA 3", "teal", 0, "SAR Harmonica"),
                ("ma4", "MA 4", "blue", 0, "SAR Harmonica"),
                ("ma4_ago", "MA 4 old", "lightgreen", 0, "SAR Harmonica"),
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
        ma1 = indicators["ma1"]
        ma2 = indicators["ma2"]
        ma3 = indicators["ma3"]
        ma4 = indicators["ma4"]
        ma4_ago = indicators["ma4_ago"]

        market = sum(1 for sar in sars if sar < signal)

        # Manage storage (hold, trade price, etc.)
        key3 = (
            signal if state["last_trade"] is None else self.storage["trade_price"][-1]
        )
        self.storage["trade_price"] = self.storage.get("trade_price", [key3, key3])

        # Bearish conditions
        bear_conditions = [
            (market < self.tune["sar_thresh"]) or (ma1 < ma2) or (ma1 < ma3),
            (signal > self.tune["signal_thresh"] * self.storage["trade_price"][-1])
            and (ma1 < ma4),
            (signal > self.tune["signal_thresh_old"] * self.storage["trade_price"][-1])
            and (ma1 < ma4_ago),
        ]

        # If bearish conditions are met, trigger Sell
        if any(bear_conditions):
            if (
                state["last_trade"] is None or isinstance(state["last_trade"], qx.Buy)
            ) and state["unix"] > self.storage["hold"]:
                if signal > min(sars):
                    if (
                        signal
                        > self.tune["signal_thresh_sell"]
                        * self.storage["trade_price"][-1]
                    ):
                        rest = self.tune["rest_multiplier"] * (
                            max(sars) / self.storage["trade_price"][-1]
                        )
                        rest = max(rest, self.tune["min_rest"])
                        self.storage["hold"] = state["unix"] + 86400 * rest
                        self.storage["trade_price"].append(signal)
                        return qx.Sell()  # Execute Sell
                    else:
                        self.storage["trade_price"].append(signal)
                        return qx.Sell()  # Execute Sell

        # Bullish conditions: If MA10 > MA60, trigger Buy
        elif (ma1 > ma2) or (ma1 > ma3):
            if any(sar < signal for sar in sars):
                if state["last_trade"] is None or isinstance(
                    state["last_trade"], qx.Sell
                ):
                    rest = self.tune["buy_rest"]
                    if state["unix"] > self.storage["hold"]:
                        self.storage["hold"] = state["unix"] + 86400 * rest
                        self.storage["trade_price"].append(signal)
                        return qx.Buy()  # Execute Buy

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
