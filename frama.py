import numpy as np
import qtradex as qx


class FRAMABot(qx.BaseBot):
    def __init__(self):
        # FRAMA parameters
        self.tune = {
            "period": 14.0,
            "fractal_period": 2.0,
        }
        self.clamps = {
            "period": [2, 14.0, 100, 1],
            "fractal_period": [2, 2.0, 100, 1],
        }

    def indicators(self, data):
        # Calculate FRAMA using the provided frama function
        frama_values = qx.qi.frama(
            data["close"], self.tune["period"], self.tune["fractal_period"]
        )

        # Return the calculated indicators
        return {
            "frama": frama_values,
        }

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            (("frama", "FRAMA", "blue", 0, "Main"),),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()

        # Buy signal: Current price crosses above FRAMA
        if (
            isinstance(state["last_trade"], qx.Sell)
            and state["close"] > indicators["frama"]
        ):
            return qx.Buy()

        # Sell signal: Current price crosses below FRAMA
        if (
            isinstance(state["last_trade"], qx.Buy)
            and state["close"] < indicators["frama"]
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

    bot = FRAMABot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
