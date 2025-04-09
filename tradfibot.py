"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

tradfibot.py

TradFi Inspired Confluence of Indications

Indicators:

- Utilizes a diverse set of technical indicators, including:
  - Simple Moving Averages (SMA) for trend direction
  - Exponential Moving Averages (EMA) for trend confirmation
  - Relative Strength Index (RSI) for momentum analysis
  - Moving Average Convergence Divergence (MACD) for identifying bullish and bearish momentum
  - Bollinger Bands for assessing volatility and breakout opportunities
  - Stochastic Oscillator for identifying overbought and oversold conditions
  - Average Directional Index (ADX) for confirming trend strength

Strategy:

- The strategy is based on a combination of these indicators to generate buy and sell signals:
  - **Buy Signal**: Triggered when the short-term SMA is above the long-term SMA, the short-term EMA 
  is above the long-term EMA, the RSI indicates oversold conditions (below 30),
   the MACD is above its signal line, the price breaks above the upper Bollinger Band, 
   the Stochastic K line crosses above the D line, and the ADX confirms a strong trend (above 25).
   
  - **Sell Signal**: Triggered when the short-term SMA is below the long-term SMA,
   the short-term EMA is below the long-term EMA, the RSI indicates overbought conditions (above 70),
    the MACD is below its signal line, the price breaks below the lower Bollinger Band, 
    the Stochastic K line crosses below the D line, and the ADX confirms a strong trend (above 25).
