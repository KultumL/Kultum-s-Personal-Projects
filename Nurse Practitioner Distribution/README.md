# Georgia Nurse Practitioners — County View (Dash)

An interactive dashboard showing nurse practitioner (NP) availability across Georgia by county. Explore three map views—**NP count**, **NP density per 10,000 residents**, and **doctor-to-NP ratio**—plus a rural/suburban/urban filter and a details panel with income and racial/ethnic composition.

---

## Research question

**How is county-level nurse practitioner density associated with racial/ethnic composition across Georgia, accounting for socioeconomic context and rurality?
Dashboard Link: https://nursepractitionerdistributiondashboard18.onrender.com/**

---

## Data sources

- **Provider rosters:** nurse practitioners and physicians (geocoded to county)  
- **Demographics:** county population and racial/ethnic percentages (Census)  
- **Income:** county median household income (Census)  
- **County type:** rural / suburban / urban classification

> All cleaned/derived files are placed in `data_work/`. Original inputs live in `data_raw/` and are not committed if they contain sensitive data.

---

## Methods (ETL)

- **Python & pandas:** standardized 5-digit FIPS, removed duplicates, fixed missing/inconsistent values  
- **Joins:** combined NP and physician rosters to county, merged Census population and race/ethnicity, attached median income and county type  
- **Derived metrics:** NP **density per 10,000 residents** and **doctor:NP ratio** for all 159 Georgia counties  
- **Validation:** checks for FIPS format, duplicate provider rows, and improbable counts prior to loading the dashboard

---

## Dashboard features

- **Three county choropleths** (Plotly):
  - NP **Count**
  - NP **Density** per **10,000** residents
  - **Doctor:NP** Ratio
- **Filter** by county type (rural / suburban / urban)
- **Details panel** on click:
  - NPs, physicians, NP density, doctor:NP ratio
  - **Median household income**
  - Racial/ethnic composition as a **donut (pie) chart** with consistent sizing and hover that shows face-value percentages
- **Always-on county outlines** and clean hover labels

---

## Findings (summary)

- NP density varies widely across counties even when raw NP counts are similar.  
- **Correlation snapshots**  
  - **Percent non-white vs. NP density:** weak positive association, **r ≈ 0.23**  
  - **Median income vs. NP density:** near-zero association, **r ≈ 0.03**

> These are descriptive associations (not causal) and can be extended with multivariate models.

---
## Tech stack

- **UI:** Plotly **Dash**, Plotly Express/Graph Objects  
- **Data:** **pandas**, **numpy**, **requests**  
- **Serving:** **Gunicorn** (for production deployments such as Render)  
- **Python:** 3.12+ recommended

---

## Quick start

```bash
# 1) (optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2) install
pip install -r requirements.txt

# 3) run locally
python app_dash.py
# open http://127.0.0.1:8050
```

### Production (Render or similar)

- **Build command:** `pip install -r requirements.txt`  
- **Start command:**  
  ```
  gunicorn app_dash:server --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT
  ```
- (Optional) add `runtime.txt` with `python-3.12.x`

---

## Repository structure

```
.
├─ app_dash.py                      # Dash app (layout, callbacks, figures)
├─ requirements.txt                 # Dependencies
├─ runtime.txt                      # Optional: pin Python version for hosting
├─ data_work/                       # Cleaned/derived CSVs + ETL scripts
│  ├─ np_geocoded.csv
│  ├─ phys_geocoded.csv
│  ├─ demographics.csv
│  ├─ county_type_by_fips.csv
│  ├─ income_by_fips.csv
│  └─ 0x_*.py                      # ETL/cleaning scripts
└─ data_raw/                        # Original inputs (not committed)
```

---

## Acknowledgments

Nell Hodgson Woodruff School of Nursing 
Team members: Kultum Lhabaik, Livia Mazniker, Rafaela Sewards, Lorayne Gulbrandsen.

---

## License

Emory University A.I Data Lab
