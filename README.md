# DATATHON 2026 - The Gridbreakers
**Team:** Neu_BRT | **Competition:** VinTelligence x VinUniversity DS&AI Club

---

## Cau truc thu muc

```
.
├── config.yaml              # Cau hinh duong dan, tham so, seed
├── requirements.txt         # Thu vien can cai
├── dataset/                 # Du lieu goc (CSV)
├── notebooks/
│   ├── 00_data_overview.ipynb        # Schema, missing, sanity check
│   ├── 01_mcq_answers.ipynb          # Tinh 10 cau trac nghiem
│   ├── 02_eda_descriptive.ipynb      # Cap 1: What happened
│   ├── 03_eda_diagnostic.ipynb       # Cap 2: Why did it happen
│   ├── 04_eda_predictive.ipynb       # Cap 3: What will happen
│   ├── 05_eda_prescriptive.ipynb     # Cap 4: What should we do
│   ├── 06_feature_engineering.ipynb  # Build feature matrix
│   ├── 07_modeling_baseline.ipynb    # Naive / Prophet / SARIMAX
│   ├── 08_modeling_ml.ipynb          # LightGBM / XGBoost / CatBoost
│   ├── 09_modeling_ensemble.ipynb    # Stacking + blend toi uu 3 metrics
│   └── 10_explainability.ipynb       # SHAP / feature importance
├── src/
│   ├── data_loader.py         # Load + parse CSV
│   ├── utils.py               # Seed, logging, IO
│   ├── metrics.py             # MAE, RMSE, R2, composite score
│   ├── validation.py          # TimeSeriesSplit expanding window
│   ├── features/
│   │   ├── calendar.py        # Calendar + holidays + Tet
│   │   ├── lags.py            # Lag/rolling/EWMA
│   │   ├── transactional.py   # Aggregate tu orders/items/web_traffic
│   │   ├── promotions.py      # Promo features
│   │   └── pipeline.py        # Build full feature matrix
│   └── models/
│       ├── baseline.py        # Naive, SeasonalNaive, EMA
│       ├── gbm.py             # LGBM / XGB / CatBoost wrappers
│       └── ensemble.py        # Blend weight optimization
├── scripts/
│   ├── train.py               # CLI train all models
│   ├── predict.py             # CLI gen submission.csv
│   └── reproduce.sh           # Chay lai ket qua end-to-end
├── outputs/
│   ├── figures/               # PNG/PDF cho EDA & report
│   ├── models/                # Model artifacts
│   ├── cv_results/            # CV scores
│   └── submissions/           # submission_v01..vN.csv + final
└── report/
    ├── main.tex               # NeurIPS 2025 LaTeX, <=4 trang
    └── figures/               # Figures cho report
```

---

## Chay lai ket qua

```bash
# 1. Cai thu vien
pip install -r requirements.txt

# 2. Chay toan bo pipeline
bash scripts/reproduce.sh

# 3. Hoac chay tung buoc
python scripts/train.py
python scripts/predict.py
```

**Random seed = 42** duoc dat trong `config.yaml` va ap dung thong nhat toan bo pipeline.

---

## Kaggle Submission
Link: https://www.kaggle.com/competitions/datathon-2026-round-1

File nop: `outputs/submissions/submission_final.csv` (548 dong, giu nguyen thu tu sample_submission.csv)
