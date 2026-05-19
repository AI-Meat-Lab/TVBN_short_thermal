# Short Thermal Exposure Effects on Measured TVB-N

This repository contains code and data to reproduce the statistical analysis and figures in the manuscript:

The code performs:
- Calculation of TVB‑N means and standard deviations
- Pairwise Mann‑Whitney U tests with False Discovery Rate (FDR) correction
- Generation of the TVB‑N vs. temperature line plot (Figure 2)

---

## File Overview

| File | Description |
|------|-------------|
| `Temperature_TVBN_calculation.py` | Main analysis script. Computes summary statistics, performs Mann‑Whitney U tests, applies FDR correction, and exports results for both technical (n=18) and biological (n=6) replicates. |
| `tvbn line chart.py` | Plotting script. Generates the TVB‑N line plot (error bars = standard deviation). 

---

## Requirements

Install the required Python packages:

```bash
pip install pandas numpy scipy statsmodels openpyxl matplotlib seaborn
```

- Python ≥ 3.8
- The scripts were developed on Windows, but should run on any OS after adjusting file paths.

---

## Usage

### 1. Prepare the data

Place `Raw data_+Calculation（n=18）.xlsx` in ```data``` directory.  
The Excel file contains a sheet named `original_data` with columns:

- `Sample` (chicken/pork/beef)
- `ID` (e.g., `C_40_1_1` – last underscore separates technical replicate)
- `Temperature` (15, 25, 30, 40 °C)
- `TVBN` (mg/100g, pre‑calculated)
- (Other columns: m‑weight, volumes, etc.)

### 2. Run the analysis script

Edit the file paths in `Temperature_TVBN_calculation.py`:

```python
# Change these lines to your actual file locations
df = pd.read_excel(r"your_path/Raw data_+Calculation（n=18）.xlsx")
# Output paths
with pd.ExcelWriter(r"your_path/temperature_exp_analysis_n=18.xlsx", ...)
with pd.ExcelWriter(r"your_path/temperature_exp_analysis_n=6.xlsx", ...)
```

Then execute:

```bash
python Temperature_TVBN_calculation.py
```

This produces two Excel files:
- `temperature_exp_analysis_n=18.xlsx` – statistics using all technical replicates (n=18)
- `temperature_exp_analysis_n=6.xlsx` – statistics using biological replicates (n=6, after averaging technical triplicates)

**The paper uses the biological‑replicate results (n=6).**  
Each output file contains three sheets:
- `original_data` – copy of input
- `mean_sd` – mean ± SD per meat type and temperature
- `test` – pairwise Mann‑Whitney U test results with FDR‑adjusted p‑values

### 3. Generate the line plot

The plotting script `tvbn line chart.py` currently uses **hard‑coded mean and SD values from the n=18 analysis**.  
To reproduce the **paper’s Figure 2** (which uses biological‑replicate SDs), you have two options:

To run the script as‑is:

```bash
python tvbn_line_chart.py
```

The figure is saved as `TVBN_lineplot_final.tiff`.

---

## Reproducibility

The code exactly reproduces the statistical tests reported in the paper (Mann‑Whitney U with FDR correction, effect sizes as rank‑biserial correlation).  
To obtain the exact numerical values shown in Table 1 and Figure 2, run `Temperature_TVBN_calculation.py` and use the **n=6 output** (biological replicates). The paper’s analytical standard deviation (0.47 mg/100g for pork at 15°C) was calculated separately from technical triplicates and is consistent with the variability shown in the raw data.

---

## Contact

For questions about the code or data, please contact the corresponding authors:  
Celio Dias Santos‑Junior – celio@mail.hzau.edu.cn  
Haizhou Wu – haizhou@mail.hzau.edu.cn
