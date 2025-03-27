"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

blackhole_strategy.py

Black Hole Strategy

Indicators:

    - atr: Average True Range, for volatility measurement
    - sma: Simple Moving Average, for trend detection
    - volatility_surge: Detects extreme spikes in ATR to detect sudden price movements
    - support_level: A dynamic support level based on the SMA and volatility
    - resistance_level: A dynamic resistance level based on the SMA and volatility
    - momentum_signal: A custom momentum signal based on fast/slow crossover of moving averages
    - blackhole_zone: A unique zone of extreme price compression (uses ATR and SMA)
    - buy_zone: The price level when entering a position based on dynamic support and volatility

Strategy:

    - Black Hole: The market is in a "black hole" when ATR is below a certain threshold 
    and price is squeezed between support and resistance.

    - Momentum Expansion: When volatility surges (ATR spike), we anticipate a breakout above or below the compression zone.

    - Compression Trigger: When price enters the "blackhole_zone" (ATR compression and low price movement),
     we start preparing for a momentum-driven expansion.

    - Buy Trigger: Once a significant momentum signal (e.g., crossover or ATR spike) breaks out from the blackhole_zone.
    
    - Sell Trigger: We exit a position when price breaks below support or fails to hold above resistance.

"""

import time

import numpy as np
import qtradex as qx


class BlackHoleStrategy(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "sma_period": 50.0,
            "atr_period": 14.0,
            "compression_factor": 0.2,
            "momentum_trigger": 0.1,
            "volatility_surge_factor": 2.5,
        }

        self.clamps = [
            [5, 200, 0.5],
            [5, 50, 0.5],
            [0.05, 1.0, 0.5],
            [0.05, 1.0, 0.5],
            [1.0, 5.0, 0.5],
        ]

    def indicators(self, data):
        metrics = {
            "sma": qx.float_period(
                qx.tu.sma, (data["close"], self.tune["sma_period"]), (1,)
            ),
            "atr": qx.float_period(
                qx.tu.atr,
                (data["high"], data["low"], data["close"], self.tune["atr_period"]),
                (3,),
            ),
        }

        # Detect volatility surge
        metrics["volatility_surge"] = [
            atr
            > np.mean(metrics["atr"][-int(self.tune["atr_period"])])
            * self.tune["volatility_surge_factor"]
            for atr in metrics["atr"]
        ]

        # Calculate dynamic support and resistance based on SMA and volatility
        metrics["support_level"] = [
            sma - atr * self.tune["compression_factor"]
            for sma, atr in zip(metrics["sma"], metrics["atr"])
        ]

        metrics["resistance_level"] = [
            sma + atr * self.tune["compression_factor"]
            for sma, atr in zip(metrics["sma"], metrics["atr"])
        ]

        # Custom momentum signal based on crossover of short and long moving averages
        metrics["momentum_signal"] = np.diff(metrics["sma"], axis=0)

        # Detect "black hole" zone (low volatility and price compression)
        metrics["blackhole_zone"] = [
            atr
            < np.mean(metrics["atr"][-int(self.tune["atr_period"])])
            * self.tune["compression_factor"]
            for atr in metrics["atr"]
        ]

        return metrics

    def plot(self, data, states, indicators, block):
        axes = qx.plot(
            data,
            states,
            indicators,
            False,
            (
                ("sma", "SMA", "blue", 0, "Trend"),
                ("support_level", "Support Level", "green", 0, "Levels"),
                ("resistance_level", "Resistance Level", "red", 0, "Levels"),
                ("blackhole_zone", "Blackhole Zone", "yellow", 0, "Market Condition"),
            ),
        )

        # Highlight the blackhole zone for visual representation
        axes[0].fill_between(
            states["unix"],
            indicators["support_level"],
            indicators["resistance_level"],
            where=indicators["blackhole_zone"],
            color="orange",
            alpha=0.4,
            label="Blackhole Zone",
        )

        axes[0].legend()
        qx.plotmotion(block)

    def strategy(self, tick_info, indicators):
        # If price enters the "blackhole zone", it's a signal for potential expansion
        if (
            indicators["blackhole_zone"]
            and indicators["momentum_signal"] > self.tune["momentum_trigger"]
        ):
            if isinstance(tick_info["last_trade"], qx.Sell):
                return qx.Buy()

        # Check for volatility surge to trigger breakout
        if any(indicators["volatility_surge"]) and isinstance(
            tick_info["last_trade"], qx.Buy
        ):
            return qx.Sell()

        # Default strategy: Follow support/resistance levels
        if tick_info["last_trade"] is None:
            return qx.Buy()

        if tick_info["last_trade"] is not None:
            return qx.Thresholds(
                buying=indicators["support_level"],
                selling=indicators["resistance_level"],
            )

        return None

    def fitness(self, states, raw_states, asset, currency):
        return [
            "roi_assets",
            "roi_currency",
            "roi",
            "sortino",
            "maximum_drawdown",
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

    bot = BlackHoleStrategy()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
