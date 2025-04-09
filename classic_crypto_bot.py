"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

classic_crypto_bot.py

ClassicalCryptoBot 

Indicators:

- Utilizes a set of well-established technical indicators including:
  - Simple Moving Average (SMA)
  - Exponential Moving Average (EMA)
  - Relative Strength Index (RSI)
  - Stochastic Oscillator (Stoch)
  - Average Directional Index (ADX)

Strategy:

- The strategy is based on a combination of these indicators to generate buy and sell signals:

  - **Buy Signal**: Triggered when the market is considered oversold (RSI < 30, Stochastic K < 20) 
  and the trend is bullish (SMA > EMA, ADX > 25).

  - **Sell Signal**: Triggered when the market is considered overbought (RSI > 70, Stochastic K > 80) 
  and the trend is bearish (SMA < EMA, ADX > 25).
"""


import numpy as np
import qtradex as qx


class ClassicalCryptoBot(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "sma_period": 50.0,  # Period for Simple Moving Average (SMA)
            "ema_period": 20.0,  # Period for Exponential Moving Average (EMA)
            "rsi_period": 14.0,  # Period for Relative Strength Index (RSI)
            "stoch_k_period": 14.0,  # Period for Stochastic Oscillator
            "stoch_kslow_period": 14.0,  # Period for Stochastic Oscillator
            "stoch_d_period": 14.0,  # Period for Stochastic Oscillator
            "adx_period": 14.0,  # Period for ADX (Average Directional Index)
            "crossover_threshold": 2,  # Threshold for crossover-based strategy
            "buy_threshold": 4,  # Number of conditions for a buy signal
            "sell_threshold": 4,  # Number of conditions for a sell signal
        }

        # fmt: off
        self.clamps = {
            "sma_period":          [5, 50.0, 100, 0.5],
            "ema_period":          [5, 20.0, 100, 0.5],
            "rsi_period":          [5, 14.0, 50,  0.5],
            "stoch_k_period":      [5, 14.0, 50,  0.5],
            "stoch_kslow_period":  [5, 14.0, 50,  0.5],
            "stoch_d_period":      [5, 14.0, 50,  0.5],
            "adx_period":          [5, 14.0, 50,  0.5],
            "crossover_threshold": [1, 2,    5,   1],
            "buy_threshold":       [1, 4,    5,   1],
            "sell_threshold":      [1, 4,    5,   1],
        }
        # fmt: on

    def indicators(self, data):
        """
        Calculate the classical indicators for the strategy.
        """
        # Simple Moving Average (SMA)
        sma = qx.ti.sma(data["close"], self.tune["sma_period"])

        # Exponential Moving Average (EMA)
        ema = qx.ti.ema(data["close"], self.tune["ema_period"])

        # Relative Strength Index (RSI)
        rsi = qx.ti.rsi(data["close"], self.tune["rsi_period"])

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
            "sma": sma,
            "ema": ema,
            "rsi": rsi,
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
                ("sma", "SMA", "yellow", 0, "Trend"),
                ("ema", "EMA", "blue", 0, "Trend"),
                ("rsi", "RSI", "green", 1, "Momentum"),
                ("stoch_k", "Stochastic K", "orange", 1, "Momentum"),
                ("stoch_d", "Stochastic D", "purple", 1, "Momentum"),
                ("adx", "ADX", "red", 1, "Trend Strength"),
            ),
        )

    def strategy(self, state, indicators):
        """
        Define strategy based on the combination of classical indicators.
        """
        if state["last_trade"] is None:
            # Enter market with all capital on the first trade
            return qx.Buy()

        # Buy Signal Criteria: Combining indicators for an entry signal
        if (
            sum(
                [
                    int(indicators["rsi"] < 30),  # RSI below 30 (oversold)
                    int(indicators["stoch_k"] < 20),  # Stochastic K below 20 (oversold)
                    # SMA above EMA (bullish trend)
                    int(indicators["sma"] > indicators["ema"]),
                    int(indicators["adx"] > 25),  # ADX above 25 (strong trend)
                ]
            )
            >= self.tune["buy_threshold"]
        ):
            if isinstance(state["last_trade"], qx.Sell):
                # Exit short position and enter long with all capital
                return qx.Buy()

        # Sell Signal Criteria: Combining indicators for an exit signal
        if (
            sum(
                [
                    int(indicators["rsi"] > 70),  # RSI above 70 (overbought)
                    # Stochastic K above 80 (overbought)
                    int(indicators["stoch_k"] > 80),
                    # SMA below EMA (bearish trend)
                    int(indicators["sma"] < indicators["ema"]),
                    int(indicators["adx"] > 25),  # ADX above 25 (strong trend)
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

    bot = ClassicalCryptoBot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
