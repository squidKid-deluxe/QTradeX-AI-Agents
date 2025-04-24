import numpy as np
import qtradex as qx


class KSTIndicatorBot(qx.BaseBot):
    def __init__(self):
        # KST parameters
        self.tune = {
            "roc1_period": 10.0,
            "roc2_period": 15.0,
            "roc3_period": 20.0,
            "roc4_period": 30.0,
            "kst_smoothing": 9.0,
        }
        self.clamps = {
            "roc1_period": [5, 10.0, 100, 1],
            "roc2_period": [5, 15.0, 100, 1],
            "roc3_period": [5, 20.0, 100, 1],
            "roc4_period": [5, 30.0, 100, 1],
            "kst_smoothing": [5, 9.0, 100, 1],
        }

    def indicators(self, data):
        # Calculate KST components using the provided kst function
        kst_data = qx.qi.kst(
            data["close"],
            self.tune["roc1_period"],
            self.tune["roc2_period"],
            self.tune["roc3_period"],
            self.tune["roc4_period"],
            self.tune["kst_smoothing"],
        )

        # Return the calculated indicators
        return {
            "kst": kst_data[0],
            "kst_signal": kst_data[1],
        }

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            (
                ("kst", "KST", "blue", 1, "Main"),
                ("kst_signal", "KST Signal", "orange", 1, "Main"),
            ),
        )

    def strategy(self, state, indicators):
        if state["last_trade"] is None:
            return qx.Buy()

        # Buy signal: KST crosses above KST Signal
        if indicators["kst"] > indicators["kst_signal"] and isinstance(
            state["last_trade"], qx.Sell
        ):
            return qx.Buy()

        # Sell signal: KST crosses below KST Signal
        if indicators["kst"] < indicators["kst_signal"] and isinstance(
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

    bot = KSTIndicatorBot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
