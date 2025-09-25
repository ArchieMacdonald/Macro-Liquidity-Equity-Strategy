# Macro Liquidity Equity Strategy

This project implements a **systematic equity strategy** in QuantConnect Lean, combining macroeconomic indicators with fundamental stock screening.
The strategy itself is based upon a youtube video: "Stock investing strategy for EVERYONE(which I developed) by "Defiant Gatekeeper"

## Idea
- Use **Fed Funds Rate (FEDFUNDS)** and **Federal Reserve Balance Sheet (WALCL)** from FRED data to classify liquidity regimes:
  - Most Liquid
  - Neutral
  - Least Liquid
- Screen US equities using fundamental ratios:
  - **Bucket A (Value):** Low P/E, low debt/EBITDA, low revenue growth.
  - **Bucket B&C (Balanced Growth):** Moderate growth, acceptable leverage, reasonable valuations.
  - **Bucket D (High Growth):** Revenue growth > 50%.
- Allocate dynamically based on liquidity regime:
  - Most Liquid → growth stocks (Bucket D).
  - Least Liquid → value stocks (Bucket A).
  - Neutral → balanced growth stocks (Bucket B&C).

## Implementation
- Built in **QuantConnect Lean (Python API)**.
- Coarse and fine universes filter ~1000 liquid US stocks.
- Weekly rebalancing based on macro regime classification.
- Equal-weight portfolio within selected bucket.

## Results
- Backtested from March 2022 to present.
- Liquidity regime switching aligns allocations with macro environment.
- [Add example equity curve plot here].

## Tools
- QuantConnect Lean (QCAlgorithm)
- Python 3.8+
- Data sources: FRED, QuantConnect fundamentals

## Next Steps
- Add transaction cost modelling.
- Compare Sharpe ratios vs SPY benchmark.
- Extend to international equities.

