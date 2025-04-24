from typing import Dict, Tuple

import numpy as np
import qtradex as qx

# Assuming the KST and FRAMA functions are defined as provided


class HeikinAshiIchimokuVortexBot(qx.BaseBot):
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
            "kst_smoothing": 9.0,
            "frama1_period": 14.0,
            "frama1_fractal_period": 2.0,
            "frama2_period": 25.0,
            "frama2_fractal_period": 2.0,
            "ravi_short": 10.0,
            "ravi_long": 50.0,
            "aema_period": 10.0,
            "aema_alpha": 0.1,
            "macd_short_period": 10.0,
            "macd_long_period": 50.0,
            "macd_signal_period": 25.0,
            "macd_type": 1,
            "tsi_long_period": 50.0,
            "tsi_short_period": 10.0,
            "k_period": 50.0,
            "d_period": 10.0,
            "eri_ma_period": 50.0,
            "eri_ma_type": 2,
            "atr_period": 15.0,
            "atr_multiplier": 3.0,
            # "arsi_rsi_period": 15.0,
            # "arsi_adpative_period": 15.0,
            # "keltner_atr_period": 15.0,
            # "keltner_ma_period": 15.0,
            # "keltner_ma_type": 2,
            # "keltner_multiplier": 15.0,
            # "donchian_period": 15.0,
            # "kagi_reversal": 15.0,
            # "renko_brick": 15.0,
            # "mp_bin_size": 15.0,
            # "pa_lookback": 15.0,
            # "pa_threshold": 15.0,
            # "tbb_ma_period": 15.0,
            # "tbb_ma_type": 2,
            # "tbb_std_period": 15.0,
            # "tbb_deviations":15.0,
            # "vortex_period":  15.0,
            # "zigzag_deviation": 15.0
        }
        # Optimizer clamps (min, initial, max, strength)
        self.clamps = {
            "sell_thresh": [1, 5, 100, 1],
            "buy_thresh": [1, 5, 100, 1],
            "ichimoku_tenkan_period": [5, 9, 30, 1],
            "ichimoku_kijun_period": [5, 26, 50, 1],
            "ichimoku_senkou_b_period": [5, 52, 100, 1],
            "ichimoku_senkou_span": [5, 26, 100, 1],
            "kst_roc1_period": [5, 10, 30, 1],
            "kst_roc2_period": [5, 15, 30, 1],
            "kst_roc3_period": [5, 20, 30, 1],
            "kst_roc4_period": [5, 30, 50, 1],
            "kst_smoothing": [1, 9, 20, 1],
            "frama1_period": [5, 14, 30, 1],
            "frama1_fractal_period": [1, 2, 5, 1],
            "frama2_period": [5, 14, 30, 1],
            "frama2_fractal_period": [1, 2, 5, 1],
            "ravi_short": [5, 10, 100, 1],
            "ravi_long": [5, 10, 100, 1],
            "aema_period": [10, 50.0, 100, 1],
            "aema_alpha": [0, 0.1, 100, 1],
            "macd_short_period": [5, 10.0, 100, 1],
            "macd_long_period": [5, 50.0, 100, 1],
            "macd_signal_period": [5, 25.0, 100, 1],
            "macd_type": [1, 1, 12, 1],
            "tsi_long_period": [5, 50.0, 100, 1],
            "tsi_short_period": [5, 20.0, 100, 1],
            "k_period": [5, 30.0, 100, 1],
            "d_period": [5, 20.0, 100, 1],
            "eri_ma_period": [5, 50.0, 100, 1],
            "eri_ma_type": [1, 2, 8, 1],
            "atr_period": [5, 10, 100, 1],
            "atr_multiplier": [0, 0.1, 100, 1],
            # "arsi_rsi_period": [1.0, 15.0, 30.0, 1],
            # "arsi_adpative_period": [1.0, 15.0, 30.0, 1],
            # "keltner_atr_period": [1.0, 15.0, 30.0, 1],
            # "keltner_ma_period": [1.0, 15.0, 30.0, 1],
            # "keltner_ma_type": [1, 2, 8, 1],
            # "keltner_multiplier": [1.0, 15.0, 30.0, 1],
            # "donchian_period": [1.0, 15.0, 30.0, 1],
            # "kagi_reversal": [1.0, 15.0, 30.0, 1],
            # "renko_brick": [1.0, 15.0, 30.0, 1],
            # "mp_bin_size": [1.0, 15.0, 30.0, 1],
            # "pa_lookback": [1.0, 15.0, 30.0, 1],
            # "pa_threshold": [1.0, 15.0, 30.0, 1],
            # "tbb_ma_period":  [1.0, 15.0, 30.0, 1],
            # "tbb_ma_type":  [1, 2, 8, 1],
            # "tbb_std_period":  [1.0, 15.0, 30.0, 1],
            # "tbb_deviations": [1.0, 15.0, 30.0, 1],
            # "vortex_period":  [1.0, 15.0, 30.0, 1],
            # "zigzag_deviation": [1.0, 15.0, 30.0, 1],
        }

    def indicators(self, data):
        # Calculate Heikin-Ashi
        ha_values = qx.qi.heikin_ashi(data)

        # Calculate Ichimoku
        ichimoku_values = qx.qi.ichimoku(
            data["high"],
            data["low"],
            data["close"],
            self.tune["ichimoku_tenkan_period"],
            self.tune["ichimoku_kijun_period"],
            self.tune["ichimoku_senkou_b_period"],
            self.tune["ichimoku_senkou_span"],
        )

        # Calculate KST
        kst_values = qx.qi.kst(
            data["close"],
            self.tune["kst_roc1_period"],
            self.tune["kst_roc2_period"],
            self.tune["kst_roc3_period"],
            self.tune["kst_roc4_period"],
            self.tune["kst_smoothing"],
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

        # arsi = qx.qi.arsi(
        #     data["close"], self.tune["arsi_rsi_period"], self.tune["arsi_adpative_period"]
        # )
        # k_upper_band, k_middle_band, k_lower_band = qx.qi.keltner(
        #     data["high"],
        #     data["low"],
        #     data["close"],
        #     self.tune["keltner_atr_period"],
        #     self.tune["keltner_ma_period"],
        #     self.tune["keltner_ma_type"],
        #     self.tune["keltner_multiplier"],
        # )
        # d_upper_band, d_middle_band, d_lower_band = qx.qi.donchian(
        #     data["high"], data["low"], self.tune["donchian_period"]
        # )
        # kagi = qx.qi.kagi(data["close"], self.tune["kagi_reversal"])
        # renko = qx.qi.renko(data["close"], self.tune["renko_brick"])
        # tick_i = qx.qi.tick_indicator(data["close"])
        # trin_i = qx.qi.trin_indicator(data["close"], data["volume"])
        # price_bins, volume_profile = qx.qi.market_profile(
        #     data["close"], volume, self.tune["mp_bin_size"]
        # )
        # a_support, a_resistance = qx.qi.price_action(
        #     data["close"], self.tune["pa_lookback"], self.tune["pa_threshold"]
        # )
        # tbb_upper_band, tbb_middle_bband, tbb_lower_band = typed_bbands(
        # data["close"],
        # self.tune["tbb_ma_period"],
        # self.tune["tbb_ma_type"],
        # self.tune["tbb_std_period"],
        # self.tune["tbb_deviations"]
        # )
        # vortex_plus, vortex_minus, vortex = vortex(
        #     data["high"], data["low"], data["close"], self.tune["vortex_period"]
        # )
        # zigzag, steps = zigzag(data["close"], self.tune["deviation"])

        return {
            "ha_close": ha_values["ha_close"],
            "ha_open": ha_values["ha_open"],
            "tenkan_sen": ichimoku_values[0],
            "kijun_sen": ichimoku_values[1],
            "kst": kst_values[0],
            "kst_signal": kst_values[1],
            "frama1": qx.qi.frama(
                data["close"],
                self.tune["frama1_period"],
                self.tune["frama1_fractal_period"],
            ),
            "frama2": qx.qi.frama(
                data["close"],
                self.tune["frama2_period"],
                self.tune["frama2_fractal_period"],
            ),
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
            # "arsi": arsi,
            # "k_upper_band": k_upper_band,
            # "k_middle_band": k_middle_band,
            # "k_lower_band": k_lower_band,
            # "d_upper_band": d_upper_band,
            # "d_middle_band": d_middle_band,
            # "d_lower_band": d_lower_band,
            # "kagi": kagi,
            # "renko": renko,
            # "tick_i": tick_i,
            # "trin_i": trin_i,
            # "price_bins": price_bins,
            # "volume_profile": volume_profile,
            # "a_support": a_support,
            # "a_resistance": a_resistance
            # "vortex_plus": vortex_plus,
            # "vortex_minus": vortex_minus,
            # "vortex": vortex,
            # "zigzag": zigzag,
            # "steps": steps,
        }

    def plot(self, *args):
        qx.plot(
            self.info,
            *args,
            (
                ("eri_bull", "eri_bull", "lime", 3, ""),
                ("eri_bear", "eri_bear", "tomato", 3, ""),
                ("tsi", "TSI", "teal", 2, ""),
                ("smi", "SMI", "cyan", 2, ""),
                ("smi_sig", "SMI Signal", "blue", 2, ""),
                ("macd", "MACD", "deepskyblue", 3, ""),
                ("signal_line", "signal line", "white", 3, ""),
                ("hist", "hist", "aqua", 3, "MACD"),
                ("aema", "AEMA", "magenta", 1, ""),
                ("ha_close", "Heikin-Ashi Close", "green", 0, "Confluence"),
                ("ha_open", "Heikin-Ashi Open", "red", 0, "Confluence"),
                ("tenkan_sen", "Tenkan-sen", "blue", 0, "Confluence"),
                ("kijun_sen", "Kijun-sen", "orange", 0, "Confluence"),
                ("frama1", "FRAMA 1", "yellow", 0, "Confluence"),
                ("frama2", "FRAMA 2", "green", 0, "Confluence"),
                ("kst", "KST", "purple", 1, "KST"),
                ("kst_signal", "KST Signal", "brown", 1, "KST"),
                ("ravi", "Ravi", "magenta", 2, "ravi"),
                ("super_t", "Super Trend", "yellow", 0, ""),
                # ("arsi", "Arsi", "coral", 2, ""),
                # ("k_upper_band", "K Upper Band", "lightblue", 2, ""),
                # ("k_middle_band", "K Middle Band", "lightgreen", 2, ""),
                # ("k_lower_band", "K Lower Band", "lightpink", 2, ""),
                # ("d_upper_band", "D Upper Band", "salmon", 2, ""),
                # ("d_middle_band", "D Middle Band", "peachpuff", 2, ""),
                # ("d_lower_band", "D Lower Band", "khaki", 2, ""),
                # ("kagi", "Kagi", "plum", 2, ""),
                # ("renko", "Renko", "lavender", 2, ""),
                # ("tick_i", "Tick Indicator", "gold", 2, ""),
                # ("trin_i", "TRIN Indicator", "orchid", 2, ""),
                # ("price_bins", "Price Bins", "lightgray", 2, ""),
                # ("volume_profile", "Volume Profile", "lightcoral", 2, ""),
                # ("a_support", "A Support", "lightseagreen", 2, ""),
                # ("a_resistance", "A Resistance", "lightsalmon", 2, ""),
                # ("vortex_plus", "Vortex Plus", "darkviolet", 2, ""),
                # ("vortex_minus", "Vortex Minus", "mediumseagreen", 2, ""),
                # ("vortex", "Vortex", "tomato", 2, ""),
                # ("zigzag", "Zigzag", "slateblue", 2, ""),
                # ("steps", "Steps", "goldenrod", 2, ""),
            ),
        )

    def strategy(self, state, indicators):
        # Basic strategy logic
        if state["last_trade"] is None:
            return qx.Buy()

        conditions = [
            indicators["ha_close"] > indicators["ha_open"],
            indicators["tenkan_sen"] > indicators["kijun_sen"],
            indicators["kst"] > indicators["kst_signal"],
            indicators["frama1"] < indicators["frama2"],
            indicators["ravi"] > 0,
            indicators["aema"] > 0,
            indicators["hist"] > indicators["macd"],
            indicators["tsi"] > 0,
            indicators["smi"] > indicators["smi_sig"],
        ]

        bearish = sum([int(i) for i in conditions])
        bullish = sum([int(not i) for i in conditions])

        # Buy signal conditions
        if bearish > self.tune["sell_thresh"]:
            return qx.Sell()

        # Sell signal conditions
        if bullish > self.tune["buy_thresh"]:
            return qx.Buy()

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

    bot = HeikinAshiIchimokuVortexBot()
    qx.dispatch(bot, data, wallet)


if __name__ == "__main__":
    main()
