# DATATHON 2026 Round 1 - NEU-BRT

Official solution repository of team **NEU-BRT** for **DATATHON 2026 Round 1**.

## Team Information

- **Team name:** NEU-BRT
- **Competition:** DATATHON 2026 - Round 1
- **Submission deadline:** 23:59, 01/05/2026

## Project Overview

This repository contains our team's work for the preliminary round of DATATHON 2026, including:

- Data exploration and preprocessing
- Feature engineering
- Model training and evaluation
- Kaggle submission pipeline
- Final report and reproducibility materials

## Problem Statement

The competition focuses on forecasting future sales from historical business data.  
The dataset simulates the operations of a Vietnamese fashion e-commerce business, covering multiple aspects such as:

- Orders
- Inventory
- Promotions
- Website traffic

Our goal is to build a robust and reproducible machine learning pipeline that can generate accurate sales predictions.

## Repository Structure

```bash
datathon-2026-round1-neu-brt/
│── data/
│   ├── raw/                 # Raw input data
│   ├── processed/           # Cleaned / transformed data
│
│── notebooks/
│   ├── 01_eda.ipynb         # Exploratory data analysis
│   ├── 02_preprocessing.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modeling.ipynb
│   └── 05_submission.ipynb
│
│── src/
│   ├── data/                # Data loading and preprocessing scripts
│   ├── features/            # Feature engineering modules
│   ├── models/              # Training / inference code
│   ├── utils/               # Helper functions
│   └── config.py
│
│── reports/
│   └── final_report.pdf     # Final submitted report
│
│── outputs/
│   ├── figures/             # Plots and visualizations
│   ├── predictions/         # Validation/test predictions
│   └── submissions/         # Kaggle submission files
│
│── requirements.txt
│── README.md