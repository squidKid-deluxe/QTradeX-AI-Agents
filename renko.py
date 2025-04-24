"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

renko.py

Renko

Indicators:

This script defines a Renko trading bot for use on the qTradex platform. 
The strategy is based on Renko bar crossovers and the Relative Strength Index (RSI) to generate buy and sell signals. 

### Strategy Overview:
- **Renko Bars**:
  - The bot uses Renko bars, which are price-based charts where each new bar represents a fixed price movement, 
  eliminating minor price fluctuations and providing a clearer view of the overall trend.
  - The bot calculates the Renko bar size using either an Average True Range (ATR) method or a traditional multiplier.

- **RSI Confirmation**:
  - The strategy incorporates the Relative Strength Index (RSI) to confirm trends:
    
    - A **long (buy)** signal is generated when the Renko close is above the Renko open, 
    indicating an uptrend, and the RSI is below the oversold level.

    - A **short (sell)** signal is generated when the Renko close is below the Renko open, 
    indicating a downtrend, and the RSI is above the overbought level.

- **Warning Zones**:
  - The bot computes warning zones around the Renko close price as a percentage of Renko movement. 
  These zones are used to determine when to exit positions:
    - Long positions are exited if the current price drops below the warning zone low.
    - Short positions are exited if the current price rises above the warning zone high.


