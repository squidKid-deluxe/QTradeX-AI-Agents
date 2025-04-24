"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

fosc_uo_msw.py

Ultimate Forecast Mesa

Indicators:

- Utilizes a blend of technical indicators, including:
  - Ultimate Oscillator (UO) for momentum analysis
  - Forecast Oscillator (FO) for trend direction
  - Mesa Sine Wave (MSW) for cycle identification
  - Derivatives of these indicators to assess momentum changes

Strategy:

- The strategy is based on the confluence of these indicators to generate buy and sell signals:
  - **Buy Signal**: Triggered when the Ultimate Oscillator is below a specified threshold (indicating oversold conditions), 
  the Forecast Oscillator is positive, the Mesa Sine Wave is above a defined level, 
  and their respective derivatives indicate upward momentum.
  
  - **Sell Signal**: Triggered when the Ultimate Oscillator is above a specified threshold (indicating overbought conditions), 
  the Forecast Oscillator is negative, the Mesa Sine Wave is below a defined level, 
  and their respective derivatives indicate downward momentum.
"""


import math
import time

import numpy as np
import qtradex as qx


class UltimateForecastMesa(qx.BaseBot):
    def __init__(self):
        # Default tuning values (periods for UO, FO, MSW, and thresholds for buy/sell signals)
        self.drop = {
            # Periods for indicators
            "uo_short_period": 7.0,  # Short period for Ultimate Oscillator
            "uo_medium_period": 14.0,  # Medium period for Ultimate Oscillator
            "uo_long_period": 28.0,  # Long period for Ultimate Oscillator
            "fosc_period": 14.0,  # Period for Forecast Oscillator
            "msw_period": 10.0,  # Period for Mesa Sine Wave
            # Required Count of Signals
            "buy_threshold": 3,  # Number of conditions to be true for a buy signal
            "sell_threshold": 3,  # Number of conditions to be true for a sell signal
            # Thresholds for indicators
            "uo_buy_threshold": 30.0,  # UO Buy threshold (oversold)
            "uo_sell_threshold": 70.0,  # UO Sell threshold (overbought)
            "fosc_buy_threshold": 0.0,  # FO Buy threshold (positive)
            "fosc_sell_threshold": 0.0,  # FO Sell threshold (negative)
            "msw_buy_threshold": 0.0,  # MSW Buy threshold (above 0 for bullish cycle)
            "msw_sell_threshold": 0.0,  # MSW Sell threshold (below 0 for bearish cycle)
            # Derivative thresholds for signals
            "uo_buy_d_threshold": 0.0,  # UO Buy derivative threshold (positive for uptrend)
            "fosc_buy_d_threshold": 0.0,  # FO Buy derivative threshold (positive for uptrend)
            "msw_buy_sine_d_threshold": 0.0,  # MSW Buy sine derivative threshold (positive for bullish cycle)
            "uo_sell_d_threshold": 0.0,  # UO Sell derivative threshold (negative for downtrend)
            "fosc_sell_d_threshold": 0.0,  # FO Sell derivative threshold (negative for downtrend)
            "msw_sine_sell_d_threshold": 0.0,  # MSW Sine Sell derivative threshold (negative for bearish cycle)
        }
        self.tune = {
            "uo_short_period": 10.34,
            "uo_medium_period": 13.39,
            "uo_long_period": 20.91,
            "fosc_period": 13.9,
            "msw_period": 16.23,
            "buy_threshold": 1,
            "sell_threshold": 1,
            "uo_buy_threshold": 17.93,
            "uo_sell_threshold": 54.39,
            "fosc_buy_threshold": -0.0018,
            "fosc_sell_threshold": 0.001582,
            "msw_buy_threshold": -0.00159,
            "msw_sell_threshold": 0.002015,
            "uo_buy_d_threshold": -0.002132,
            "fosc_buy_d_threshold": 0.00275,
            "msw_buy_sine_d_threshold": 0.00253,
            "uo_sell_d_threshold": 0.001878,
            "fosc_sell_d_threshold": -0.0003842,
            "msw_sine_sell_d_threshold": 0.0009187,
        }

        # Optimizer clamps (min, max, strength)
        self.clamps = {
            "uo_short_period": [5, 7.0, 50, 0.5],
            "uo_medium_period": [5, 14.0, 50, 0.5],
            "uo_long_period": [5, 28.0, 50, 0.5],
            "fosc_period": [5, 14.0, 50, 0.5],
            "msw_period": [5, 10.0, 50, 0.5],
            "buy_threshold": [1, 3, 5, 1],
            "sell_threshold": [1, 3, 5, 1],
            "uo_buy_threshold": [0, 30.0, 100, 0.5],
            "uo_sell_threshold": [0, 70.0, 100, 0.5],
            "fosc_buy_threshold": [-100, 0.0, 0, 0.5],
            "fosc_sell_threshold": [0, 0.0, 100, 0.5],
            "msw_buy_threshold": [-100, 0.0, 0, 0.5],
            "msw_sell_threshold": [0, 0.0, 100, 0.5],
            "uo_buy_d_threshold": [-1, 0.0, 1, 0.5],
            "fosc_buy_d_threshold": [-1, 0.0, 1, 0.5],
            "msw_buy_sine_d_threshold": [-1, 0.0, 1, 0.5],
            "uo_sell_d_threshold": [-1, 0.0, 1, 0.5],
            "fosc_sell_d_threshold": [-1, 0.0, 1, 0.5],
            "msw_sine_sell_d_threshold": [-1, 0.0, 1, 0.5],
        }

    def indicators(self, data):
        """
        Calculate the indicators used in the strategy.
        """
        # Ultimate Oscillator (UO)
        uo = qx.ti.ultosc(
            data["high"],
            data["low"],
            data["close"],
            self.tune["uo_short_period"],
            self.tune["uo_medium_period"],
            self.tune["uo_long_period"],
        )

        # Derivative of Ultimate Oscillator (UO)
        uo_derivative = qx.derivative(uo)

        # Forecast Oscillator (FO)
        fosc = qx.ti.fosc(data["close"], self.tune["fosc_period"])

        # Derivative of Forecast Oscillator (FO)
        fosc_derivative = qx.derivative(fosc)

        # Mesa Sine Wave (MSW)
        msw_sine, msw_lead = qx.ti.msw(data["close"], self.tune["msw_period"])

        # Derivative of Mesa Sine Wave (MSW)
        msw_sine_derivative = qx.derivative(msw_sine)

        return {
            "uo": uo,
            "fosc": fosc,
            "msw_sine": msw_sine,
            "uo_derivative": uo_derivative,
            "fosc_derivative": fosc_derivative,
            "msw_sine_derivative": msw_sine_derivative,
        }

    def plot(self, *args):
        """
        Plot indicators for visual analysis.
        """
        qx.plot(
            self.info,
            *args,
            (
                ("uo", "Ultimate Oscillator", "yellow", 3, "Confluence"),
                ("fosc", "Forecast Oscillator", "green", 2, "Confluence"),
                ("msw_sine", "MSW Sine", "blue", 2, "Confluence"),
                ("uo_derivative", "UO Derivative", "red", 1, "Derivative"),
                ("fosc_derivative", "FO Derivative", "orange", 1, "Derivative"),
                (
                    "msw_sine_derivative",
                    "MSW Sine Derivative",
                    "purple",
                    1,
                    "Derivative",
                ),
            ),
        )

    def strategy(self, state, indicators):
        """
        Define strategy based on Ultimate Oscillator, Forecast Oscillator, and Mesa Sine Wave with their derivatives.
        """
        if state["last_trade"] is None:
            # Enter market with all capital on the first trade
            return qx.Buy()

        # Buy Signal Criteria
        if (
            sum(
                [
                    int(indicators["uo"] < self.tune["uo_buy_threshold"]),
                    int(indicators["fosc"] > self.tune["fosc_buy_threshold"]),
                    int(indicators["msw_sine"] > self.tune["msw_buy_threshold"]),
                    int(indicators["uo_derivative"] > self.tune["uo_buy_d_threshold"]),
                    int(
                        indicators["fosc_derivative"]
                        > self.tune["fosc_buy_d_threshold"]
                    ),
                    int(
                        indicators["msw_sine_derivative"]
                        > self.tune["msw_buy_sine_d_threshold"]
                    ),
                ]
            )
            > self.tune["buy_threshold"]
        ):
            if isinstance(state["last_trade"], qx.Sell):
                # Exit short position and enter long with all capital
                return qx.Buy()

        # Sell Signal Criteria
        if (
            sum(
                [
                    int(indicators["uo"] > self.tune["uo_sell_threshold"]),
                    int(indicators["fosc"] < self.tune["fosc_sell_threshold"]),
                    int(indicators["msw_sine"] < self.tune["msw_sell_threshold"]),
                    int(indicators["uo_derivative"] < self.tune["uo_sell_d_threshold"]),
                    int(
                        indicators["fosc_derivative"]
                        < self.tune["fosc_sell_d_threshold"]
                    ),
                    int(
                        indicators["msw_sine_derivative"]
                        < self.tune["msw_sine_sell_d_threshold"]
                    ),
                ]
            )
            > self.tune["sell_threshold"]
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
    asset, currency = "XLM", "XRP"
    wallet = qx.PaperWallet({asset: 0, currency: 1})
    data = qx.Data(
        exchange="kucoin",
        asset=asset,
        currency=currency,
        intermediary="BTC",
        begin="2021-01-01",
        end="2023-01-01",
    )

    bot = UltimateForecastMesa()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
