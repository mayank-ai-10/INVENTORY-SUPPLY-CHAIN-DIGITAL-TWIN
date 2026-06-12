import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# =========================
# CONFIG
# =========================
DATA_FOLDER = "."

groups = {
    "Delivery_vs_Backlog": ["delivery.csv", "backlog.csv"],
    "Inventory_vs_Pipeline": ["inventory.csv", "pipeline_inventory.csv"],
    "Inventory_vs_Returned": ["inventory2.csv", "returned_inventory.csv"],
    "Waste_vs_Disposal": ["waste_accumulation.csv", "waste_disposal.csv"],
    "Delivery_vs_Unfulfilled": ["delivery2.csv", "unfulfilled_demand.csv"],
    "Backlog_vs_Fulfillment": ["backlog2.csv", "backlog_fulfillment.csv"]
}

# =========================
# LOAD CSV (SAFE)
# =========================
def load_csv(file):
    path = os.path.join(DATA_FOLDER, file)

    try:
        df = pd.read_csv(path)
    except:
        df = pd.read_csv(path, header=None)

    df.columns = [str(c).strip().lower() for c in df.columns]

    # If no proper headers
    if len(df.columns) == 2:
        df.columns = ["time", "value"]

    # Ensure time column exists
    if "time" not in df.columns:
        df.rename(columns={df.columns[0]: "time"}, inplace=True)

    return df


def get_value_column(df):
    return [c for c in df.columns if c != "time"][0]


def clean_name(file):
    return file.replace(".csv", "").replace("_", " ").title()


# =========================
# ANALYSIS FUNCTIONS
# =========================

def trend(series):
    return "increasing" if series.iloc[-1] > series.iloc[0] else "decreasing"


def correlation(x, y):
    df = pd.concat([x, y], axis=1).dropna()
    if len(df) < 2:
        return 0
    return df.iloc[:, 0].corr(df.iloc[:, 1])


def lag_effect(x, y, max_lag=8):
    best_lag = 0
    best_corr = 0

    for lag in range(1, max_lag):
        corr = x[:-lag].corr(y[lag:])
        if abs(corr) > abs(best_corr):
            best_corr = corr
            best_lag = lag

    return best_lag


def shock(series):
    diff = np.diff(series)
    return np.argmax(np.abs(diff))


# =========================
# MAIN
# =========================

report = ""

for group, files in groups.items():

    print(f"\nProcessing {group}...")

    df1 = load_csv(files[0])
    df2 = load_csv(files[1])

    col1 = get_value_column(df1)
    col2 = get_value_column(df2)

    name1 = clean_name(files[0])
    name2 = clean_name(files[1])

    # Merge
    merged = pd.merge(
        df1[["time", col1]],
        df2[["time", col2]],
        on="time",
        suffixes=("_1", "_2")
    )

    m1 = col1 + "_1"
    m2 = col2 + "_2"

    # Clean NaN
    merged = merged.dropna()

    # Analysis
    t1 = trend(df1[col1])
    t2 = trend(df2[col2])

    corr = correlation(merged[m1], merged[m2])
    lag = lag_effect(merged[m1], merged[m2])
    s1 = shock(df1[col1])
    s2 = shock(df2[col2])

    # =========================
    # PLOT
    # =========================
    plt.figure()
    plt.plot(df1["time"], df1[col1], label=name1)
    plt.plot(df2["time"], df2[col2], label=name2)

    plt.title(group)
    plt.xlabel("Time")
    plt.ylabel("Values")
    plt.legend()
    plt.grid()

    plt.savefig(f"{group}.png")
    plt.close()

    # =========================
    # EXPLANATION
    # =========================
    explanation = f"""
=== {group} ===

Trend:
- {name1}: {t1}
- {name2}: {t2}

Shock:
- {name1}: week {s1}
- {name2}: week {s2}

Correlation: {corr:.2f}

Lag Effect:
- {name1} affects {name2} after ~{lag} weeks

System Behavior:
"""

    if corr < -0.5:
        explanation += "Balancing (inverse relationship)\n"
    elif corr > 0.5:
        explanation += "Reinforcing (same direction growth)\n"
    else:
        explanation += "Weak relationship\n"

    explanation += "\n-----------------------------\n"

    print(explanation)
    report += explanation


# =========================
# SAVE REPORT (FIXED)
# =========================
with open("FINAL_REPORT.txt", "w", encoding="utf-8") as f:
    f.write(report)

print("\n✅ Analysis Completed ! 🔥")