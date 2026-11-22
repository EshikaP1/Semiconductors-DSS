# Tin final dataset, 2021–2025

Research question: How did price volatility and U.S. import dependence change for refined tin, an input used in semiconductor packaging, from 2021 to 2025?

- `tin_annual_combined_2021_2025.csv`: primary five-row descriptive dataset.
- `tin_monthly_combined_2021_2025.csv`: 60 monthly prices joined to annual quantities. Annual fields are repeated context, not independent monthly flows.
- `tin_trade_context.csv`: official 2025 reliance and pooled 2021–2024 supplier statistics from the supplied trade table.
- `combine_tin_2021_2025.ipynb`: executed reproducible notebook; prints first 50 rows and HTML previews.
- `validation_report.json`: checks, source differences, exclusions and SHA256 fingerprints.
- `inputs/`: the three user-provided input snapshots; do not edit.

## Definitions
Realized annual volatility is the sample standard deviation of 12 monthly simple percentage price changes, not annualized. January uses previous December. Forward three-month volatility is preserved only in the monthly companion and may include prices beyond the current calendar year.

The net-imports/consumption proxy is `(refined imports - refined exports) / apparent refined consumption * 100`. It is NOT official USGS net import reliance. Official reliance is available only for 2025 (77%). Missing 2021–2024 official values are explicitly `not_provided_in_inputs`, not imputed. Therefore the supplied data cannot establish the change in official import reliance over the full period. Do not convert these labels to zero or use them as numeric model inputs.

Imports were mislabelled `consumption` in the supply file; selection uses exact detail. MCS2026 definitions are kept consistent; the competing ds140 2021 consumption value is not substituted. The supplied source does not retain estimate flags; 2025 may be estimated. Price benchmark provenance/purity is not independently verified and it is not semiconductor-packaging-specific. No causal or forecasting claim is made.

## Run
Open the notebook from this directory and Run All (Python kernel; no pandas required). All outputs are recreated from the input snapshots. No external download is needed.
