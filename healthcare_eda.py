"""
==============================================================================
HEALTHCARE DATA ANALYSIS - EXPLORATORY DATA ANALYSIS (EDA)
==============================================================================
Author: Data Analyst
Description:
    End-to-end EDA pipeline for the healthcare dataset. This script:
        1. Loads the raw dataset
        2. Inspects structure, data types, and data quality
        3. Cleans the data (missing values, duplicates, inconsistent text,
           invalid values, outliers)
        4. Produces descriptive statistics
        5. Generates and saves professional visualizations
        6. Prints a summary of key healthcare insights

Run from the project root or the Notebook/ folder:
    python healthcare_eda.py

All paths below are relative, so the script works after the project folder
is extracted anywhere on disk, as long as the folder structure is preserved.
==============================================================================
"""

import os
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend so charts save without a display
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# ------------------------------------------------------------------------
# 0. PATH SETUP (relative, works regardless of current working directory)
# ------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DATA_PATH = os.path.join(PROJECT_ROOT, "Data", "healthcare_data.csv")
CLEAN_DATA_PATH = os.path.join(PROJECT_ROOT, "Data", "cleaned_healthcare_data.csv")
VIZ_DIR = os.path.join(PROJECT_ROOT, "Visualization")

os.makedirs(VIZ_DIR, exist_ok=True)

