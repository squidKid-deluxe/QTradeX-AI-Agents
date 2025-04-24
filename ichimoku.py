import numpy as np
import qtradex as qx


class IchimokuBot(qx.BaseBot):
    def __init__(self):
        # Ichimoku parameters
        self.tune = {
            "tenkan_period": 9.5,
            "kijun_period": 26.1,
            "senkou_b_period": 52.9,
            "senkou_span": 26.2,
        }
        # fmt: off
        self.clamps = {
            "tenkan_period":   [5,  9.0, 150, 1],
            "kijun_period":    [5, 26.0, 150, 1],
            "senkou_b_period": [5, 52.0, 150, 1],
            "senkou_span":     [5, 26.0, 150, 1],
        }
        # fmt: on

    def indicators(self, data):
        # Calculate Ichimoku components using the provided ichimoku function
        (
            tenkan_sen,
            kijun_sen,
            senkou_span_a,
            senkou_span_b,
            chikou_span,
        ) = qx.qi.ichimoku(
            data["high"],
            data["low"],
            data["close"],
            self.tune["tenkan_period"],
            self.tune["kijun_period"],
            self.tune["senkou_b_period"],
            self.tune["senkou_span"],
        )

        # Return the calculated indicators
        return {
            "tenkan": tenkan_sen,
            "kijun": kijun_sen,
            "senkou_A": senkou_span_a,
            "senkou_B": senkou_span_b,
            "chikou": chikou_span,
        }

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            (
                ("tenkan", "Tenkan-sen", "green", 0, "Main"),
                ("kijun", "Kijun-sen", "red", 0, "Main"),
                ("senkou_A", "Senkou Span A", "blue", 0, "Main"),
                ("senkou_B", "Senkou Span B", "orange", 0, "Main"),
            ),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()

        # Buy signal: Senkou A crosses above Senkou B
        if indicators["senkou_A"] > indicators["senkou_B"] and isinstance(
            state["last_trade"], qx.Sell
        ):
            return qx.Buy()

        # Sell signal: Senkou A crosses below Senkou B
        if indicators["senkou_A"] < indicators["senkou_B"] and isinstance(
            state["last_trade"], qx.Buy
        ):
            return qx.Sell()

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
        end="2025-01-01",
    )

    bot = IchimokuBot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
