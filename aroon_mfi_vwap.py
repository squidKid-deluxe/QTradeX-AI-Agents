"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

aroon_mfi_vwap.py

Aroon MFI VWAP

Indicators:

- Short Exponential Moving Average (EMA)
- Aroon Indicator
- Money Flow Index (MFI)
- Volume Weighted Average Price (VWAP)

Strategy:

qx.Buy Signal:

- The difference between `aroon_up` and `aroon_down` is greater than the specified threshold for buying (`aroon_buy`).
- The `short_ema` is less than the `vwap`, indicating that the market may be oversold.


qx.Sell Signal:

- The MFI is greater than the specified threshold (`mfi`), indicating overbought conditions.
- The difference between `aroon_up` and `aroon_down` is less than the specified threshold for selling (`aroon_sell`).
- The `short_ema` is greater than the `vwap`, suggesting a potential reversal to a downtrend.
"""
import math

import numpy as np
import qtradex as qx


class AroonMfiVwap(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "short_period": 2.0,
            "vwap_period": 8.0,
            "mfi_period": 30.0,
            "mfi": 41.0,
            "aroon_period": 105,
            "aroon_buy": 0.0,
            "aroon_sell": 0.0,
        }

        # fmt: off
        self.clamps = {
            # min, max, strength
            "short_period": [1, 2.0,  200, 0.5],
            "vwap_period":  [1, 8.0,  200, 0.5],
            "mfi_period":   [1, 30.0, 200, 0.5],
            "mfi":          [1, 41.0, 200, 0.5],
            "aroon_period": [1, 105,  200, 0.5],
            "aroon_buy":    [0, 0.0,  100, 1],
            "aroon_sell":   [0, 0.0,  100, 1],
        }
        # fmt: on

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            (
                ("vwap", "VWAP", "blue", 0, "Primary"),
                ("short_ema", "Short EMA", "white", 0, "Primary"),
                ("mfi", "MFI", "yellow", 1, "Secondary"),
                ("aroon_down", "AROON_down", "red", 1, "Secondary"),
                ("aroon_up", "AROON_up", "green", 1, "Secondary"),
            ),
        )

    def indicators(self, data):
        short_ema = qx.ti.ema(data["close"], self.tune["short_period"])
        mfi = qx.ti.mfi(
            data["high"],
            data["low"],
            data["close"],
            data["volume"],
            self.tune["mfi_period"],
        )
        vwap = qx.ti.vwma(data["close"], data["volume"], self.tune["vwap_period"])
        aroon_down, aroon_up = qx.ti.aroon(
            data["high"], data["low"], self.tune["aroon_period"]
        )

        return {
            "short_ema": short_ema,
            "aroon_down": aroon_down,
            "aroon_up": aroon_up,
            "mfi": mfi,
            "vwap": vwap,
        }

    def strategy(self, state, indicators):
        # Strategy conditions
        if (indicators["aroon_up"] - indicators["aroon_down"]) > self.tune["aroon_buy"]:
            if indicators["short_ema"] < indicators["vwap"]:
                if state["last_trade"] is None or isinstance(
                    state["last_trade"], qx.Sell
                ):
                    return qx.Buy()  # qx.Buy signal

        elif indicators["mfi"] > self.tune["mfi"]:
            if (indicators["aroon_up"] - indicators["aroon_down"]) < self.tune[
                "aroon_sell"
            ]:
                if indicators["short_ema"] > indicators["vwap"]:
                    if state["last_trade"] is None or isinstance(
                        state["last_trade"], qx.Buy
                    ):
                        return qx.Sell()  # qx.Sell signal

        return None  # No action if conditions are not met

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

    bot = AroonMfiVwap()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
