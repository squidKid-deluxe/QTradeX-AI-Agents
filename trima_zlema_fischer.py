"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

trima_zlema_fischer.py

TrimaZlemaFisher 

Indicators:

1. **ZLEMA**: A moving average that reduces lag, providing a more responsive signal to price changes. 
It is calculated using a specified period and its derivative is also computed to assess momentum.

2. **TRIMA**: A moving average that gives more weight to the middle of the price range, smoothing out price fluctuations. 
Its derivative is calculated to confirm the trend's strength.

3. **Fisher Transform**: A technical indicator that transforms prices into a Gaussian normal distribution, allowing for 
clearer identification of potential reversals. The Fisher Transform and its signal line are both calculated,
 along with their derivatives for momentum confirmation.

Strategy:

The bot employs a set of criteria to generate buy and sell signals based on the aforementioned indicators and their derivatives. 
A buy signal is triggered when a combination of bullish conditions is met, such as 
ZLEMA being above TRIMA, positive derivatives, and a bullish crossover in the Fisher Transform. 


Conversely, a sell signal is generated when bearish conditions are satisfied, including 
ZLEMA being below TRIMA, negative derivatives, and a bearish crossover in the Fisher Transform. 
"""


import time

import numpy as np
import qtradex as qx


class TrimaZlemaFisher(qx.BaseBot):
    def __init__(self):
        # Default tuning values (periods for ZLEMA, TRIMA, and Fisher Transform)
        self.drop = {
            # Periods for indicators
            "zlema_period": 14.0,  # Period for Zero-Lag Exponential Moving Average (ZLEMA)
            "trima_period": 14.0,  # Period for Triangular Moving Average (TRIMA)
            "fisher_period": 14.0,  # Period for Fisher Transform
            # Thresholds for Buy and Sell signals
            "buy_threshold": 3,  # Number of conditions required to trigger a buy signal
            "sell_threshold": 3,  # Number of conditions required to trigger a sell signal
            # Derivative thresholds for momentum confirmation
            "zlema_d_threshold": 0.0,  # Derivative threshold for ZLEMA
            "trima_d_threshold": 0.0,  # Derivative threshold for TRIMA
            "fisher_d_threshold": 0.0,  # Derivative threshold for Fisher Transform
            # Threshold for ZLEMA > TRIMA (bullish) and ZLEMA < TRIMA (bearish)
            "zlema_trima_bear": 0.0,  # Difference threshold between ZLEMA and TRIMA for confirmation
            "zlema_trima_bull": 0.0,  # Difference threshold between ZLEMA and TRIMA for confirmation
        }

        self.tune = {
            "zlema_period": 16.079811096409834,
            "trima_period": 12.359240918039314,
            "fisher_period": 13.159103070899896,
            "buy_threshold": 4,
            "sell_threshold": 3,
            "zlema_d_threshold": 1.7775721207853355e-05,
            "trima_d_threshold": 0.002318766926234281,
            "fisher_d_threshold": -0.003962869346491464,
            "zlema_trima_bear": 0.006053328773750694,
            "zlema_trima_bull": 0.006184075655839947,
        }

        # Optimizer clamps (min, max, strength)
        self.clamps = {
            "zlema_period": [5, 14.0, 50, 0.5],
            "trima_period": [5, 14.0, 50, 0.5],
            "fisher_period": [5, 14.0, 50, 0.5],
            "buy_threshold": [1, 3, 5, 1],
            "sell_threshold": [1, 3, 5, 1],
            "zlema_d_threshold": [-1, 0.0, 1, 0.5],
            "trima_d_threshold": [-1, 0.0, 1, 0.5],
            "fisher_d_threshold": [-1, 0.0, 1, 0.5],
            "zlema_trima_bear": [0, 0.0, 1, 0.5],
            "zlema_trima_bull": [0, 0.0, 1, 0.5],
        }

    def indicators(self, data):
        """
        Calculate the indicators used in the strategy.
        """
        # Zero-Lag Exponential Moving Average (ZLEMA)
        zlema = qx.ti.zlema(data["close"], self.tune["zlema_period"])

        # Derivative of Zero-Lag Exponential Moving Average (ZLEMA)
        zlema_derivative = qx.derivative(zlema)

        # Triangular Moving Average (TRIMA)
        trima = qx.ti.trima(data["close"], self.tune["trima_period"])

        # Derivative of Triangular Moving Average (TRIMA)
        trima_derivative = qx.derivative(trima)

        # Fisher Transform (FT)
        fisher, fisher_signal = qx.ti.fisher(
            data["high"], data["low"], self.tune["fisher_period"]
        )

        # Derivative of Fisher Transform (FT)
        fisher_derivative = qx.derivative(fisher)

        # Derivative of Fisher Signal
        fisher_signal_derivative = qx.derivative(fisher_signal)

        return {
            "zlema": zlema,
            "trima": trima,
            "fisher": fisher,
            "fisher_signal": fisher_signal,
            "zlema_derivative": zlema_derivative,
            "trima_derivative": trima_derivative,
            "fisher_derivative": fisher_derivative,
            "fisher_signal_derivative": fisher_signal_derivative,
        }

    def plot(self, *args):
        """
        Plot indicators for visual analysis.
        """
        qx.plot(
            self.info,
            *args,
            (
                ("zlema", "Zero-Lag EMA", "yellow", 0, "Smoothing"),
                ("trima", "Triangular Moving Average", "green", 0, "Smoothing"),
                ("fisher", "Fisher Transform", "blue", 2, "Reversal"),
                ("fisher_signal", "Fisher Signal", "cyan", 2, "Reversal"),
                ("zlema_derivative", "ZLEMA Derivative", "red", 1, "Momentum"),
                ("trima_derivative", "TRIMA Derivative", "purple", 1, "Momentum"),
                ("fisher_derivative", "Fisher Derivative", "orange", 1, "Momentum"),
                (
                    "fisher_signal_derivative",
                    "Fisher Signal Derivative",
                    "pink",
                    1,
                    "Momentum",
                ),
            ),
        )

    def strategy(self, state, indicators):
        """
        Define strategy based on ZLEMA, TRIMA, and Fisher Transform with their derivatives.
        """
        if state["last_trade"] is None:
            # Enter market with all capital on the first trade
            return qx.Buy()

        # Bullish Signal Criteria
        if (
            sum(
                [
                    int(
                        indicators["zlema"]
                        > indicators["trima"] + self.tune["zlema_trima_bull"]
                    ),  # ZLEMA > TRIMA (Bullish)
                    int(
                        indicators["zlema_derivative"] > self.tune["zlema_d_threshold"]
                    ),  # Positive ZLEMA derivative
                    int(
                        indicators["trima_derivative"] > self.tune["trima_d_threshold"]
                    ),  # Positive TRIMA derivative
                    int(
                        indicators["fisher"] > indicators["fisher_signal"]
                    ),  # Fisher crossover (bullish)
                    int(
                        indicators["fisher_derivative"]
                        > self.tune["fisher_d_threshold"]
                    ),  # Positive Fisher derivative
                    int(
                        indicators["fisher_signal_derivative"]
                        > self.tune["fisher_d_threshold"]
                    ),  # Positive Fisher Signal derivative
                ]
            )
            >= self.tune["buy_threshold"]
        ):
            if isinstance(state["last_trade"], qx.Sell):
                # Exit short position and enter long with all capital
                return qx.Buy()

        # Bearish Signal Criteria
        if (
            sum(
                [
                    int(
                        indicators["zlema"]
                        < indicators["trima"] - self.tune["zlema_trima_bear"]
                    ),  # ZLEMA < TRIMA (Bearish)
                    int(
                        indicators["zlema_derivative"] < self.tune["zlema_d_threshold"]
                    ),  # Negative ZLEMA derivative
                    int(
                        indicators["trima_derivative"] < self.tune["trima_d_threshold"]
                    ),  # Negative TRIMA derivative
                    int(
                        indicators["fisher"] < indicators["fisher_signal"]
                    ),  # Fisher crossover (bearish)
                    int(
                        indicators["fisher_derivative"]
                        < self.tune["fisher_d_threshold"]
                    ),  # Negative Fisher derivative
                    int(
                        indicators["fisher_signal_derivative"]
                        < self.tune["fisher_d_threshold"]
                    ),  # Negative Fisher Signal derivative
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

    bot = TrimaZlemaFisher()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
