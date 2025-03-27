# QTradeX AI Agents

## Algo Trading Strategies

This repository contains a collection of algorithmic trading strategies implemented in Python, designed for use with the [QTradeX](https://github.com/squidKid-deluxe/QTradeX-Algo-Trading-SDK) platform. Each strategy leverages technical indicators to generate buy and sell signals for trading assets. Below is a brief description of each strategy.

---

## Strategies

Please note that some of these strategies are a work in progress.  Known good strategies are:

 - `cthulu.py`
 - `extinction_event.py`
 - `iching.py`
 - `forty96.py`
 - `harmonica.py`
 - `ma_sabres.py`
 - `parabolic_ten.py`

*Others may not work or backtest profitably.*

### 1. `aroon.py`
- **Indicators**: Uses the **Aroon Oscillator**, a momentum indicator that measures trend strength based on high and low prices over a specified period (`aroon_period`). It ranges from -100 to +100.
- **Strategy**: Triggers buy signals when the Aroon Oscillator crosses above a `buy_thresh` (indicating an uptrend) and sell signals when it crosses below a `sell_thresh` (indicating a downtrend).

---

### 2. `aroon_mfi_vwap.py`
- **Indicators**: Combines **Short EMA**, **Aroon Indicator**, **Money Flow Index (MFI)**, and **Volume Weighted Average Price (VWAP)**.
- **Strategy**: Generates a buy signal when the difference between `aroon_up` and `aroon_down` exceeds a threshold (`aroon_buy`) and the `short_ema` is below the `vwap` (suggesting an oversold condition).

---

### 3. `blackhole.py`
- **Indicators**: Includes **ATR (Average True Range)**, **SMA (Simple Moving Average)**, volatility surge detection, dynamic support/resistance levels, momentum signals, and a unique "blackhole zone" for price compression.
- **Strategy**: Detects extreme market conditions (e.g., volatility surges) and uses dynamic support/resistance levels to set buy zones for entering positions.

---

### 4. `classic_crypto_bot.py`
- **Indicators**: Features **SMA**, **EMA**, **RSI**, **Stochastic Oscillator**, and **ADX (Average Directional Index)** with customizable periods.
- **Strategy**: Combines multiple indicators with thresholds (`buy_threshold`, `sell_threshold`) to confirm buy/sell signals based on trend and momentum.

---

### 5. `confluence.py`
- **Indicators**: Uses **Short-term EMA**, **Long-term EMA**, **RSI**, **MACD**, and **Bollinger Bands**.
- **Strategy**: Seeks confluence across multiple indicators to identify high-probability trades, leveraging trend and momentum signals.

---

### 6. `cryptomasterbot.py`
- **Indicators**: Combines **SMA**, **EMA**, **RSI**, **MACD**, **Bollinger Bands**, **Fisher Transform**, and **Stochastic Oscillator**.
- **Strategy**: A multi-indicator approach that uses MACD crossovers, RSI overbought/oversold levels, and Stochastic signals for trade execution.

---

### 7. `cthulhu.py`
- **Indicators**: Features a 14-period **EMA**, **Standard Deviation**, and dynamic upper/lower channels around the EMA.
- **Strategy**: Tracks trends with EMA and uses volatility-based channels to identify breakout or reversal points.

---

### 8. `directional_movement.py`
- **Indicators**: Includes **Short-, Mid-, and Long-term EMAs**, **DMI (Directional Movement Indicators)**, **ADX**, and **ADXR**.
- **Strategy**: Uses ADX to measure trend strength and DMI to determine direction, supplemented by EMA crossovers.

---

### 9. `ema_cross.py`
- **Indicators**: Relies on two **EMAs** (short-term and long-term) calculated with closing prices.
- **Strategy**: Triggers trades based on crossovers between the fast and slow EMAs, signaling trend changes.

---

### 10. `extinction_event.py`
- **Indicators**: Features multiple **EMAs**, dynamic **support**, **resistance**, **selloff**, and **despair** levels, plus trend detection.
- **Strategy**: Adjusts buy/sell prices based on market trends (‘bull’, ‘bear’, or neutral) and overrides default behavior during trend shifts.

---

### 11. `forty96.py`
- **Indicators**: Calculates **EMA values and slopes** to form a "hexagram" (12-dimensional dictionary) representing market conditions.
- **Strategy**: Uses the hexagram's binary string to determine buy, sell, or no-action decisions.

---

### 12. `fosc_uo_msw.py`
- **Indicators**: Combines **Ultimate Oscillator (UO)**, **Forecast Oscillator (FOSC)**, and **Mesa Sine Wave (MSW)**.
- **Strategy**: Requires a threshold number of aligned signals (`buy_threshold`, `sell_threshold`) for trade execution.

---

### 13. `harmonica.py`
- **Indicators**: Uses six **Parabolic SAR** values with varying sensitivity and four **EMAs** (10, 60, 90 periods).
- **Strategy**: Detects trend reversals with SAR and confirms direction with EMAs.

---

### 14. `iching.py`
- **Indicators**: Calculates **EMA slopes** to form a 6-dimensional "hexagram" (binary array).
- **Strategy**: Converts the hexagram into a binary string to lookup buy/sell actions in a tuning dictionary.

---

### 15. `lava_hkbot.py`
- **Indicators**: Features two **EMAs** (fast and slow) and an **OHLC4** (average of open, high, low, close prices).
- **Strategy**: Determines market mode (bullish, bearish, or neutral) by comparing start and close prices, guided by EMA trends.

---

### 16. `ma_sabres.py`
- **Indicators**: Uses five configurable **Moving Averages** (EMA, SMA, HMA) and their slopes for trend detection.
- **Strategy**: Generates dynamic buy/sell signals based on slope alignment and bullish/bearish thresholds.

---

### 17. `mac_dr_si.py`
- **Indicators**: Combines **MACD**, **RSI**, **ADX**, and **Fourier Transform (FFT)** with a low-pass filter.
- **Strategy**: Uses MACD crossovers, RSI levels, and ADX trend strength for buy/sell decisions, filtering noise with FFT.

---

### 18. `masterbot.py`
- **Indicators**: Features **MACD**, **RSI**, **Stochastic Oscillator**, and **ATR**.
- **Strategy**: Confirms entries with RSI and Stochastic, using MACD for trend direction and ATR for volatility.

---

### 19. `parabolic_ten.py`
- **Indicators**: Identical to `harmonica.py` with six **Parabolic SAR** values and four **EMAs**.
- **Strategy**: Tracks trends with SAR and confirms with EMA directionality.

---

### 20. `renko.py`
- **Indicators**: Uses **Renko Bars** (fixed price movement) and **RSI**.
- **Strategy**: Triggers buy signals when Renko shows an uptrend and RSI is oversold; sell signals when Renko shows a downtrend and RSI is overbought.

---

### 21. `tradfibot.py`
- **Indicators**: Includes **SMA**, **EMA**, **RSI**, **MACD**, **Bollinger Bands**, and **Stochastic Oscillator**.
- **Strategy**: A traditional finance-inspired approach combining trend, momentum, and volatility indicators.

---

### 22. `trima_zlema_fischer.py`
- **Indicators**: Uses **ZLEMA (Zero-Lag EMA)**, **TRIMA (Triangular MA)**, and **Fisher Transform**.
- **Strategy**: Requires a threshold number of conditions (`buy_threshold`, `sell_threshold`) based on momentum and trend signals.


## Tunes

This repository also contains a `tunes` directory created by QTradeX's tune manager, each labeled with the strategy name and number of parameters.  These tunes do not have to be interacted with manually and are automatically indexed by the tune manager.
