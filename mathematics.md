# Mathematical Analysis Documentation for Cryptocurrency Metrics

This document consolidates the mathematical equations and variables used for fundamental, technical, quantitative, and peer analysis of cryptocurrency metrics within the /src folder.

## Table of Contents
1. [Fundamental Analysis](#fundamental-analysis)
2. [Technical Analysis](#technical-analysis)
3. [Quantitative Analysis](#quantitative-analysis)
4. [Peer Analysis](#peer-analysis)

## Fundamental Analysis

### 1. NVT Ratio
- **Equation**: `(P × S) / (V × P)` (mean over period)
- **Variables**:
  - `P`: Close Price
  - `S`: Circulating Supply
  - `V`: Volume

### 2. Price/Volume Ratio
- **Equation**: `P_current / (V × P)_mean`
- **Variables**:
  - `P_current`: Current Close Price
  - `(V × P)_mean`: Average Quote Volume

### 3. Market Cap Growth Rate
- **Equation**: `((P_end × S) / (P_start × S))^(1 / t) - 1`
- **Variables**:
  - `P_end`: End Price
  - `P_start`: Start Price
  - `S`: Circulating Supply
  - `t`: Time in Years (1)

### 4. Volume CAGR
- **Equation**: `((V_end × P_end) / (V_start × P_start))^(1 / t) - 1`
- **Variables**:
  - `V_end`: End Volume
  - `V_start`: Start Volume
  - `P_end`: End Price
  - `P_start`: Start Price
  - `t`: Time in Years (1)

### 5. Liquidity Ratio
- **Equation**: `(V × P)_mean / (P_current × S)`
- **Variables**:
  - `(V × P)_mean`: Average Quote Volume
  - `P_current`: Current Price
  - `S`: Circulating Supply

### 6. Mayer Multiple
- **Equation**: `P_current / SMA_200`
- **Variables**:
  - `P_current`: Current Price
  - `SMA_200`: 200-day Simple Moving Average

### 7. Price Momentum
- **Equation**: `(P_end - P_start) / P_start`
- **Variables**:
  - `P_end`: End Price
  - `P_start`: Start Price

### 8. Volume Momentum
- **Equation**: `((V × P)_late - (V × P)_early) / (V × P)_early`
- **Variables**:
  - `(V × P)_late`: Mean Quote Volume (second half)
  - `(V × P)_early`: Mean Quote Volume (first half)

### 9. Volatility-Adjusted Market Cap
- **Equation**: `(P_current × S) / (1 + σ)`
- **Variables**:
  - `P_current`: Current Price
  - `S`: Circulating Supply
  - `σ`: Annualized Volatility (`std(P_pct_change) × √365`)

### 10. Turnover Ratio
- **Equation**: `Σ(V × P) / S`
- **Variables**:
  - `Σ(V × P)`: Total Quote Volume
  - `S`: Circulating Supply

### 11. Price Stability Ratio
- **Equation**: `P_mean / σ`
- **Variables**:
  - `P_mean`: Mean Price
  - `σ`: Annualized Volatility

### 12. Volume-to-Price Ratio
- **Equation**: `(V × P)_mean / P_current`
- **Variables**:
  - `(V × P)_mean`: Average Quote Volume
  - `P_current`: Current Price

### 13. Discounted Expected Utility Value (DEUV)
- **Equation**: `(P_current × S) / Σ[(V × P)_current × (1 + g)^t / (1 + r)^t]` (t = 1 to 5)
- **Variables**:
  - `P_current`: Current Price
  - `S`: Circulating Supply
  - `(V × P)_current`: Current Average Quote Volume
  - `g`: Growth Rate (0.08)
  - `r`: Discount Rate (0.12)

### 14. Price to Volatility Cost
- **Equation**: `P_current / (P_current × σ)`
- **Variables**:
  - `P_current`: Current Price
  - `σ`: Annualized Volatility

### 15. Regulatory Discount
- **Equation**: `P_current × (1 - h)`
- **Variables**:
  - `P_current`: Current Price
  - `h`: Haircut (0.20)

## Technical Analysis

### 1. SMA 50-day
- **Equation**: `Σ(P_i) / 50` (last 50 days)
- **Variables**:
  - `P_i`: Close Price at day i

### 2. EMA 20-day
- **Equation**: `(P_current × k) + (EMA_prev × (1 - k))`, `k = 2 / (20 + 1)`
- **Variables**:
  - `P_current`: Current Price
  - `EMA_prev`: Previous EMA
  - `k`: Smoothing Factor

### 3. RSI
- **Equation**: `100 - (100 / (1 + (Avg Gain / Avg Loss)))` (14-day period)
- **Variables**:
  - `Avg Gain`: Mean of positive price changes
  - `Avg Loss`: Mean of negative price changes

### 4. MACD Histogram
- **Equation**: `(EMA_12 - EMA_26) - Signal`, `Signal = EMA_9 of (EMA_12 - EMA_26)`
- **Variables**:
  - `EMA_12`: 12-day EMA
  - `EMA_26`: 26-day EMA
  - `Signal`: 9-day EMA

### 5. Bollinger Bands Width
- **Equation**: `(Upper - Lower) / SMA_20`, `Upper = SMA_20 + 2 × σ_20`, `Lower = SMA_20 - 2 × σ_20`
- **Variables**:
  - `SMA_20`: 20-day SMA
  - `σ_20`: 20-day Standard Deviation

### 6. ATR
- **Equation**: `Σ(TR_i) / 14` (last 14 days), `TR_i = max(H - L, |H - C_prev|, |L - C_prev|)`
- **Variables**:
  - `H`: High
  - `L`: Low
  - `C_prev`: Previous Close

### 7. OBV
- **Equation**: `Σ(V × sign(C - C_prev))`
- **Variables**:
  - `V`: Volume
  - `sign(C - C_prev)`: 1 if `C > C_prev`, -1 if `C < C_prev`, 0 if equal

### 8. VWAP
- **Equation**: `Σ((H + L + C) / 3 × V) / ΣV`
- **Variables**:
  - `H`: High
  - `L`: Low
  - `C`: Close
  - `V`: Volume

### 9. Price ROC
- **Equation**: `((P_current - P_14) / P_14) × 100`
- **Variables**:
  - `P_current`: Current Price
  - `P_14`: Price 14 days ago

### 10. Stochastic %K
- **Equation**: `100 × (C - L_14) / (H_14 - L_14)`
- **Variables**:
  - `C`: Current Close
  - `L_14`: Lowest Low (14 days)
  - `H_14`: Highest High (14 days)

### 11. Williams %R
- **Equation**: `-100 × (H_14 - C) / (H_14 - L_14)`
- **Variables**:
  - `H_14`: Highest High (14 days)
  - `L_14`: Lowest Low (14 days)
  - `C`: Current Close

### 12. Momentum
- **Equation**: `P_current - P_10`
- **Variables**:
  - `P_current`: Current Price
  - `P_10`: Price 10 days ago

### 13. Volume Oscillator
- **Equation**: `((V_MA_5 - V_MA_20) / V_MA_20) × 100`
- **Variables**:
  - `V_MA_5`: 5-day Volume MA
  - `V_MA_20`: 20-day Volume MA

### 14. Chande Momentum Oscillator (CMO)
- **Equation**: `100 × (ΣUp - ΣDown) / (ΣUp + ΣDown)` (14-day period)
- **Variables**:
  - `ΣUp`: Sum of positive price changes
  - `ΣDown`: Sum of negative price changes

### 15. Price Channel Breakout
- **Equation**: `1 if P_current > H_20, -1 if P_current < L_20, else 0`
- **Variables**:
  - `P_current`: Current Price
  - `H_20`: 20-day High
  - `L_20`: 20-day Low

## Quantitative Analysis

### 1. NVT Ratio
- **Equation**: `(P × S) / (V × P)` (mean)
- **Variables**:
  - `P`: Close Price
  - `S`: Circulating Supply
  - `V`: Volume

### 2. Price/Volume Ratio
- **Equation**: `P_current / (V × P)_mean`
- **Variables**:
  - `P_current`: Current Price
  - `(V × P)_mean`: Average Quote Volume

### 3. Sharpe Ratio
- **Equation**: `(R_mean + APY_d - Rf_d) / σ × √365`
- **Variables**:
  - `R_mean`: Mean Daily Return
  - `APY_d`: Staking Yield / 365 (0.06 / 365)
  - `Rf_d`: Risk-Free Rate / 365 (0.025 / 365)
  - `σ`: Daily Return Std

### 4. Current Utility Value (CUV)
- **Equation**: `(P_current × S) / (V × P)_mean`
- **Variables**:
  - `P_current`: Current Price
  - `S`: Circulating Supply
  - `(V × P)_mean`: Average Quote Volume

### 5. Discounted Expected Utility Value (DEUV)
- **Equation**: `(P_current × S) / Σ[(V × P)_current × (1 + g)^t / (1 + r)^t]` (t = 1 to 5)
- **Variables**:
  - `P_current`: Current Price
  - `S`: Circulating Supply
  - `(V × P)_current`: Current Average Quote Volume
  - `g`: Growth Rate (0.08)
  - `r`: Discount Rate (0.12)

### 6. Volume CAGR
- **Equation**: `((V_end × P_end) / (V_start × P_start))^(1 / t) - 1`
- **Variables**:
  - `V_end`: End Volume
  - `V_start`: Start Volume
  - `P_end`: End Price
  - `P_start`: Start Price
  - `t`: Time in Years (1)

### 7. Volume Composition (Buy)
- **Equation**: `V_buy / (V × P)_total`
- **Variables**:
  - `V_buy`: Taker Buy Quote Volume
  - `(V × P)_total`: Total Quote Volume

### 8. Volume Composition (Sell)
- **Equation**: `V_sell / (V × P)_total`
- **Variables**:
  - `V_sell`: Total Quote Volume - `V_buy`
  - `(V × P)_total`: Total Quote Volume

### 9. Volatility Reduction
- **Equation**: `(σ_early - σ_late) / σ_early` (if > 0, else 0)
- **Variables**:
  - `σ_early`: Std of Returns (first half) × √365
  - `σ_late`: Std of Returns (second half) × √365

### 10. Price Momentum
- **Equation**: `(P_end - P_start) / P_start`
- **Variables**:
  - `P_end`: End Price
  - `P_start`: Start Price

### 11. Risk-Adjusted Volume Discount
- **Equation**: `(V × P)_mean / (1 + (Rf + β × MRP) × σ) / (V × P)_mean`
- **Variables**:
  - `(V × P)_mean`: Average Quote Volume
  - `Rf`: Risk-Free Rate (0.025)
  - `β`: Beta (1.4)
  - `MRP`: Market Risk Premium (0.06)
  - `σ`: Annualized Volatility

### 12. Trading Volume
- **Equation**: `(V × P)_mean`
- **Variables**:
  - `(V × P)_mean`: Average Quote Volume

### 13. Volume Volatility
- **Equation**: `σ_v / (V × P)_mean`
- **Variables**:
  - `σ_v`: Std of Quote Volume
  - `(V × P)_mean`: Average Quote Volume

### 14. Volume-to-Price Ratio
- **Equation**: `(V × P)_mean / P_current`
- **Variables**:
  - `(V × P)_mean`: Average Quote Volume
  - `P_current`: Current Price

### 15. Price Correlation
- **Equation**: `corr(P_pct_change, P_pct_change)` (self-correlation = 1)
- **Variables**:
  - `P_pct_change`: Daily Price Returns

### 16. Mayer Multiple
- **Equation**: `P_current / SMA_200`
- **Variables**:
  - `P_current`: Current Price
  - `SMA_200`: 200-day SMA

### 17. Price DCF Intrinsic Value
- **Equation**: `Σ[P_current × (1 + g)^t / (1 + r)^t]` (t = 1 to 5)
- **Variables**:
  - `P_current`: Current Price
  - `g`: Growth Rate (0.10)
  - `r`: Discount Rate (0.15)

### 18. Price DCF Valuation Ratio
- **Equation**: `DCF_Intrinsic / P_current`
- **Variables**:
  - `DCF_Intrinsic`: Price DCF Intrinsic Value
  - `P_current`: Current Price

### 19. Price to Volatility Cost
- **Equation**: `P_current / (P_current × σ)`
- **Variables**:
  - `P_current`: Current Price
  - `σ`: Annualized Volatility

### 20. Regulatory Discount
- **Equation**: `P_current × (1 - h)`
- **Variables**:
  - `P_current`: Current Price
  - `h`: Haircut (0.20)

### 21. Price/Volume Ratio (Alt)
- **Equation**: `P_current / (V × P)_30day_mean`
- **Variables**:
  - `P_current`: Current Price
  - `(V × P)_30day_mean`: 30-day Average Quote Volume

## Peer Analysis

### 1. NVT Ratio
- **Equation**: `(P × S) / (V × P)` (mean)
- **Variables**:
  - `P`: Close Price
  - `S`: Circulating Supply
  - `V`: Volume

### 2. Sharpe Ratio
- **Equation**: `(R_mean + APY_d - Rf_d) / σ × √365`
- **Variables**:
  - `R_mean`: Mean Daily Return
  - `APY_d`: Staking Yield / 365 (0.05 / 365)
  - `Rf_d`: Risk-Free Rate / 365 (0.025 / 365)
  - `σ`: Daily Return Std

### 3. Price/Volume Ratio
- **Equation**: `P_current / (V × P)_mean`
- **Variables**:
  - `P_current`: Current Price
  - `(V × P)_mean`: Average Quote Volume

### 4. Mayer Multiple
- **Equation**: `P_current / SMA_200`
- **Variables**:
  - `P_current`: Current Price
  - `SMA_200`: 200-day SMA

### 5. Speculative Signal
- **Equation**: `1 if NVT > 50 or Mayer > 2.4, else 0`
- **Variables**:
  - `NVT`: NVT Ratio
  - `Mayer`: Mayer Multiple

### 6. RSI
- **Equation**: `100 - (100 / (1 + (Avg Gain / Avg Loss)))` (14-day period)
- **Variables**:
  - `Avg Gain`: Mean of positive price changes
  - `Avg Loss`: Mean of negative price changes

### 7. MACD Histogram
- **Equation**: `(EMA_12 - EMA_26) - Signal`, `Signal = EMA_9 of (EMA_12 - EMA_26)`
- **Variables**:
  - `EMA_12`: 12-day EMA
  - `EMA_26`: 26-day EMA
  - `Signal`: 9-day EMA

---
