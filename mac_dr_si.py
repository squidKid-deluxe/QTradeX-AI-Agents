"""
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗═╗ ╦
║═╬╗║ ╠╦╝╠═╣ ║║║╣ ╔╩╦╝
╚═╝╚╩ ╩╚═╩ ╩═╩╝╚═╝╩ ╚═

bbadx_mac_dr_si.py

Big Bad X Mac Dr Scipy

Indicators:

- Uses the **MACD** (Moving Average Convergence Divergence) to identify trend reversals.

- Relies on the **RSI** (Relative Strength Index) to determine overbought and oversold conditions.

- Applies **Fourier Transform (FFT)** with a low-pass filter to remove high-frequency noise
 and highlight significant trends.

- Utilizes **ADX** (Average Directional Index) to measure the strength of the trend and 
distinguish between trending and range-bound markets.

- Incorporates customizable parameters for fine-tuning the strategy, including thresholds for Z-scores, 
FFT filters, and Bollinger Bands.

- Market regime detection: Uses ADX to determine whether the market is trending or range-bound.

Strategy:

- **Buy conditions**:
  - The MACD line must cross above the MACD signal line, indicating a bullish trend.
  - RSI should be above a specified threshold, indicating upward momentum.
  - The FFT filter should show positive signals, suggesting the presence of a dominant trend.
  
- **Sell conditions**:
  - The MACD line must cross below the MACD signal line, indicating a bearish trend.
  - RSI should fall below a specified threshold, indicating downward momentum.
  - The FFT filter should show negative signals, suggesting the trend is weakening.
"""

import numpy as np
import qtradex as qx
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt


