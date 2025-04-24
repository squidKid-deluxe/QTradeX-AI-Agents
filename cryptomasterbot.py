"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

cryptomasterbot.py

CryptoMasterBot 

Indicators:

- Utilizes a variety of technical indicators, including:
  - Simple Moving Average (SMA) and Exponential Moving Average (EMA) for trend analysis
  - Relative Strength Index (RSI) for momentum assessment
  - Moving Average Convergence Divergence (MACD) for trend strength and momentum
  - Bollinger Bands for volatility and price levels
  - Fisher Transform for identifying potential reversals
  - Stochastic Oscillator for momentum and overbought/oversold conditions
  - Average Directional Index (ADX) for trend confirmation
  - Volatility indicator to gauge market fluctuations

Strategy:

- The strategy is based on a combination of these indicators to generate buy and sell signals:
  - **Buy Signal**: Triggered when the RSI indicates oversold conditions (below 30), 
  the MACD crosses above its signal line, the price is above the upper Bollinger Band, 
  the Stochastic K line crosses above the D line, the ADX confirms trend strength, and volatility is increasing.
  
  - **Sell Signal**: Triggered when the RSI indicates overbought conditions (above 70), 
  the MACD crosses below its signal line, the price is below the lower Bollinger Band, 
  the Stochastic K line crosses below the D line, the ADX confirms trend strength, and volatility is increasing.