# ------------------------------------------------------------------------
# Plot styling - consistent professional look across all charts
# ------------------------------------------------------------------------
sns.set_theme(style="whitegrid")
PALETTE = "viridis"
plt.rcParams.update({
    "figure.dpi": 120,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "font.size": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def save_chart(fig, filename):
    """Save a chart into the Visualization folder and close the figure."""
    path = os.path.join(VIZ_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: Visualization/{filename}")


print("=" * 78)
print("HEALTHCARE DATA ANALYSIS - EDA PIPELINE")
print("=" * 78)

# ==========================================================================
# 1. LOAD DATA
# ==========================================================================
print("\n[1] Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"    Loaded {df.shape[0]:,} rows and {df.shape[1]} columns.")

# ==========================================================================
# 2. INITIAL INSPECTION
# ==========================================================================
print("\n[2] Dataset structure")
print("-" * 78)
print(df.dtypes)

print("\nColumn names:", list(df.columns))

# ==========================================================================
# 3. DATA QUALITY CHECKS
# ==========================================================================
print("\n[3] Data quality checks")
print("-" * 78)

missing = df.isnull().sum()
print("Missing values per column:")
print(missing[missing > 0] if missing.sum() > 0 else "  No missing values found.")

n_duplicates = df.duplicated().sum()
print(f"\nFully duplicated rows: {n_duplicates}")

n_negative_billing = (df["Billing Amount"] < 0).sum()
print(f"Negative Billing Amount values (invalid charges): {n_negative_billing}")

print("\nUnique value counts for categorical columns:")
categorical_cols = ["Gender", "Blood Type", "Medical Condition", "Admission Type",
                     "Test Results", "Insurance Provider", "Medication"]
for col in categorical_cols:
    print(f"  {col}: {df[col].nunique()} unique -> {sorted(df[col].unique())}")

print(f"\nUnique patient names: {df['Name'].nunique():,} (of {len(df):,} records)")
print(f"Unique hospitals: {df['Hospital'].nunique():,}")
print(f"Unique doctors: {df['Doctor'].nunique():,}")

print("\nAge range: {} - {}".format(df["Age"].min(), df["Age"].max()))
print("Billing Amount range: {:.2f} - {:.2f}".format(df["Billing Amount"].min(), df["Billing Amount"].max()))
print("Room Number range: {} - {}".format(df["Room Number"].min(), df["Room Number"].max()))

# ==========================================================================
# 4. DATA CLEANING
# ==========================================================================
print("\n[4] Data cleaning")
print("-" * 78)

df_clean = df.copy()

# 4.1 Standardize the "Name" column (mixed/inconsistent capitalization observed)
df_clean["Name"] = df_clean["Name"].str.strip().str.title()
print("  - Standardized patient name capitalization (Title Case).")

# 4.2 Standardize text columns (strip whitespace)
text_cols = ["Gender", "Blood Type", "Medical Condition", "Doctor", "Hospital",
             "Insurance Provider", "Admission Type", "Medication", "Test Results"]
for col in text_cols:
    df_clean[col] = df_clean[col].astype(str).str.strip()
print("  - Stripped leading/trailing whitespace from text columns.")

# 4.3 Correct data types: convert date columns to datetime
df_clean["Date of Admission"] = pd.to_datetime(df_clean["Date of Admission"], errors="coerce")
df_clean["Discharge Date"] = pd.to_datetime(df_clean["Discharge Date"], errors="coerce")
print("  - Converted 'Date of Admission' and 'Discharge Date' to datetime.")

# 4.4 Remove exact duplicate records
before = len(df_clean)
df_clean = df_clean.drop_duplicates()
after = len(df_clean)
print(f"  - Removed {before - after} fully duplicated records ({before:,} -> {after:,}).")

# 4.5 Handle invalid Billing Amount values (negative charges are not valid)
before = len(df_clean)
df_clean = df_clean[df_clean["Billing Amount"] >= 0]
after = len(df_clean)
print(f"  - Removed {before - after} records with negative Billing Amount ({before:,} -> {after:,}).")

# 4.6 Derived column: Length of Stay (days) - useful for healthcare analysis
df_clean["Length of Stay"] = (df_clean["Discharge Date"] - df_clean["Date of Admission"]).dt.days
invalid_los = (df_clean["Length of Stay"] < 0).sum()
if invalid_los > 0:
    df_clean = df_clean[df_clean["Length of Stay"] >= 0]
print(f"  - Derived 'Length of Stay' from admission/discharge dates "
      f"({invalid_los} invalid records removed).")

# 4.7 Derived column: Admission Year / Month for trend analysis
df_clean["Admission Year"] = df_clean["Date of Admission"].dt.year
df_clean["Admission Month"] = df_clean["Date of Admission"].dt.month
df_clean["Admission Year-Month"] = df_clean["Date of Admission"].dt.to_period("M").astype(str)

# 4.8 Outlier detection on Billing Amount using IQR (reported, not removed,
#     since high-cost treatments are plausible in a real healthcare setting)
Q1 = df_clean["Billing Amount"].quantile(0.25)
Q3 = df_clean["Billing Amount"].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
n_outliers = ((df_clean["Billing Amount"] < lower_bound) | (df_clean["Billing Amount"] > upper_bound)).sum()
print(f"  - Billing Amount IQR outlier check: {n_outliers} potential outliers "
      f"(kept in dataset; billing amounts are valid business values).")

print(f"\n  Final cleaned dataset: {df_clean.shape[0]:,} rows x {df_clean.shape[1]} columns.")

# Save cleaned dataset
df_clean.to_csv(CLEAN_DATA_PATH, index=False)
print(f"  Cleaned dataset saved to: Data/cleaned_healthcare_data.csv")

# ==========================================================================
# 5. DESCRIPTIVE STATISTICS
# ==========================================================================
print("\n[5] Descriptive statistics")
print("-" * 78)
print(df_clean[["Age", "Billing Amount", "Length of Stay"]].describe().round(2))

# ==========================================================================
# 6. EXPLORATORY DATA ANALYSIS + VISUALIZATIONS
# ==========================================================================
print("\n[6] Generating visualizations")
print("-" * 78)

COLOR_MAIN = "#2563eb"
COLOR_ACCENT = "#0ea5e9"

# --- Chart 01: Age Distribution -------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df_clean["Age"], bins=30, kde=True, color=COLOR_MAIN, ax=ax)
ax.set_title("Patient Age Distribution")
ax.set_xlabel("Age (years)")
ax.set_ylabel("Number of Patients")
save_chart(fig, "01_age_distribution.png")

# --- Chart 02: Gender Distribution -----------------------------------------
fig, ax = plt.subplots(figsize=(6, 6))
gender_counts = df_clean["Gender"].value_counts()
colors = sns.color_palette(PALETTE, len(gender_counts))
ax.pie(gender_counts.values, labels=gender_counts.index, autopct="%1.1f%%",
       colors=colors, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax.set_title("Patient Gender Distribution")
save_chart(fig, "02_gender_distribution.png")

# --- Chart 03: Medical Condition Frequency ---------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
cond_counts = df_clean["Medical Condition"].value_counts()
sns.barplot(x=cond_counts.values, y=cond_counts.index, hue=cond_counts.index,
            palette=PALETTE, ax=ax, legend=False)
ax.set_title("Number of Patients by Medical Condition")
ax.set_xlabel("Number of Patients")
ax.set_ylabel("Medical Condition")
save_chart(fig, "03_medical_condition_frequency.png")

# --- Chart 04: Billing Amount Distribution ---------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df_clean["Billing Amount"], bins=40, kde=True, color=COLOR_ACCENT, ax=ax)
ax.set_title("Billing Amount Distribution")
ax.set_xlabel("Billing Amount (USD)")
ax.set_ylabel("Number of Records")
save_chart(fig, "04_billing_amount_distribution.png")

# --- Chart 05: Average Billing by Medical Condition ------------------------
fig, ax = plt.subplots(figsize=(9, 5))
avg_billing_cond = df_clean.groupby("Medical Condition")["Billing Amount"].mean().sort_values(ascending=False)
sns.barplot(x=avg_billing_cond.values, y=avg_billing_cond.index, hue=avg_billing_cond.index,
            palette=PALETTE, ax=ax, legend=False)
ax.set_title("Average Billing Amount by Medical Condition")
ax.set_xlabel("Average Billing Amount (USD)")
ax.set_ylabel("Medical Condition")
save_chart(fig, "05_avg_billing_by_condition.png")

# --- Chart 06: Admission Type Distribution ---------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
adm_counts = df_clean["Admission Type"].value_counts()
sns.barplot(x=adm_counts.index, y=adm_counts.values, hue=adm_counts.index,
            palette=PALETTE, ax=ax, legend=False)
ax.set_title("Patient Distribution by Admission Type")
ax.set_xlabel("Admission Type")
ax.set_ylabel("Number of Patients")
save_chart(fig, "06_admission_type_distribution.png")

# --- Chart 07: Test Results Distribution -----------------------------------
fig, ax = plt.subplots(figsize=(6, 6))
tr_counts = df_clean["Test Results"].value_counts()
colors = sns.color_palette(PALETTE, len(tr_counts))
ax.pie(tr_counts.values, labels=tr_counts.index, autopct="%1.1f%%",
       colors=colors, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax.set_title("Test Results Distribution")
save_chart(fig, "07_test_results_distribution.png")

# --- Chart 08: Insurance Provider Comparison --------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
ins_counts = df_clean["Insurance Provider"].value_counts()
sns.barplot(x=ins_counts.values, y=ins_counts.index, hue=ins_counts.index,
            palette=PALETTE, ax=ax, legend=False)
ax.set_title("Number of Patients by Insurance Provider")
ax.set_xlabel("Number of Patients")
ax.set_ylabel("Insurance Provider")
save_chart(fig, "08_insurance_provider_distribution.png")

# --- Chart 09: Admissions Trend Over Time -----------------------------------
fig, ax = plt.subplots(figsize=(11, 5))
monthly_trend = df_clean.groupby("Admission Year-Month").size().sort_index()
ax.plot(monthly_trend.index, monthly_trend.values, color=COLOR_MAIN, linewidth=2, marker="o", markersize=3)
ax.set_title("Monthly Patient Admissions Trend (2019-2024)")
ax.set_xlabel("Month")
ax.set_ylabel("Number of Admissions")
step = max(1, len(monthly_trend) // 15)
ax.set_xticks(range(0, len(monthly_trend), step))
ax.set_xticklabels(monthly_trend.index[::step], rotation=45, ha="right")
save_chart(fig, "09_admissions_trend_over_time.png")

# --- Chart 10: Age Group vs Medical Condition (Heatmap) ---------------------
bins = [0, 18, 30, 45, 60, 75, 100]
labels = ["0-18", "19-30", "31-45", "46-60", "61-75", "76+"]
df_clean["Age Group"] = pd.cut(df_clean["Age"], bins=bins, labels=labels, right=True)
pivot = pd.crosstab(df_clean["Age Group"], df_clean["Medical Condition"])
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax, cbar_kws={"label": "Number of Patients"})
ax.set_title("Medical Condition Frequency by Age Group")
ax.set_xlabel("Medical Condition")
ax.set_ylabel("Age Group")
save_chart(fig, "10_age_group_vs_condition_heatmap.png")

# --- Chart 11: Billing Amount by Admission Type (Boxplot) -------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df_clean, x="Admission Type", y="Billing Amount", hue="Admission Type",
            palette=PALETTE, ax=ax, legend=False)
ax.set_title("Billing Amount Distribution by Admission Type")
ax.set_xlabel("Admission Type")
ax.set_ylabel("Billing Amount (USD)")
save_chart(fig, "11_billing_by_admission_type_boxplot.png")

# --- Chart 12: Correlation Heatmap (numeric features) -----------------------
fig, ax = plt.subplots(figsize=(6, 5))
numeric_df = df_clean[["Age", "Billing Amount", "Room Number", "Length of Stay"]]
corr = numeric_df.corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, fmt=".2f", ax=ax,
            cbar_kws={"label": "Correlation"})
ax.set_title("Correlation Heatmap (Numeric Features)")
save_chart(fig, "12_correlation_heatmap.png")

# --- Chart 13: Medication Usage Frequency -----------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
med_counts = df_clean["Medication"].value_counts()
sns.barplot(x=med_counts.values, y=med_counts.index, hue=med_counts.index,
            palette=PALETTE, ax=ax, legend=False)
ax.set_title("Medication Usage Frequency")
ax.set_xlabel("Number of Prescriptions")
ax.set_ylabel("Medication")
save_chart(fig, "13_medication_usage_frequency.png")

# --- Chart 14: Length of Stay Distribution -----------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df_clean["Length of Stay"], bins=30, kde=True, color=COLOR_MAIN, ax=ax)
ax.set_title("Length of Hospital Stay Distribution")
ax.set_xlabel("Length of Stay (days)")
ax.set_ylabel("Number of Patients")
save_chart(fig, "14_length_of_stay_distribution.png")

# --- Chart 15: Top 10 Hospitals by Patient Volume ---------------------------
fig, ax = plt.subplots(figsize=(9, 5))
top_hospitals = df_clean["Hospital"].value_counts().head(10)
sns.barplot(x=top_hospitals.values, y=top_hospitals.index, hue=top_hospitals.index,
            palette=PALETTE, ax=ax, legend=False)
ax.set_title("Top 10 Hospitals by Patient Volume")
ax.set_xlabel("Number of Patients")
ax.set_ylabel("Hospital")
save_chart(fig, "15_top10_hospitals_by_volume.png")

print(f"\n  Total charts generated: 15")

# ==========================================================================
# 7. KEY INSIGHTS SUMMARY
# ==========================================================================
print("\n[7] Key insights summary")
print("-" * 78)

total_patients = len(df_clean)
avg_age = df_clean["Age"].mean()
avg_billing = df_clean["Billing Amount"].mean()
total_billing = df_clean["Billing Amount"].sum()
avg_los = df_clean["Length of Stay"].mean()
most_common_condition = df_clean["Medical Condition"].value_counts().idxmax()
most_common_admission = df_clean["Admission Type"].value_counts().idxmax()
normal_rate = (df_clean["Test Results"] == "Normal").mean() * 100
costliest_condition = avg_billing_cond.idxmax()

insights = f"""
  Total patient records analyzed : {total_patients:,}
  Average patient age            : {avg_age:.1f} years
  Average billing amount         : ${avg_billing:,.2f}
  Total billing (sum)            : ${total_billing:,.2f}
  Average length of stay         : {avg_los:.1f} days
  Most common medical condition  : {most_common_condition}
  Most common admission type     : {most_common_admission}
  Most costly condition (avg $)  : {costliest_condition} (${avg_billing_cond.max():,.2f})
  Share of 'Normal' test results : {normal_rate:.1f}%
"""
print(insights)

# Save a small text summary that the dashboard/report can reference
summary_path = os.path.join(PROJECT_ROOT, "Data", "key_insights_summary.txt")
with open(summary_path, "w") as f:
    f.write("HEALTHCARE DATA ANALYSIS - KEY INSIGHTS SUMMARY\n")
    f.write("=" * 60 + "\n")
    f.write(insights)
print(f"  Summary saved to: Data/key_insights_summary.txt")

print("\n" + "=" * 78)
print("EDA PIPELINE COMPLETE - all charts saved to the Visualization/ folder")
print("=" * 78)
