import numpy as np
import qtradex as qx


class VortexIndicatorBot(qx.BaseBot):
    def __init__(self):
        # Vortex Indicator parameters
        self.tune = {
            "vortex_period": 14.0,
        }
        self.clamps = {
            "vortex_period": [5, 14.0, 100, 1],
        }

    def indicators(self, data):
        # Calculate Vortex Indicator components using the provided vortex_indicator function
        vortex_data = qx.qi.vortex(
            data["high"], data["low"], self.tune["vortex_period"]
        )

        # Return the calculated indicators
        return {
            "vortex_plus": vortex_data[0],
            "vortex_minus": vortex_data[1],
            "vortex": vortex_data[2],
        }

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            (
                ("vortex_plus", "Vortex Plus", "green", 1, "Main"),
                ("vortex_minus", "Vortex Minus", "red", 0, "Main"),
                ("vortex", "Vortex", "blue", 2, "Main"),
            ),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()

        # Buy signal: Vortex Plus crosses above Vortex Minus
        if indicators["vortex_plus"] > indicators["vortex_minus"] and isinstance(
            state["last_trade"], qx.Sell
        ):
            return qx.Buy()

        # Sell signal: Vortex Plus crosses below Vortex Minus
        if indicators["vortex_plus"] < indicators["vortex_minus"] and isinstance(
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

    bot = VortexIndicatorBot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