class BBadXMacDrSi(qx.BaseBot):
    def __init__(self):
        # Parameters for the strategy (customizable through tuning)
        self.tune = {
            "macd_fast_period": 12.0,  # Fast period for MACD
            "macd_slow_period": 26.0,  # Slow period for MACD
            "macd_signal_period": 9.0,  # Signal period for MACD
            "rsi_period": 14.0,  # Period for RSI
            "adx_period": 14.0,  # Period for ADX
            "rsi_zscore_buy_threshold": 1.0,  # Z-score threshold for RSI when buying
            "rsi_zscore_sell_threshold": -1.0,  # Z-score threshold for RSI when selling
            "macd_zscore_buy_threshold": 1.0,  # Z-score threshold for MACD when buying
            "macd_zscore_sell_threshold": -1.0,  # Z-score threshold for MACD when selling
            "fft_filtered_buy": 0.0,  # Threshold for FFT filtered data when buying
            "fft_filtered_sell": 0.0,  # Threshold for FFT filtered data when selling
            "bollinger_std_dev": 2.0,  # Std deviation for Bollinger Bands
            "bollinger_window_size": 20,  # Window size for Bollinger Bands
            "adx_threshold": 25.0,  # ADX threshold to distinguish between trending and range-bound market
            "cutoff_frequency": 0.1,  # Low-pass filter cutoff frequency for FFT
            "low_pass_order": 3,  # Order of Butterworth filter
            "btype": 0,  # 0 for low-pass, 1 for high-pass, etc.
            "analog": 1,  # 1 for True, 0 for False (analog filter type)
            "fft_d": 1.0,  # Sampling interval for FFT
            # Control for flipping the direction of comparisons (0 = default, 1 = flipped)
            "macd_comparison": 0,  # 0 for no flip (MACD: '>' for Buy), 1 for flipped ('<' for Buy)
            "rsi_comparison": 0,  # 0 for no flip (RSI: '>' for Buy), 1 for flipped ('<' for Buy)
            "fft_comparison": 0,  # 0 for no flip (FFT: '>' for Buy), 1 for flipped ('<' for Buy)
        }

        # Optimizer clamps to limit the parameter ranges for optimization
        self.clamps = [
            [5, 20, 1.0],  # macd_fast_period
            [15, 50, 1.0],  # macd_slow_period
            [5, 15, 1.0],  # macd_signal_period
            [5, 30, 1.0],  # rsi_period
            [5, 30, 1.0],  # adx_period
            [0.0, 3.0, 0.1],  # rsi_zscore_buy_threshold
            [-3.0, 0.0, 0.1],  # rsi_zscore_sell_threshold
            [0.0, 3.0, 0.1],  # macd_zscore_buy_threshold
            [-3.0, 0.0, 0.1],  # macd_zscore_sell_threshold
            [-1, 1, 0.5],  # fft_filtered
            [-1, 1, 0.5],  # fft_filtered
            [1.5, 3.0, 0.1],  # bollinger_std_dev
            [10, 50, 1.0],  # bollinger_window_size
            [15.0, 40.0, 0.5],  # adx_threshold
            [0.01, 0.5, 0.01],  # cutoff_frequency
            [2, 5, 1],  # low_pass_order
            [0, 1, 1],  # btype (low=0, high=1, etc.)
            [0, 1, 1],  # analog (True=1, False=0)
            [0.1, 2.0, 0.01],  # fft_d (Sampling interval)
            [0, 1, 1],  # macd_comparison (0 = no flip, 1 = flipped)
            [0, 1, 1],  # rsi_comparison (0 = no flip, 1 = flipped)
            [0, 1, 1],  # fft_comparison (0 = no flip, 1 = flipped)
        ]

        # Initialize storage for trade details (e.g., holding positions, last trade info)
        self.storage = {"hold": 0, "last_trade_time": 0, "trade_price": 0}

    def indicators(self, data):
        """
        Calculate key technical indicators (MACD, RSI, FFT, and ADX) for strategy decision-making.
        """
        # MACD calculation: MACD line and Signal line
        macd_line, macd_signal, _ = qx.float_period(
            qx.tu.macd,
            (
                data["close"],
                self.tune["macd_fast_period"],
                self.tune["macd_slow_period"],
                self.tune["macd_signal_period"],
            ),
            (1, 2, 3),
        )

        # RSI (Relative Strength Index) calculation: Momentum indicator that tells overbought/oversold conditions
        rsi = qx.float_period(qx.tu.rsi, (data["close"], self.tune["rsi_period"]), (1,))

        # FFT (Fast Fourier Transform): Frequency analysis to detect underlying cyclical patterns
        fft_data = fft(data["close"])
        fft_freqs = fftfreq(
            len(data["close"]), d=self.tune["fft_d"]
        )  # Frequencies for FFT
        # Low-pass filter applied to FFT data to remove high-frequency noise and isolate significant trends
        fft_filtered = self.low_pass_filter(fft_data)

        # ADX (Average Directional Index): Measures trend strength
        adx = qx.float_period(
            qx.tu.adx,
            (data["high"], data["low"], data["close"], self.tune["adx_period"]),
            (3,),
        )

        return {
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "rsi": rsi,
            "fft_filtered": fft_filtered,
            "adx": adx,
        }

    def low_pass_filter(self, data):
        """
        Apply a low-pass filter to the FFT data to remove high-frequency noise and extract the primary trend.
        This is done by applying a Butterworth filter to the data.
        """
        # Select filter type based on configuration (low-pass, high-pass, etc.)
        btype_map = ["low", "high", "bandpass", "bandstop"]
        btype = btype_map[self.tune["btype"]]
        analog = bool(self.tune["analog"])

        nyquist = 0.5 * len(data)  # Nyquist frequency
        normal_cutoff = (
            self.tune["cutoff_frequency"] / nyquist
        )  # Normalized cutoff frequency
        b, a = butter(
            self.tune["low_pass_order"], normal_cutoff, btype=btype, analog=analog
        )
        if nyquist <= 1:
            return np.abs(data)
        else:
            return filtfilt(
                b, a, np.abs(data)
            )  # Apply the filter to the absolute value of FFT data

    def plot(self, *args):
        """
        Plot various indicators for analysis, including MACD, RSI, FFT, and ADX.
        """
        qx.plot(
            *args,
            (
                ("macd_line", "MACD Line", "blue", 0, "BBadXMacDrSi"),
                ("macd_signal", "MACD Signal", "orange", 0, "BBadXMacDrSi"),
                ("rsi", "RSI", "green", 0, "BBadXMacDrSi"),
                ("fft_filtered", "FFT Filtered", "purple", 0, "BBadXMacDrSi"),
                ("adx", "ADX", "red", 0, "BBadXMacDrSi"),
            )
        )

    def strategy(self, state, indicators):
        """
        The main strategy logic for handling buy/sell actions based on technical indicators and conditions.
        """
        macd_line = indicators["macd_line"]
        macd_signal = indicators["macd_signal"]
        rsi = indicators["rsi"]
        fft_filtered = indicators["fft_filtered"]
        adx = indicators["adx"]

        current_time = state["unix"]

        # Detect market regime (Trend vs Range)
        if adx < self.tune["adx_threshold"]:
            market_regime = "range"  # Market is range-bound, typically no strong trends
        else:
            market_regime = (
                "trend"  # Market is trending, look for strong price movements
            )

        # Buy conditions with dynamic comparison operators
        if (
            self.tune["macd_comparison"] * (macd_line - macd_signal) > 0
            and self.tune["rsi_comparison"]
            * (rsi - self.tune["rsi_zscore_buy_threshold"])
            > 0
            and self.tune["fft_comparison"]
            * (fft_filtered - self.tune["fft_filtered_buy"])
            > 0
        ):
            # Ensure we don't already have a position before buying
            if state["last_trade"] is None or isinstance(state["last_trade"], qx.Sell):
                self.storage["last_trade_time"] = current_time
                self.storage["trade_price"] = state["close"]
                return qx.Buy()  # Execute Buy action

        # Sell conditions with dynamic comparison operators
        elif (
            self.tune["macd_comparison"] * (macd_line - macd_signal) < 0
            and self.tune["rsi_comparison"]
            * (rsi - self.tune["rsi_zscore_sell_threshold"])
            < 0
            and self.tune["fft_comparison"]
            * (fft_filtered - self.tune["fft_filtered_sell"])
            < 0
        ):
            # Ensure we don't already have a position before selling
            if state["last_trade"] is None or isinstance(state["last_trade"], qx.Buy):
                self.storage["last_trade_time"] = current_time
                self.storage["trade_price"] = state["close"]
                return qx.Sell()  # Execute Sell action

        # If no conditions are met, do nothing (no action taken)
        return None

    def fitness(self, states, raw_states, asset, currency):
        """
        Returns the fitness criteria for strategy optimization (e.g., ROI, Sortino ratio, win rate).
        """
        return [
            "roi_gross",  # Gross Return on Investment
            "sortino_ratio",  # Risk-adjusted return (Sortino ratio)
            "trade_win_rate",  # Percentage of profitable trades
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

    bot = BBadXMacDrSi()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
