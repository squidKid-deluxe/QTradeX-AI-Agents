"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

confluence.py

Confluence

Indicators:

- Employs a combination of technical indicators, including:
  - Exponential Moving Averages (EMAs) for trend direction
  - Relative Strength Index (RSI) for momentum analysis
  - Moving Average Convergence Divergence (MACD) for trend strength
  - Bollinger Bands for volatility and price levels
  - Volume analysis to confirm price movements

Strategy:

- The strategy is based on the confluence of these indicators to generate trading signals:
  - **Buy Signal**: Triggered when the short-term EMA is above the long-term EMA, the RSI is below 70 (not overbought),
   the MACD histogram is positive (indicating bullish momentum), and the price is near or below the lower Bollinger Band.
   
  - **Sell Signal**: Triggered when the short-term EMA is below the long-term EMA, the RSI is above 30 (not oversold),
   the MACD histogram is negative (indicating bearish momentum), and the price is near or above the upper Bollinger Band.

"""


import math
import time

import numpy as np
import qtradex as qx


class Confluence(qx.BaseBot):
    def __init__(self):
        # Default tuning values (periods for EMAs, RSI, MACD, Bollinger Bands)
        self.tune = {
            "ma1_period": 5.0,  # Short-term EMA
            "ma2_period": 20.0,  # Long-term EMA
            "rsi_period": 14.0,  # RSI period
            "macd_fast_period": 12.0,  # MACD fast period
            "macd_slow_period": 26.0,  # MACD slow period
            "macd_signal_period": 9.0,  # MACD signal period
            "bollinger_period": 20.0,  # Bollinger Bands period
            "bollinger_stddev": 2.0,  # Bollinger Bands standard deviation
        }
        # Optimizer clamps (min, max, strength)
        self.clamps = [
            [5, 100, 0.5],  # For ma1
            [10, 150, 0.6],  # For ma2
            [5, 30, 0.5],  # For RSI
            [5, 50, 0.6],  # For MACD periods
            [5, 50, 0.6],  # For MACD periods
            [5, 50, 0.6],  # For MACD periods
            [10, 50, 0.5],  # For Bollinger Bands period
            [1, 3, 0.5],  # For Bollinger Bands standard deviation
        ]

    def indicators(self, data):
        """
        Calculate the indicators used in the strategy.
        """
        # EMA Crossovers
        ma1 = qx.float_period(qx.tu.ema, (data["close"], self.tune["ma1_period"]), (1,))
        ma2 = qx.float_period(qx.tu.ema, (data["close"], self.tune["ma2_period"]), (1,))

        # RSI
        rsi = qx.float_period(qx.tu.rsi, (data["close"], self.tune["rsi_period"]), (1,))

        # MACD
        macd_line, macd_signal, macd_histogram = qx.float_period(
            qx.tu.macd,
            (
                data["close"],
                self.tune["macd_fast_period"],
                self.tune["macd_slow_period"],
                self.tune["macd_signal_period"],
            ),
            (1, 1, 1),
        )

        # Bollinger Bands
        bollinger_upper, bollinger_middle, bollinger_lower = qx.float_period(
            qx.tu.bbands,
            (
                data["close"],
                self.tune["bollinger_period"],
                self.tune["bollinger_stddev"],
            ),
            (1, 1, 1),
        )

        # Volume (default to simple volume)
        volume = qx.float_period(
            qx.tu.sma, (data["volume"], self.tune["bollinger_period"]), (1,)
        )

        return {
            "ma1": ma1,
            "ma2": ma2,
            "rsi": rsi,
            "macd_histogram": macd_histogram,
            "bollinger_upper": bollinger_upper,
            "bollinger_lower": bollinger_lower,
            "volume": volume,
        }

    def plot(self, *args):
        """
        Plot indicators for visual analysis.
        """
        qx.plot(
            *args,
            (
                ("ma1", "EMA 1", "white", 0, "Confluence"),
                ("ma2", "EMA 2", "cyan", 0, "Confluence"),
                ("bollinger_upper", "Bollinger Upper", "blue", 0, "Confluence"),
                ("bollinger_lower", "Bollinger Lower", "blue", 0, "Confluence"),
                ("rsi", "RSI", "green", 1, "RSI"),
                ("macd_histogram", "MACD Histogram", "orange", 2, "MACD"),
            ),
        )

    def strategy(self, state, indicators):
        """
        Define strategy based on EMA crossovers, RSI, MACD, Bollinger Bands, and Volume.
        """
        if state["last_trade"] is None:
            # Enter market with all capital on the first trade
            return qx.Buy()

        # Relaxed Buy Signal Criteria (Buy near the lower Bollinger Band and check for bullish momentum)
        if (
            indicators["ma1"] > indicators["ma2"]  # Short EMA above Long EMA
            and indicators["rsi"] < 70  # RSI is not in overbought region
            and indicators["macd_histogram"] > 0  # Positive MACD histogram (momentum)
            and state["close"]
            < indicators[
                "bollinger_lower"
            ]  # Price near or below Bollinger Band lower bound
        ):
            if isinstance(state["last_trade"], qx.Sell):
                # Exit short position and enter long with all capital
                return qx.Buy()

        # Relaxed Sell Signal Criteria (Sell near the upper Bollinger Band and check for bearish momentum)
        if (
            indicators["ma1"] < indicators["ma2"]  # Short EMA below Long EMA
            and indicators["rsi"] > 30  # RSI is not in oversold region
            and indicators["macd_histogram"] < 0  # Negative MACD histogram (momentum)
            and state["close"]
            > indicators[
                "bollinger_upper"
            ]  # Price near or above Bollinger Band upper bound
        ):
            if isinstance(state["last_trade"], qx.Buy):
                # Exit long position and enter short with all capital
                return qx.Sell()

        return None

    def fitness(self, states, raw_states, asset, currency):
        """
        Measure fitness of the bot based on ROI, Sortino ratio, and win rate.
        """
        return ["roi_gross", "sortino_ratio", "trade_win_rate"], {}


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

    bot = Confluence()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
