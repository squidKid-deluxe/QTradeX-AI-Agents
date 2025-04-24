from typing import Dict, Tuple

import numpy as np
import qtradex as qx

# Assuming the KST and FRAMA functions are defined as provided

TEST = 7


TESTS = {
    1: (
        ("eri_bull", "Elder Ray Index (ERI) Bull", "lime", 1, ""),
        ("eri_bear", "Elder Ray Index (ERI) Bear", "tomato", 1, ""),
        ("tsi", "Trend Strength Indicator (TSI)", "teal", 2, ""),
        ("smi", "Stochastic Momentum Index (SMI)", "cyan", 2, ""),
        ("smi_sig", "Stochastic Momentum Signal", "blue", 2, ""),
        (
            "macd",
            "Typed Moving Average Convergence Divergence (MACD)",
            "deepskyblue",
            3,
            "",
        ),
        ("signal_line", "Typed MACD Signal", "white", 3, ""),
        ("hist", "Typed MACD Histogram", "aqua", 3, "MACD"),
    ),
    2: (
        ("ha_close", "Heikin-Ashi Close", "pink", 1, ""),
        ("ha_open", "Heikin-Ashi Open", "deepskyblue", 1, ""),
        ("tenkan_sen", "Ichimoku Tenkan Sen", "yellow", 0, ""),
        ("kijun_sen", "Ichimoku Kijun Sen", "orange", 0, ""),
        ("senkou_span_a", "Ichimoku Senkou Span A", "lime", 0, ""),
        ("senkou_span_b", "Ichimoku Senkou Span B", "lime", 0, ""),
        ("chikou_span", "Ichimoku Chikou Span", "red", 0, ""),
    ),
    3: (
        ("frama1", "Fractal Adaptive Moving Average (FRAMA) 1", "yellow", 0, ""),
        ("frama2", "Fractal Adaptive Moving Average (FRAMA) 2", "orange", 0, ""),
        ("super_t", "Super Trend Reversal", "deepskyblue", 0, ""),
        ("kst", "Know Sure Thing (KST)", "lime", 1, "KST"),
        ("kst_signal", "Know Sure Thing (KST) Signal", "tomato", 1, "KST"),
        ("ravi", "Range Action Verification Index (RAVI)", "magenta", 2, "ravi"),
    ),
    4: (
        ("k_upper_band", "Keltner Upper Band", "lightblue", 0, ""),
        ("k_middle_band", "Keltner Middle Band", "lightgreen", 0, ""),
        ("k_lower_band", "Keltner Lower Band", "lightpink", 0, ""),
        ("d_upper_band", "Donchian Upper Band", "salmon", 0, ""),
        ("d_middle_band", "Donchian Middle Band", "peachpuff", 0, ""),
        ("d_lower_band", "Donchian Lower Band", "khaki", 0, ""),
    ),
    5: (
        ("tick_i", "Tick Indicator", "gold", 4, ""),
        ("volume_profile", "Volume Profile", "lightcoral", 3, ""),
        ("trin_i", "TRIN Indicator", "orchid", 5, ""),
        ("vortex_plus", "Vortex Plus", "darkviolet", 2, ""),
        ("vortex_minus", "Vortex Minus", "mediumseagreen", 2, ""),
    ),
    6: (
        ("holt_smooth", "Holt-Winters Smooth", "purple", 0, ""),
        ("holt_trend", "Holt-Winters Trend", "orange", 1, ""),
        ("trix_values", "% Rate of Change of Triple EMA (Trix)", "blue", 2, ""),
        ("ulcer_index_values", "Ulcer Index", "red", 3, ""),
    ),
    # 7: (
    #     ("a_support", "Price Action Support", "lightseagreen", 0, ""), # seems lagging / broken
    #     ("a_resistance", "Price Action Resistance", "lightsalmon", 0, ""), # seems lagging / broken
    # ),
    # 8: (
    #     ("zigzag", "Zig Zag", "slateblue", 0, ""),
    #     ("steps", "Zig Zag Pivot Points", "goldenrod", 0, ""),
    # The following entries are commented out as per the original data
    # ("arsi", "Adaptive RSI", "coral", 2, ""), # empty array
    # ("kagi", "Kagi", "plum", 0, ""), # empty array
    # ("renko", "Renko", "lavender", 0, ""), # empty array
    # ("ehlers_arsi", "Ehlers Adaptive RSI", "white", 0, ""), # empty array
    # ("price_bins", "Price Bins", "lightgray", 0, ""), # plots a log curve? not legit.
    # ("aema", "Adaptive Exponential Moving Average (AEMA)", "magenta", 2, ""), # plots an oscillator? not legit.
    # ),
}


