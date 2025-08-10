# CMPT 353 Project — Figures and RQ3 Analysis
Tianxi Huang

This repo generates the report figures and runs the RQ3 statistical analysis from a single cleaned dataset.

## What’s included
- `graph.py`: creates publication-ready figures and saves them to `reports/figures/`.
- `project.ipynb`: end-to-end notebook (ETL/modeling/analysis) and saves summary CSVs for plotting.
- `cleaned_data/`: input CSVs for figures (e.g., `top_predictors_rq1.csv`, `roi_merged_full.csv`, `listings_unified_clean.csv`) and RQ3 outputs saved by the notebook (`rq3_price_summary.csv`, `rq3_license_share.csv`, etc.).
- `reports/figures/`: output images.

## Setup (Windows PowerShell)
Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
### Required folders
Ensure these folders exist (create them if missing):
```powershell
# from the project root
New-Item -ItemType Directory -Force .\cleaned_data | Out-Null
New-Item -ItemType Directory -Force .\reports\figures | Out-Null
```
All dependencies tested on Window PC.

## Steps: run the notebook first, then build figures
Option A — VS Code:
- Open `project.ipynb` in VS Code.
- Select the Python kernel you installed (Python 3.12 recommended).
- Run `All cells` top-to-bottom. This will produce the RQ3 CSVs in `cleaned_data/` automatically.
- When it finishes, run:
   ```powershell
   python .\graph.py
   ```

Option B — Jupyter:
- Launch Jupyter
- Open `project.ipynb`, use Run All, wait for completion, then in a terminal run `python .\graph.py`.

## Generate Figures
From the project root:
```powershell
python .\graph.py
```
This will create:
- `fig_rq1_rf_importance.png`
- `fig_rq2_roi_top10_all.png`
- `fig_rq2_roi_top_vancouver.png`
- `fig_rq2_roi_top_victoria.png`
- `fig_rq3_avg_price_prepost.png` (requires `cleaned_data/rq3_price_summary.csv`)
- `fig_rq3_license_share_prepost.png` (requires `cleaned_data/rq3_license_share.csv`)

## Troubleshooting
- If geospatial installs fail, you can still run RQ1/RQ2/RQ3 figures without GeoPandas. Only the mapping cells in the notebook need GeoPandas/Shapely.
- Ensure `cleaned_data/listings_unified_clean.csv` is present; otherwise, the RQ3 cell cannot run.

## License
Free to use/modify.