"""


import numpy as np
import qtradex as qx


class TradFiInspired(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "sma_short_period": 50.0,  # Short period for SMA
            "sma_long_period": 200.0,  # Long period for SMA
            "ema_short_period": 20.0,  # Short period for EMA
            "ema_long_period": 50.0,  # Long period for EMA
            "rsi_period": 14.0,  # Period for RSI
            "macd_fast_period": 12.0,  # Fast period for MACD
            "macd_slow_period": 26.0,  # Slow period for MACD
            "macd_signal_period": 9.0,  # Signal period for MACD
            "bollinger_window": 20.0,  # Period for Bollinger Bands
            "bollinger_std_dev": 2.0,  # Standard deviation for Bollinger Bands
            "stoch_k_period": 14.0,  # Stochastic K period
            "stoch_kslow_period": 3.0,  # Stochastic K slowing period
            "stoch_d_period": 14.0,  # Stochastic D period
            "adx_period": 14.0,  # Period for ADX (Average Directional Index)
            "buy_threshold": 6,  # Number of conditions for a buy signal
            "sell_threshold": 6,  # Number of conditions for a sell signal
        }

        self.clamps = {
            "sma_short_period": [5, 50.0, 100, 0.5],
            "sma_long_period": [5, 200.0, 100, 0.5],
            "ema_short_period": [5, 20.0, 100, 0.5],
            "ema_long_period": [5, 50.0, 100, 0.5],
            "rsi_period": [5, 14.0, 50, 0.5],
            "macd_fast_period": [5, 12.0, 50, 0.5],
            "macd_slow_period": [5, 26.0, 50, 0.5],
            "macd_signal_period": [5, 9.0, 50, 0.5],
            "bollinger_window": [5, 20.0, 50, 0.5],
            "bollinger_std_dev": [1, 2.0, 5, 0.5],
            "stoch_k_period": [5, 14.0, 50, 0.5],
            "stoch_kslow_period": [5, 3.0, 50, 0.5],
            "stoch_d_period": [5, 14.0, 50, 0.5],
            "adx_period": [5, 14.0, 50, 0.5],
            "buy_threshold": [1, 6, 10, 0.5],
            "sell_threshold": [1, 6, 10, 0.5],
        }

    def indicators(self, data):
        """
        Calculate classical indicators for the strategy.
        """
        # Simple Moving Averages (SMA)
        sma_short = qx.ti.sma(data["close"], self.tune["sma_short_period"])
        sma_long = qx.ti.sma(data["close"], self.tune["sma_long_period"])

        # Exponential Moving Averages (EMA)
        ema_short = qx.ti.ema(data["close"], self.tune["ema_short_period"])
        ema_long = qx.ti.ema(data["close"], self.tune["ema_long_period"])

        # Relative Strength Index (RSI)
        rsi = qx.ti.rsi(data["close"], self.tune["rsi_period"])

        # MACD (Moving Average Convergence Divergence)
        macd, macd_signal, _ = qx.ti.macd(
                data["close"],
                self.tune["macd_fast_period"],
                self.tune["macd_slow_period"],
                self.tune["macd_signal_period"],
            )

        # Bollinger Bands
        bbands_upper, bbands_middle, bbands_lower = qx.ti.bbands(
                data["close"],
                self.tune["bollinger_window"],
                self.tune["bollinger_std_dev"],
            )

        # Stochastic Oscillator (Stoch)
        stoch_k, stoch_d = qx.ti.stoch(
                data["high"],
                data["low"],
                data["close"],
                self.tune["stoch_k_period"],
                self.tune["stoch_kslow_period"],
                self.tune["stoch_d_period"],
            )

        # Average Directional Index (ADX)
        adx = qx.ti.adx(data["high"], data["low"], data["close"], self.tune["adx_period"])

        return {
            "sma_short": sma_short,
            "sma_long": sma_long,
            "ema_short": ema_short,
            "ema_long": ema_long,
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "bbands_upper": bbands_upper,
            "bbands_middle": bbands_middle,
            "bbands_lower": bbands_lower,
            "stoch_k": stoch_k,
            "stoch_d": stoch_d,
            "adx": adx,
        }

    def plot(self, *args):
        """
        Plot indicators for visual analysis.
        """
        qx.plot(
            *args,
            (
                ("sma_short", "SMA Short", "yellow", 0, "Trend"),
                ("sma_long", "SMA Long", "orange", 0, "Trend"),
                ("ema_short", "EMA Short", "blue", 0, "Trend"),
                ("ema_long", "EMA Long", "green", 0, "Trend"),
                ("rsi", "RSI", "purple", 1, "Momentum"),
                ("macd", "MACD", "red", 1, "Momentum"),
                ("macd_signal", "MACD Signal", "cyan", 1, "Momentum"),
                ("bbands_upper", "Bollinger Upper", "green", 0, "Volatility"),
                ("bbands_middle", "Bollinger Middle", "blue", 0, "Volatility"),
                ("bbands_lower", "Bollinger Lower", "red", 0, "Volatility"),
                ("stoch_k", "Stochastic K", "orange", 1, "Momentum"),
                ("stoch_d", "Stochastic D", "brown", 1, "Momentum"),
                ("adx", "ADX", "black", 1, "Trend"),
            ),
        )

    def strategy(self, state, indicators):
        """
        Define strategy with classical indicators and complex logic.
        """
        if state["last_trade"] is None:
            # Enter market with all capital on the first trade
            return qx.Buy()

        # Buy Signal Logic
        buy_conditions = [
            # Short SMA above Long SMA (bullish trend)
            indicators["sma_short"] > indicators["sma_long"],
            # Short EMA above Long EMA (bullish trend)
            indicators["ema_short"] > indicators["ema_long"],
            # RSI below 30 (oversold)
            indicators["rsi"] < 30,
            # MACD above Signal line (bullish momentum)
            indicators["macd"] > indicators["macd_signal"],
            # Price breaking above upper Bollinger Band (breakout)
            indicators["close"] > indicators["bbands_upper"],
            # Stochastic K crosses above D (bullish signal)
            indicators["stoch_k"] > indicators["stoch_d"],
            # ADX above 25 (strong trend)
            indicators["adx"] > 25,
        ]

        if sum(buy_conditions) >= self.tune["buy_threshold"]:
            if isinstance(state["last_trade"], qx.Sell):
                # Exit short position and enter long with all capital
                return qx.Buy()

        # Sell Signal Logic
        sell_conditions = [
            # Short SMA below Long SMA (bearish trend)
            indicators["sma_short"] < indicators["sma_long"],
            # Short EMA below Long EMA (bearish trend)
            indicators["ema_short"] < indicators["ema_long"],
            # RSI above 70 (overbought)
            indicators["rsi"] > 70,
            # MACD below Signal line (bearish momentum)
            indicators["macd"] < indicators["macd_signal"],
            # Price breaking below lower Bollinger Band (breakdown)
            indicators["close"] < indicators["bbands_lower"],
            # Stochastic K crosses below D (bearish signal)
            indicators["stoch_k"] < indicators["stoch_d"],
            # ADX above 25 (strong trend)
            indicators["adx"] > 25,
        ]

        if sum(sell_conditions) >= self.tune["sell_threshold"]:
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

    bot = TradFiInspired()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
