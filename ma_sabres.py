"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

ma_sabres.py

MASabres Bot

Key Features:
- Multiple moving average types and periods: The bot allows for switching between different moving average types
  (e.g., EMA, SMA, HMA) for each of the five available moving averages, making the strategy adaptable to various market conditions.
- Automated tuning: The bot supports tuning of several key parameters, including moving average periods, types, and 
  thresholds for bullish and bearish signals. This allows for dynamic optimization based on market behavior.
- Slope-based trend detection: The strategy utilizes the slope of each moving average (calculated using derivatives)
  to determine the trend direction and strength. The slopes are compared with preset thresholds to classify the market
  as bullish or bearish.
- Dynamic Buy/Sell signals: The bot generates Buy and Sell signals based on the combined slope indicators for the
  moving averages. It executes a trade when a sufficient number of indicators align with bullish or bearish conditions.
  
Indicators:
- Moving averages: The strategy uses five different moving averages, which are selected and configured using the 
  tune dictionary. Each moving average can be assigned a different period and type.
- Slope calculation: The slope of each moving average is calculated using the derivative of the moving average over time.
  This slope is then normalized and used to assess the trend's direction and strength.
  
Strategy:
- Buy signal: Generated when a sufficient number of moving averages show a bullish slope (greater than the configured threshold).
- Sell signal: Generated when a sufficient number of moving averages show a bearish slope (less than the configured threshold).
- A strategy wait period is enforced to avoid multiple trades within the same market condition.
"""
import math
import time

import numpy as np
import qtradex as qx


class MASabres(qx.BaseBot):
    def __init__(self):
        # Initial tune values
        self.tune = {
            "ma1_period": 5.0,
            "ma2_period": 10.0,
            "ma3_period": 15.0,
            "ma4_period": 20.0,
            "ma5_period": 25.0,
            "ma1_type": 11,
            "ma2_type": 11,
            "ma3_type": 11,
            "ma4_type": 11,
            "ma5_type": 11,
            "bear1": 0.1,
            "bear2": 0.1,
            "bear3": 0.1,
            "bear4": 0.1,
            "bear5": 0.1,
            "bull1": 0.1,
            "bull2": 0.1,
            "bull3": 0.1,
            "bull4": 0.1,
            "bull5": 0.1,
            "bullish": 4.0,
            "bearish": 4.0,
            "thresh": 2.0,
        }

        # Clamps for tuning values
        self.clamps = {
            "ma1_period": [5, 5.0, 200, 0.5],
            "ma2_period": [5, 10.0, 200, 0.5],
            "ma3_period": [5, 15.0, 200, 0.5],
            "ma4_period": [5, 20.0, 200, 0.5],
            "ma5_period": [5, 25.0, 200, 0.5],
            "ma1_type": [0, 11, 11, 1],
            "ma2_type": [0, 11, 11, 1],
            "ma3_type": [0, 11, 11, 1],
            "ma4_type": [0, 11, 11, 1],
            "ma5_type": [0, 11, 11, 1],
            "bear1": [-1, 0.1, 1, 0.5],
            "bear2": [-1, 0.1, 1, 0.5],
            "bear3": [-1, 0.1, 1, 0.5],
            "bear4": [-1, 0.1, 1, 0.5],
            "bear5": [-1, 0.1, 1, 0.5],
            "bull1": [-1, 0.1, 1, 0.5],
            "bull2": [-1, 0.1, 1, 0.5],
            "bull3": [-1, 0.1, 1, 0.5],
            "bull4": [-1, 0.1, 1, 0.5],
            "bull5": [-1, 0.1, 1, 0.5],
            "bullish": [1, 4.0, 5, 1],
            "bearish": [1, 4.0, 5, 1],
            "thresh": [0, 2.0, 5, 1],
        }

    def indicators(self, data):
        """
        Compute and return indicators used for strategy
        """
        ret = {}
        for i in range(5):
            i += 1
            func = [
                qx.ti.dema,
                qx.ti.ema,
                qx.ti.hma,
                qx.ti.kama,
                qx.ti.linreg,
                qx.ti.sma,
                qx.ti.tema,
                qx.ti.trima,
                qx.ti.tsf,
                qx.ti.vwma,
                qx.ti.wma,
                qx.ti.zlema,
            ][self.tune[f"ma{i}_type"]]
            if self.tune[f"ma{i}_type"] == 9:
                ret[f"ma{i}_slope"] = qx.derivative(
                    func(data["close"], data["volume"], self.tune[f"ma{i}_period"])
                )
                ret[f"ma{i}_slope"], data_close = qx.truncate(
                    ret[f"ma{i}_slope"], data["close"]
                )
                ret[f"ma{i}_slope"] = ret[f"ma{i}_slope"] / data_close * 10
            else:
                ret[f"ma{i}_slope"] = qx.derivative(
                    func(data["close"], self.tune[f"ma{i}_period"])
                )
                ret[f"ma{i}_slope"], data_close = qx.truncate(
                    ret[f"ma{i}_slope"], data["close"]
                )
                ret[f"ma{i}_slope"] = ret[f"ma{i}_slope"] / data_close * 10
        return ret

    def plot(self, *args):
        """
        Plot the strategy with moving averages
        """
        qx.plot(
            self.info,
            *args,
            tuple(
                (f"ma{i}_slope", "Moving Average", (i / 6, i / 6, 1, 1), 1, "Slopes")
                for i in range(1, 6)
            ),
        )

    def strategy(self, state, indicators):
        """
        Strategy logic for buy/sell signals based on MA crossover and ATR
        """
        ma1s = indicators["ma1_slope"]
        ma2s = indicators["ma2_slope"]
        ma3s = indicators["ma3_slope"]
        ma4s = indicators["ma4_slope"]
        ma5s = indicators["ma5_slope"]

        # Ensure the bot waits for a previous trade before making a decision
        if state["last_trade"] is None:
            return qx.Buy()

        bullish = 0

        if ma1s > self.tune["bull1"]:
            bullish += 1
        if ma2s > self.tune["bull2"]:
            bullish += 1
        if ma3s > self.tune["bull3"]:
            bullish += 1
        if ma4s > self.tune["bull4"]:
            bullish += 1
        if ma5s > self.tune["bull5"]:
            bullish += 1

        bearish = 0
        if ma1s < -self.tune["bear1"]:
            bearish += 1
        if ma2s < -self.tune["bear2"]:
            bearish += 1
        if ma3s < -self.tune["bear3"]:
            bearish += 1
        if ma4s < -self.tune["bear4"]:
            bearish += 1
        if ma5s < -self.tune["bear5"]:
            bearish += 1

        if abs(bullish - bearish) < self.tune["thresh"]:
            return None

        if bullish >= self.tune["bullish"] and isinstance(state["last_trade"], qx.Sell):
            return qx.Buy()

        if bearish >= self.tune["bearish"] and isinstance(state["last_trade"], qx.Buy):
            return qx.Sell()

        return None

    def fitness(self, states, raw_states, asset, currency):
        return [
            "roi",
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

    bot = MASabres()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
