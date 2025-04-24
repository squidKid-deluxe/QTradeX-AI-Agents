"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

cthulhu.py

Cthulhu Bollinger Bands

Indicators:

1. **Exponential Moving Average (EMA)**:
   - The bot calculates the 14-period EMA (`ma0`) for trend tracking. 
   The EMA is a weighted moving average that gives more weight to recent prices.
   - `ma1` is a shifted version of `ma0` used for comparing price movements.

2. **Standard Deviation (Std)**:
   - The bot calculates the 14-period standard deviation (`std`) of the closing price, 
   which is used to measure price volatility.
   - This helps define the upper and lower bounds (channel) around the EMA.

3. **Upper and Lower Channels**:
   - The upper and lower bands are calculated as:
     - Upper Channel = EMA + (Upper Deviations * Std)
     - Lower Channel = EMA - (Lower Deviations * Std)
   - These bands are used for channel trading, 
   signaling buy and sell opportunities when the price moves outside of these bands.

4. **Parabolic SAR (PSAR)**:
   - The bot uses the Parabolic SAR to track the market trend. 
   The PSAR values (`sar0` and `sar1`) help identify trend reversals, 
   signaling potential buy or sell opportunities when the SAR crosses the EMA.

Strategy:

1. **Channel Trading**:
   - If the price is within the channel (i.e., `diff` is less than the specified threshold `channel`), 
   the bot checks if the price is lower than the lower channel (buy condition) 
   or higher than the upper channel (sell condition).
   - **qx.Buy Signal**: Price * `channel_buy_factor` < Lower Channel
   - **qx.Sell Signal**: Price * `channel_sell_factor` > Upper Channel

2. **Trending Market**:
   - If the price is trending (i.e., `diff` is greater than the `channel` threshold), 
   the bot checks if the price is above or below the EMA.
   - **qx.Buy Signal**: Price * `trend_buy_factor` > EMA
   - **qx.Sell Signal**: Price * `trend_sell_factor` < EMA

3. **Trend Reversal (SAR)**:
   - If the Parabolic SAR crosses the EMA (either from below to above or vice versa), 
   it signals a potential trend reversal.
   - **qx.Buy Signal**: SAR < EMA and previous SAR > previous EMA
   - **qx.Sell Signal**: SAR > EMA and previous SAR < previous EMA

4. **Breakout**:
   - The bot also checks for breakouts when the price moves above or below the EMA.
   - **qx.Buy Signal**: Price * `breakout_buy_factor` > EMA
   - **qx.Sell Signal**: Price * `breakout_sell_factor` < EMA
"""


import qtradex as qx


class Cthulhu(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "ema_period": 20.53,
            "std_period": 7.448,
            "upper_deviations": 1.781,
            "lower_deviations": 2.533,
            "channel_buy_factor": 1.746,
            "channel_sell_factor": 0.9373,
            "trend_buy_factor": 0.4987,
            "trend_sell_factor": 0.9355,
            "breakout_buy_factor": 0.5072,
            "breakout_sell_factor": 1.809,
            "sar_accel": 0.008457,
            "sar_max": 0.1174,
            "channel": 0.008094,
        }

        self.clamps = {
            "ema_period": [5, 14.0, 100, 0.5],
            "std_period": [5, 14.0, 100, 0.5],
            "upper_deviations": [1.0, 2.0, 4.0, 0.5],
            "lower_deviations": [1.0, 2.0, 4.0, 0.5],
            "channel_buy_factor": [0.5, 0.9, 2.0, 0.5],
            "channel_sell_factor": [0.5, 1.1, 2.0, 0.5],
            "trend_buy_factor": [0.5, 1.1, 2.0, 0.5],
            "trend_sell_factor": [0.5, 0.9, 2.0, 0.5],
            "breakout_buy_factor": [0.5, 1.05, 2.0, 0.5],
            "breakout_sell_factor": [0.5, 0.95, 2.0, 0.5],
            "sar_accel": [0.0001, 0.02, 0.2, 0.5],
            "sar_max": [0.0001, 0.2, 0.2, 0.5],
            "channel": [0.0001, 0.01, 0.2, 0.5],
        }

    def indicators(self, data):
        metrics = {}

        # Example for moving average (use QX's built-in indicators like EMA or SMA)
        metrics["ma0"] = qx.ti.ema(data["close"], self.tune["ema_period"])
        metrics["ma1"] = metrics["ma0"][:-1]
        metrics["std"] = qx.ti.stddev(data["close"], self.tune["std_period"])

        metrics["ma0"], metrics["ma1"], metrics["std"] = qx.truncate(
            metrics["ma0"], metrics["ma1"], metrics["std"]
        )

        metrics["upper"] = (
            metrics["ma0"] + self.tune["upper_deviations"] * metrics["std"]
        )  # Upper channel (example)
        metrics["lower"] = (
            metrics["ma0"] - self.tune["lower_deviations"] * metrics["std"]
        )  # Lower channel (example)

        # Difference for channel trading logic
        metrics["diff"] = metrics["upper"] - metrics["lower"]

        # Parabolic SAR (example, adjust according to your requirements)
        metrics["sar0"] = qx.ti.psar(
            data["high"], data["low"], self.tune["sar_accel"], self.tune["sar_max"]
        )
        metrics["sar1"] = metrics["sar0"][:-1]

        return metrics

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            (
                # key, name, color, index, title
                ("upper", "Upper Band", "white", 0, "Cthulhu"),
                ("lower", "Lower Band", "white", 0, "Cthulhu"),
                ("ma0", "Middle Band", "cyan", 0, "Cthulhu"),
                ("sar0", "Parabolic SAR", "yellow", 0, "Cthulhu"),
            ),
        )

    def strategy(self, tick_info, indicators):
        # Extracting values from the indicators and tune
        ma0 = indicators["ma0"]
        ma1 = indicators["ma1"]
        std = indicators["std"]
        upper = indicators["upper"]
        lower = indicators["lower"]
        price = tick_info["close"]
        diff = indicators["diff"]
        sar0 = indicators["sar0"]
        sar1 = indicators["sar1"]

        channel_buy_factor = self.tune["channel_buy_factor"]
        channel_sell_factor = self.tune["channel_sell_factor"]
        trend_buy_factor = self.tune["trend_buy_factor"]
        trend_sell_factor = self.tune["trend_sell_factor"]
        breakout_buy_factor = self.tune["breakout_buy_factor"]
        breakout_sell_factor = self.tune["breakout_sell_factor"]
        channel = self.tune["channel"]

        # PRICE IS CHANNELED:
        if diff < channel:
            if channel_buy_factor * price < lower[0]:
                return qx.Buy()
            elif channel_sell_factor * price > upper[0]:
                return qx.Sell()

        # PRICE IS TRENDING:
        else:
            if trend_buy_factor * price > ma0:
                return qx.Buy()
            elif trend_sell_factor * price < ma0:
                return qx.Sell()

        # TREND IS ENDING:
        if sar0 < ma0 and sar1 > ma1:
            return qx.Buy()

        if sar0 > ma0 and sar1 < ma1:
            return qx.Sell()

        # HOLDING:
        if breakout_buy_factor * price > ma0:
            return qx.Buy()
        elif breakout_sell_factor * price < ma0:
            return qx.Sell()

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
    wallet = qx.PaperWallet({asset: 0, currency: 1})
    data = qx.Data(
        exchange="kucoin",
        asset=asset,
        currency=currency,
        begin="2021-01-01",
        end="2023-01-01",
    )

    bot = Cthulhu()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
