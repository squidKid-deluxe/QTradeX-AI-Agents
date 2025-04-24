"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

masterbot.py

Masterbot - A Powerful MACD*RSI*STOCH*ATR Trading Strategy

Indicators:

- **MACD (Moving Average Convergence Divergence)**:
  - The MACD is used to identify trend direction and momentum by comparing the difference 
  between two exponential moving averages (EMAs). 
  The bot uses the MACD line and the signal line to generate buy and sell signals.

- **RSI (Relative Strength Index)**:
  - The RSI is a momentum oscillator that measures the speed and change of price movements. 
  It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions. 
  The bot uses the RSI to confirm entry signals.

- **Stochastic Oscillator**:
  - The Stochastic Oscillator compares a particular closing price of an asset
   to a range of its prices over a certain period. 
   The bot uses both %K and %D lines to determine potential reversal points in the market.

- **ATR (Average True Range)**:
  - The ATR is a measure of market volatility. 
  The bot uses the ATR to set dynamic stop loss and take profit levels, 
  allowing for better risk management based on current market conditions.

Strategy:

**Entry Conditions**:
   - A **Buy** signal is generated when:
     - The MACD line crosses above the signal line.
     - The Stochastic %K is above 50.
     - The RSI is above 50.
   - A **Sell** signal is generated when:
     - The MACD line crosses below the signal line.
     - The Stochastic %K is below 50.
     - The RSI is below 50.

**Exit Conditions**:
   - The bot defines exit conditions based on the following:
     - For long positions, exit if:
       - The MACD line crosses below the signal line.
       - The current price falls below the average position price minus the ATR-based stop loss.
       - The current price rises above the average position price plus the ATR-based take profit.
     - For short positions, exit if:
       - The MACD line crosses above the signal line.
       - The current price rises above the average position price plus the ATR-based stop loss.
       - The current price falls below the average position price minus the ATR-based take profit.

https://www.tradingview.com/script/pOT16FZ5-Powerfull-strategy-MACD-RSI-STOCH-ATR-stop-best-on-Crude-Oil/
"""


import math
import time

import qtradex as qx


class MasterBot(qx.BaseBot):
    def __init__(self):
        # Strategy Parameters
        self.tune = {
            "macd_fast_period": 12.0,  # MACD Fast length
            "macd_slow_period": 26.0,  # MACD Slow length
            "macd_signal_period": 9.0,  # MACD Signal line length
            "k_period": 14.1,
            "k_slowing": 9.0,
            "d_period": 9.0,
            "rsi_period": 14.0,  # RSI Length
            "atr_period": 14.0,  # ATR Length for stop loss and take profit calculation
            "tp_multiplier": 6.0,  # Take profit multiplier (ATR)
            "sl_multiplier": 2.0,  # Stop loss multiplier (ATR)
        }

        self.clamps = {
            "macd_fast_period": [5, 12.0, 100, 0.5],
            "macd_slow_period": [5, 26.0, 100, 0.5],
            "macd_signal_period": [5, 9.0, 100, 0.5],
            "k_period": [5, 14.1, 100, 0.5],
            "k_slowing": [5, 9.0, 100, 0.5],
            "d_period": [5, 9.0, 100, 0.5],
            "rsi_period": [5, 14.0, 100, 0.5],
            "atr_period": [2, 14.0, 100, 0.5],
            "tp_multiplier": [2, 6.0, 100, 0.5],
            "sl_multiplier": [2, 2.0, 100, 0.5],
        }

    def indicators(self, data):
        """
        Calculate indicators using QX's indicator library (EMA, RSI, Stochastic, ATR).
        """
        macd_line, macd_signal, _ = qx.ti.macd(
            data["close"],
            self.tune["macd_fast_period"],
            self.tune["macd_slow_period"],
            self.tune["macd_signal_period"],
        )
        stoch_k, stoch_d = qx.ti.stoch(
            data["close"],
            data["high"],
            data["low"],
            self.tune["k_period"],
            self.tune["k_slowing"],
            self.tune["d_period"],
        )
        rsi = qx.ti.rsi(data["close"], self.tune["rsi_period"])
        atr = qx.ti.atr(
            data["high"], data["low"], data["close"], self.tune["atr_period"]
        )

        return {
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "rsi": rsi,
            "stoch_k": stoch_k,
            "stoch_d": stoch_d,
            "atr": atr,
        }

    def plot(self, *args):
        """
        Plot the indicators and strategy signals.
        """
        qx.plot(
            self.info,
            *args,
            (
                ("macd_line", "MACD Line", "blue", 3, "Main"),
                ("macd_signal", "MACD Signal", "red", 3, "Main"),
                ("stoch_k", "Stochastic %K", "green", 1, "Subplot"),
                ("stoch_d", "Stochastic %D", "purple", 1, "Subplot"),
                ("rsi", "RSI", "cyan", 2, "Subplot"),
                ("atr", "ATR", "orange", 3, "Subplot"),
            ),
        )

    def strategy(self, state, indicators):
        """
        Define the entry and exit strategy based on MACD, RSI, Stochastic, and ATR.
        """
        if state["last_trade"] is None:
            return qx.Buy()

        macd_line = indicators["macd_line"]
        macd_signal = indicators["macd_signal"]
        rsi = indicators["rsi"]
        stoch_k = indicators["stoch_k"]
        stoch_d = indicators["stoch_d"]
        atr = indicators["atr"]

        # Define entry conditions for long and short positions
        long_condition = (macd_line > macd_signal) and (stoch_k > 50) and (rsi > 50)
        short_condition = (macd_line < macd_signal) and (stoch_k < 50) and (rsi < 50)

        # Define ATR-based stop loss and take profit
        atr_stop_loss = (atr * self.tune["sl_multiplier"]) / state["close"]
        atr_take_profit = (atr * self.tune["tp_multiplier"]) / state["close"]

        # Exit conditions
        long_exit_condition = (
            (macd_line < macd_signal)
            or (state["close"] < state["last_trade"].price - atr_stop_loss)
            or (state["close"] > state["last_trade"].price + atr_take_profit)
        )
        short_exit_condition = (
            (macd_line > macd_signal)
            or (state["close"] > state["last_trade"].price + atr_stop_loss)
            or (state["close"] < state["last_trade"].price - atr_take_profit)
        )

        # Entry signals
        if long_condition and isinstance(state["last_trade"], qx.Sell):
            return qx.Buy()
        elif short_condition and isinstance(state["last_trade"], qx.Buy):
            return qx.Sell()

        # Exit signals
        if long_exit_condition and isinstance(state["last_trade"], qx.Buy):
            return qx.Sell()
        elif short_exit_condition and isinstance(state["last_trade"], qx.Sell):
            return qx.Buy()

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

    bot = MasterBot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