"""
import time

import numpy as np
import qtradex as qx


class CryptoMasterBot(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "sma_period": 20.0,  # Period for Simple Moving Average (SMA)
            "ema_period": 14.0,  # Period for Exponential Moving Average (EMA)
            "rsi_period": 14.0,  # Period for Relative Strength Index (RSI)
            "macd_short_period": 12.0,  # MACD short period
            "macd_long_period": 26.0,  # MACD long period
            "macd_signal_period": 9.0,  # MACD signal period
            "bollinger_period": 20.0,  # Bollinger Bands period
            "bollinger_deviation": 2.0,  # Bollinger Bands standard deviation
            "fisher_period": 14.0,  # Fisher Transform period
            "stoch_k_period": 14.0,  # Stochastic K period
            "stoch_kslow_period": 3.0,  # Stochastic K slowing period
            "stoch_d_period": 14.0,  # Stochastic D period
            "adx_period": 14.0,  # Average Directional Index (ADX) period
            "adx_threshold": 25.0,  # ADX threshold for trend confirmation
            "volatility_period": 14.0,  # Volatility indicator period
            "buy_threshold": 6,  # Number of conditions for a buy signal
            "sell_threshold": 6,  # Number of conditions for a sell signal
        }

        self.clamps = {
            "sma_period": [5, 20.0, 100, 0.5],
            "ema_period": [5, 14.0, 100, 0.5],
            "rsi_period": [5, 14.0, 50, 0.5],
            "macd_short_period": [5, 12.0, 50, 0.5],
            "macd_long_period": [5, 26.0, 50, 0.5],
            "macd_signal_period": [5, 9.0, 50, 0.5],
            "bollinger_period": [5, 20.0, 100, 0.5],
            "bollinger_deviation": [1, 2.0, 5, 0.5],
            "fisher_period": [5, 14.0, 50, 0.5],
            "stoch_k_period": [5, 14.0, 50, 0.5],
            "stoch_kslow_period": [5, 3.0, 50, 0.5],
            "stoch_d_period": [5, 14.0, 50, 0.5],
            "adx_period": [5, 14.0, 50, 0.5],
            "adx_threshold": [10, 25.0, 50, 0.5],
            "volatility_period": [5, 14.0, 100, 0.5],
            "buy_threshold": [2, 6, 6, 1],
            "sell_threshold": [2, 6, 6, 1],
        }

    def indicators(self, data):
        """
        Calculate the various indicators for the strategy.
        """
        # Simple Moving Average (SMA)
        sma = qx.ti.sma(data["close"], self.tune["sma_period"])

        # Exponential Moving Average (EMA)
        ema = qx.ti.ema(data["close"], self.tune["ema_period"])

        # Relative Strength Index (RSI)
        rsi = qx.ti.rsi(data["close"], self.tune["rsi_period"])

        # MACD (Moving Average Convergence Divergence)
        macd, macd_signal, _ = qx.ti.macd(
            data["close"],
            self.tune["macd_short_period"],
            self.tune["macd_long_period"],
            self.tune["macd_signal_period"],
        )

        # Bollinger Bands
        upper_band, middle_band, lower_band = qx.ti.bbands(
            data["close"],
            self.tune["bollinger_period"],
            self.tune["bollinger_deviation"],
        )

        # Fisher Transform
        fisher, fisher_signal = qx.ti.fisher(
            data["high"], data["low"], self.tune["fisher_period"]
        )

        # Stochastic Oscillator
        stoch_k, stoch_d = qx.ti.stoch(
            data["high"],
            data["low"],
            data["close"],
            self.tune["stoch_k_period"],
            self.tune["stoch_kslow_period"],
            self.tune["stoch_d_period"],
        )

        # Average Directional Index (ADX)
        adx = qx.ti.adx(
            data["high"], data["low"], data["close"], self.tune["adx_period"]
        )

        # Volatility indicator (standard deviation of price)
        volatility = qx.ti.stddev(data["close"], self.tune["volatility_period"])

        return {
            "sma": sma,
            "ema": ema,
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "upper_band": upper_band,
            "middle_band": middle_band,
            "lower_band": lower_band,
            "fisher": fisher,
            "fisher_signal": fisher_signal,
            "stoch_k": stoch_k,
            "stoch_d": stoch_d,
            "adx": adx,
            "volatility": volatility,
        }

    def plot(self, *args):
        """
        Plot indicators for visual analysis.
        """
        qx.plot(
            self.info,
            *args,
            (
                ("sma", "SMA", "yellow", 0, "Trend"),
                ("ema", "EMA", "blue", 0, "Trend"),
                ("rsi", "RSI", "green", 1, "Momentum"),
                ("macd", "MACD", "purple", 1, "Momentum"),
                ("macd_signal", "MACD Signal", "red", 1, "Momentum"),
                ("upper_band", "Bollinger Upper", "cyan", 0, "Volatility"),
                ("middle_band", "Bollinger Middle", "orange", 0, "Volatility"),
                ("lower_band", "Bollinger Lower", "pink", 0, "Volatility"),
                ("fisher", "Fisher", "blue", 0, "Reversal"),
                ("fisher_signal", "Fisher Signal", "cyan", 0, "Reversal"),
                ("stoch_k", "Stochastic K", "purple", 1, "Momentum"),
                ("stoch_d", "Stochastic D", "red", 1, "Momentum"),
                ("adx", "ADX", "green", 0, "Trend Strength"),
                ("volatility", "Volatility", "magenta", 1, "Volatility"),
            ),
        )

    def strategy(self, state, indicators):
        """
        Define strategy based on a mix of indicators.
        """
        if state["last_trade"] is None:
            # Enter market with all capital on the first trade
            return qx.Buy()

        # Buy signal criteria
        if (
            sum(
                [
                    int(indicators["rsi"] < 30),  # RSI below 30 (oversold)
                    int(
                        indicators["macd"] > indicators["macd_signal"]
                    ),  # MACD cross above signal
                    int(
                        state["close"] > indicators["upper_band"]
                    ),  # Price above upper Bollinger Band
                    int(
                        indicators["stoch_k"] > indicators["stoch_d"]
                    ),  # Stochastic K above D (bullish crossover)
                    int(
                        indicators["adx"] > self.tune["adx_threshold"]
                    ),  # ADX confirms trend strength
                    int(indicators["volatility"] > 0.02),  # Volatility increasing
                ]
            )
            >= self.tune["buy_threshold"]
        ):
            if isinstance(state["last_trade"], qx.Sell):
                # Exit short position and enter long with all capital
                return qx.Buy()

        # Sell signal criteria
        if (
            sum(
                [
                    int(indicators["rsi"] > 70),  # RSI above 70 (overbought)
                    int(
                        indicators["macd"] < indicators["macd_signal"]
                    ),  # MACD cross below signal
                    int(
                        state["close"] < indicators["lower_band"]
                    ),  # Price below lower Bollinger Band
                    int(
                        indicators["stoch_k"] < indicators["stoch_d"]
                    ),  # Stochastic K below D (bearish crossover)
                    int(
                        indicators["adx"] > self.tune["adx_threshold"]
                    ),  # ADX confirms trend strength
                    int(indicators["volatility"] > 0.02),  # Volatility increasing
                ]
            )
            >= self.tune["sell_threshold"]
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

    bot = CryptoMasterBot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
