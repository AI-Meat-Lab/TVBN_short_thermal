# README (short version)

## Scripts in this folder

- `Temperature_TVBN_calculation.py` – runs Mann‑Whitney U tests, FDR correction, and exports summary stats (mean ± SD) for both technical (n=18) and biological (n=6) replicates.
- `tvbn_line_chart.py` – generates the TVB‑N vs. temperature line plot.

## Requirements

```bash
pip install pandas numpy scipy statsmodels openpyxl matplotlib seaborn
```

## Usage

1. Place `Raw data_+Calculation（n=18）.xlsx` in the same directory (or update file paths in the scripts).
2. Run `Temperature_TVBN_calculation.py` to produce `*_analysis_n=6.xlsx` and `*_analysis_n=18.xlsx`.
3. For the correct figure, modify `tvbn_line_chart.py` to read `TVBN_mean` and `TVBN_std` from the `mean_sd` sheet of `*_analysis_n=6.xlsx`.