class QiIndicatorsTest(qx.BaseBot):
    def __init__(self):
        self.tune = {
            "sell_thresh": 2.0,
            "buy_thresh": 2.0,
            "ichimoku_tenkan_period": 9.0,
            "ichimoku_kijun_period": 26.0,
            "ichimoku_senkou_b_period": 52.0,
            "ichimoku_senkou_span": 26.0,
            "kst_roc1_period": 10.0,
            "kst_roc2_period": 15.0,
            "kst_roc3_period": 20.0,
            "kst_roc4_period": 30.0,
            "kst_smoothing": 3.0,
            "frama1_period": 14.0,
            "frama1_fractal_period": 2.0,
            "frama2_period": 28.0,
            "frama2_fractal_period": 4.0,
            "ravi_short": 10.0,
            "ravi_long": 20.0,
            "aema_period": 50.0,
            "aema_alpha": 0.1,
            "macd_short_period": 12.0,
            "macd_long_period": 26.0,
            "macd_signal_period": 9.0,
            "macd_type": 1,
            "tsi_long_period": 50.0,
            "tsi_short_period": 20.0,
            "k_period": 14.0,
            "d_period": 3.0,
            "eri_ma_period": 50.0,
            "eri_ma_type": 2,
            "atr_period": 14.0,
            "atr_multiplier": 1.5,
            "keltner_atr_period": 14.0,
            "keltner_ma_period": 14.0,
            "keltner_ma_type": 2,
            "keltner_multiplier": 2.0,
            "donchian_period": 20.0,
            "mp_bin_size": 100.0,
            "pa_lookback": 10.0,
            "pa_threshold": 0.1,
            "tbb_ma_period": 20.0,
            "tbb_ma_type": 2,
            "tbb_std_period": 20.0,
            "tbb_deviations": 1.0,
            "arsi_rsi_period": 14.0,
            "kagi_reversal": 0.02,
            "renko_brick": 0.5,
            "vortex_period": 14.0,
            "zigzag_deviation": 0.010,
            "holt_winters_span": 10,
            "holt_winters_beta": 0.2,
            "ulcer_index_window": 14,
            "trix_window": 15,
            "earsi_auto_min": 10.0,
            "earsi_auto_max": 15.0,
            "earsi_auto_avg": 50.0,
        }

        self.clamps = {
            "sell_thresh": [0, 5, 100, 1],
            "buy_thresh": [0, 5, 100, 1],
            "ichimoku_tenkan_period": [1, 9, 30, 1],
            "ichimoku_kijun_period": [1, 26, 50, 1],
            "ichimoku_senkou_b_period": [1, 52, 100, 1],
            "ichimoku_senkou_span": [1, 26, 100, 1],
            "kst_roc1_period": [1, 10, 30, 1],
            "kst_roc2_period": [1, 15, 30, 1],
            "kst_roc3_period": [1, 20, 30, 1],
            "kst_roc4_period": [1, 30, 50, 1],
            "kst_smoothing": [1, 3, 20, 1],
            "frama1_period": [1, 14, 30, 1],
            "frama1_fractal_period": [1, 2, 5, 1],
            "frama2_period": [1, 28, 30, 1],
            "frama2_fractal_period": [1, 4, 5, 1],
            "ravi_short": [1, 10, 100, 1],
            "ravi_long": [1, 20, 100, 1],
            "aema_period": [1, 50.0, 100, 1],
            "aema_alpha": [0, 0.1, 1, 1],
            "macd_short_period": [1, 12.0, 100, 1],
            "macd_long_period": [1, 26.0, 100, 1],
            "macd_signal_period": [1, 9.0, 100, 1],
            "macd_type": [1, 1, 12, 1],
            "tsi_long_period": [1, 50.0, 100, 1],
            "tsi_short_period": [1, 20.0, 100, 1],
            "k_period": [1, 14.0, 100, 1],
            "d_period": [1, 3.0, 100, 1],
            "eri_ma_period": [1, 50.0, 100, 1],
            "eri_ma_type": [1, 2, 8, 1],
            "atr_period": [1, 14, 100, 1],
            "atr_multiplier": [0, 1.5, 10, 1],
            "keltner_atr_period": [1.0, 14.0, 30.0, 1],
            "keltner_ma_period": [1.0, 14.0, 30.0, 1],
            "keltner_ma_type": [1, 2, 8, 1],
            "keltner_multiplier": [1.0, 2.0, 10.0, 1],
            "donchian_period": [1.0, 20.0, 30.0, 1],
            "mp_bin_size": [1.0, 10.0, 30.0, 1],
            "pa_lookback": [1.0, 100.0, 30.0, 1],
            "pa_threshold": [0.0, 0.1, 30.0, 1],
            "tbb_ma_period": [1.0, 20.0, 30.0, 1],
            "tbb_ma_type": [1, 2, 8, 1],
            "tbb_std_period": [1.0, 20.0, 30.0, 1],
            "tbb_deviations": [0.0, 1.0, 30.0, 1],
            "arsi_rsi_period": [1.0, 14.0, 30.0, 1],
            "kagi_reversal": [0.0, 0.02, 30.0, 1],
            "renko_brick": [0.1, 0.5, 30.0, 1],
            "vortex_period": [1.0, 14.0, 30.0, 1],
            "zigzag_deviation": [0.1, 1.0, 30.0, 1],
            "holt_winters_span": [1, 10, 100, 1],
            "holt_winters_beta": [0.01, 0.5, 0.99, 1],
            "ulcer_index_window": [1, 14, 100, 1],
            "trix_window": [1, 15, 100, 1],
            "earsi_auto_min": [1.0, 10.0, 100.0, 1],
            "earsi_auto_max": [1.0, 15.0, 100.0, 1],
            "earsi_auto_avg": [1.0, 50.0, 100.0, 1],
        }

    def indicators(self, data):
        ha_values = qx.qi.heikin_ashi(
            dict(
                {
                    "open": data["open"],
                    "high": data["high"],
                    "low": data["low"],
                    "close": data["close"],
                    "volume": data["volume"],  # Volume remains the same
                }
            )
        )
        ichimoku_values = qx.qi.ichimoku(
            data["high"],
            data["low"],
            data["close"],
            self.tune["ichimoku_tenkan_period"],
            self.tune["ichimoku_kijun_period"],
            self.tune["ichimoku_senkou_b_period"],
            self.tune["ichimoku_senkou_span"],
        )
        kst_values = qx.qi.kst(
            data["close"],
            self.tune["kst_roc1_period"],
            self.tune["kst_roc2_period"],
            self.tune["kst_roc3_period"],
            self.tune["kst_roc4_period"],
            self.tune["kst_smoothing"],
        )
        frama1 = qx.qi.frama(
            data["close"],
            self.tune["frama1_period"],
            self.tune["frama1_fractal_period"],
        )
        frama2 = qx.qi.frama(
            data["close"],
            self.tune["frama2_period"],
            self.tune["frama2_fractal_period"],
        )
        ravi = qx.qi.ravi(
            data["high"],
            data["low"],
            data["close"],
            self.tune["ravi_short"],
            self.tune["ravi_long"],
        )
        aema = qx.derivative(
            qx.qi.aema(data["close"], self.tune["aema_period"], self.tune["aema_alpha"])
        )
        macd, signal_line, hist = qx.qi.typed_macd(
            data["close"],
            self.tune["macd_short_period"],
            self.tune["macd_long_period"],
            self.tune["macd_signal_period"],
            self.tune["macd_type"],
        )
        tsi = qx.qi.tsi(
            data["close"], self.tune["tsi_long_period"], self.tune["tsi_short_period"]
        )
        smi, smi_sig = qx.qi.smi(
            data["close"],
            data["high"],
            data["low"],
            self.tune["k_period"],
            self.tune["d_period"],
        )
        eri_bull, eri_bear = qx.qi.eri(
            data["high"],
            data["low"],
            data["close"],
            self.tune["eri_ma_period"],
            self.tune["eri_ma_type"],
        )
        super_t, upt, dt = qx.qi.super_trend(
            data["high"],
            data["low"],
            data["close"],
            self.tune["atr_period"],
            self.tune["atr_multiplier"],
        )

        k_upper_band, k_middle_band, k_lower_band = qx.qi.keltner(
            data["high"],
            data["low"],
            data["close"],
            self.tune["keltner_atr_period"],
            self.tune["keltner_ma_period"],
            self.tune["keltner_ma_type"],
            self.tune["keltner_multiplier"],
        )
        d_upper_band, d_middle_band, d_lower_band = qx.qi.donchian(
            data["high"], data["low"], self.tune["donchian_period"]
        )
        tick_i = qx.qi.tick_indicator(data["close"])
        price_bins, volume_profile = qx.qi.market_profile(
            data["close"], data["volume"], self.tune["mp_bin_size"]
        )
        a_support, a_resistance = qx.qi.price_action(
            data["close"], self.tune["pa_lookback"], self.tune["pa_threshold"]
        )
        tbb_upper_band, tbb_middle_bband, tbb_lower_band = qx.qi.typed_bbands(
            data["close"],
            self.tune["tbb_ma_period"],
            self.tune["tbb_ma_type"],
            self.tune["tbb_std_period"],
            self.tune["tbb_deviations"],
        )
        trin_i = qx.qi.trin_indicator(data["close"], data["volume"])

        vortex_plus, vortex_minus, vortex = qx.qi.vortex(
            data["high"], data["low"], data["close"], self.tune["vortex_period"]
        )
        zigzag, steps = qx.qi.zigzag(data["close"], self.tune["zigzag_deviation"])
        holt_smooth, holt_trend = qx.qi.holt_winters_des(
            data["close"],
            self.tune["holt_winters_span"],
            self.tune["holt_winters_beta"],
        )
        trix_values = qx.qi.trix(data["close"], self.tune["trix_window"])
        ulcer_index_values = qx.qi.ulcer_index(
            data["close"], self.tune["ulcer_index_window"]
        )
        arsi = qx.qi.arsi(
            data["close"],
            self.tune["arsi_rsi_period"],
        )
        kagi = qx.qi.kagi(data["close"], self.tune["kagi_reversal"])
        renko = qx.qi.renko(data["close"], self.tune["renko_brick"])
        ehlers_arsi = qx.qi.earsi(
            data["close"],
            self.tune["earsi_auto_min"],
            self.tune["earsi_auto_max"],
            self.tune["earsi_auto_avg"],
        )

        return {
            "random": np.random.randint(-5, 5, data["close"].shape[0]),
            "ha_close": ha_values["ha_close"],
            "ha_open": ha_values["ha_open"],
            "tenkan_sen": ichimoku_values[0],
            "kijun_sen": ichimoku_values[1],
            "senkou_span_a": ichimoku_values[2],
            "senkou_span_b": ichimoku_values[3],
            "chikou_span": ichimoku_values[4],
            "kst": kst_values[0],
            "kst_signal": kst_values[1],
            "frama1": frama1,
            "frama2": frama2,
            "ravi": ravi,
            "aema": aema,
            "macd": macd,
            "signal_line": signal_line,
            "hist": hist,
            "tsi": tsi,
            "smi": smi,
            "smi_sig": smi_sig,
            "eri_bull": eri_bull,
            "eri_bear": eri_bear,
            "super_t": super_t,
            "k_upper_band": k_upper_band,
            "k_middle_band": k_middle_band,
            "k_lower_band": k_lower_band,
            "d_upper_band": d_upper_band,
            "d_middle_band": d_middle_band,
            "d_lower_band": d_lower_band,
            "tick_i": tick_i,
            "price_bins": price_bins,
            "volume_profile": volume_profile,
            "a_support": a_support,
            "a_resistance": a_resistance,
            "trin_i": trin_i,
            "vortex_plus": vortex_plus,
            "vortex_minus": vortex_minus,
            "vortex": vortex,
            "zigzag": zigzag,
            "steps": steps,
            "holt_smooth": holt_smooth,
            "holt_trend": holt_trend,
            "trix_values": trix_values,
            "ulcer_index_values": ulcer_index_values,
            # "arsi": arsi,
            # "kagi": kagi,
            # "renko": renko,
            # "ehlers_arsi": ehlers_arsi,
        }

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            TESTS[TEST],
        )

    def strategy(self, state, indicators):
        # Random Strategy Logic
        if indicators["random"] < -4:
            return qx.Sell()
        elif indicators["random"] > 4:
            return qx.Buy()

    def fitness(self, states, raw_states, asset, currency):
        return [
            "roi_assets",
            "roi_currency",
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

    bot = QiIndicatorsTest()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