### Parameters:
- **ATR Period** (`atr_period`): Period for calculating the Average True Range, used if the ATR method is selected 
for Renko calculation.
- **Use ATR for Renko Calculation** (`is_atr`): Boolean flag to determine whether to use ATR for Renko size calculation 
or use the traditional multiplier method.
- **Traditional Renko Multiplier** (`trad_len`): Multiplier for traditional Renko calculation when `is_atr` is set to 0.
- **Warning Zone Percentage** (`warning_zone`): Percentage of Renko movement to define the warning zones for exits.
- **RSI Period** (`rsi_period`): Period used for calculating the Relative Strength Index.
- **RSI Oversold Threshold** (`rsi_oversold`): RSI level below which the market is considered oversold 
(used for long signal confirmation).
- **RSI Overbought Threshold** (`rsi_overbought`): RSI level above which the market is considered overbought 
(used for short signal confirmation).
"""


import math

import numpy as np
import qtradex as qx


class Renko(qx.BaseBot):
    def __init__(self):
        # Strategy Parameters
        self.tune = {
            "atr_period": 14.0,  # ATR period
            "is_atr": 0,  # Bool: Use ATR for Renko calculation
            "trad_len": 1.15,  # Traditional Renko multiplier
            "warning_zone": 50.0,  # Warning zone as a percentage of Renko
            "rsi_period": 14.0,  # RSI period
            "rsi_oversold": 30.0,  # RSI oversold threshold
            "rsi_overbought": 70.0,  # RSI overbought threshold
        }

        self.clamps = {
            "atr_period": [5, 14.0, 50, 0.5],
            "is_atr": [0, 0, 1, 1],
            "trad_len": [0.1, 1.15, 2.5, 0.5],
            "warning_zone": [10, 50.0, 90, 0.5],
            "rsi_period": [5, 14.0, 30, 1],
            "rsi_oversold": [0, 30.0, 100, 1],
            "rsi_overbought": [0, 70.0, 100, 1],
        }

    def calculate_renko(self, data, is_atr, atr_period, trad_len):
        """Calculate Renko bars based on ATR or Traditional method."""
        if is_atr:
            # ATR-based Renko calculation
            atr = qx.ti.atr(data["high"], data["low"], data["close"], atr_period)
            renko_size = atr[-1] if len(atr) > 0 else 1
        else:
            # Traditional Renko calculation using the multiplier
            renko_size = trad_len

        renko_open = np.roll(data["close"], 1)  # Previous close as open
        renko_close = data["close"]
        renko_diff = abs(renko_close - renko_open)

        return renko_open, renko_close, renko_diff, renko_size

    def compute_rsi(self, data, rsi_period):
        """Calculate RSI (Relative Strength Index)"""
        return qx.ti.rsi(data["close"], rsi_period)

    def indicators(self, data):
        """Compute Renko bars and RSI, as well as warning zones."""
        # Get Renko bars based on chosen parameters
        renko_open, renko_close, renko_diff, renko_size = self.calculate_renko(
            data, self.tune["is_atr"], self.tune["atr_period"], self.tune["trad_len"]
        )

        # Calculate RSI
        rsi = self.compute_rsi(data, self.tune["rsi_period"])

        # Warning zones for Renko
        warning_zone_high = renko_close + renko_diff * (self.tune["warning_zone"] / 100)
        warning_zone_low = renko_close - renko_diff * (self.tune["warning_zone"] / 100)

        return {
            "renko_open": renko_open,
            "renko_close": renko_close,
            "renko_diff": renko_diff,
            "warning_zone_high": warning_zone_high,
            "warning_zone_low": warning_zone_low,
            "rsi": rsi,
        }

    def strategy(self, tick_info, indicators):
        """Define the trading strategy using Renko crossover signals.

        The strategy generates all-in, all-out buy/sell signals based purely on the Renko bar crossover
        and RSI momentum. The logic is as follows:

        - **Long (Buy) Entry**: Triggered when Renko close is greater than Renko open (uptrend) and RSI is below the oversold level.
        - **Short (Sell) Entry**: Triggered when Renko close is less than Renko open (downtrend) and RSI is above the overbought level.
        - **Exit Conditions**:
          - Long positions are closed if the current price drops below the warning zone low.
          - Short positions are closed if the current price rises above the warning zone high.

        Args:
            tick_info (dict): Contains the current price data, including 'close' price.
            indicators (dict): Contains the computed indicators, such as 'renko_open', 'renko_close', 'rsi', etc.

        Returns:
            qx.Buy or qx.Sell: The corresponding trading signal (buy or sell) based on the conditions.
        """

        renko_open = indicators["renko_open"]
        renko_close = indicators["renko_close"]
        renko_diff = indicators["renko_diff"]
        warning_zone_high = indicators["warning_zone_high"]
        warning_zone_low = indicators["warning_zone_low"]
        rsi = indicators["rsi"]

        # Long entry condition (Renko close crosses above Renko open + RSI confirmation)
        long_condition = renko_close > renko_open and rsi < self.tune["rsi_oversold"]

        # Short entry condition (Renko close crosses below Renko open + RSI confirmation)
        short_condition = renko_close < renko_open and rsi > self.tune["rsi_overbought"]

        # Long exit condition (price drops below the warning zone low)
        long_exit_condition = tick_info["close"] < warning_zone_low

        # Short exit condition (price rises above the warning zone high)
        short_exit_condition = tick_info["close"] > warning_zone_high

        # All-in, all-out approach: Close the current position and enter a new one.
        if long_condition:
            return qx.Buy()  # Open Long position

        elif short_condition:
            return qx.Sell()  # Open Short position

        # Exit conditions: If current price hits the warning zone for the respective position, close the position.
        elif long_exit_condition:
            return qx.Sell()  # Close Long position

        elif short_exit_condition:
            return qx.Buy()  # Close Short position

        return None  # No action if no conditions are met

    def plot(self, *args):
        """Plot Renko bars, warning zones, and entry/exit arrows."""
        renko_open = args[0]["renko_open"]
        renko_close = args[0]["renko_close"]
        warning_zone_high = args[0]["warning_zone_high"]
        warning_zone_low = args[0]["warning_zone_low"]

        qx.plot(
            self.info,
            *args,
            (
                ("renko_close", "Renko Close", "green", 0, "Main"),
                ("renko_open", "Renko Open", "red", 0, "Main"),
                ("warning_zone_high", "Warning Zone High", "yellow", 1, "Main"),
                ("warning_zone_low", "Warning Zone Low", "yellow", 1, "Main"),
            ),
        )

        # Plot arrows for buy/sell signals
        long_arrow = 1 if renko_close[-1] > renko_open[-1] else None
        short_arrow = -1 if renko_close[-1] < renko_open[-1] else None
        qx.plot_arrow(long_arrow, colorup="aqua", transp=0)
        qx.plot_arrow(short_arrow, colordown="red", transp=0)

        # Plot warning zone arrows
        if tick_info["close"] < warning_zone_low:
            qx.plot_arrow(1, colordown="red", transp=60)
        elif tick_info["close"] > warning_zone_high:
            qx.plot_arrow(-1, colorup="aqua", transp=60)

    def fitness(self, states, raw_states, asset, currency):
        return [
            "roi_assets",
            "roi_currency",
            "roi",
            "cagr",
            "sortino",
            "maximum_drawdown",
            "trade_win_rate",
        ], {}


def main():
    asset, currency = "BTC", "USDT"
    wallet = qx.PaperWallet({asset: 1, currency: 0})
    data = qx.Data(
        exchange="kucoin",
        asset=asset,
        currency=currency,
        begin="2021-01-01",
        end="2023-01-01",
    )

    bot = Renko()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
