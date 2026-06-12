import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# STEP 1: LOAD BOTH CSV FILES
# -----------------------------
delivery_df = pd.read_csv("delivery.csv")
backlog_df = pd.read_csv("backlog.csv")

# Assuming both have Time column
time = delivery_df.iloc[:,0]

delivery = delivery_df.iloc[:,1]
backlog = backlog_df.iloc[:,1]


# -----------------------------
# STEP 2: TREND DETECTION
# -----------------------------
def get_trend(series):
    if series.iloc[-1] > series.iloc[0]:
        return "increasing"
    elif series.iloc[-1] < series.iloc[0]:
        return "decreasing"
    else:
        return "stable"

delivery_trend = get_trend(delivery)
backlog_trend = get_trend(backlog)


# -----------------------------
# STEP 3: EVENT DETECTION
# -----------------------------
def detect_events(series):
    events = []
    for i in range(1, len(series)):
        change = series.iloc[i] - series.iloc[i-1]

        if change > np.std(series)*1.5:
            events.append((i, "sharp_rise"))
        elif change < -np.std(series)*1.5:
            events.append((i, "sharp_drop"))

    return events

delivery_events = detect_events(delivery)
backlog_events = detect_events(backlog)


# -----------------------------
# STEP 4: GENERATE EXPLANATION
# -----------------------------
def generate_explanation():
    explanation = ""

    # Delivery analysis
    if delivery_trend == "increasing":
        explanation += "Delivery rate increases over time, indicating improved supply performance.\n"
    elif delivery_trend == "decreasing":
        explanation += "Delivery rate decreases, indicating reduced supply capacity.\n"
    else:
        explanation += "Delivery remains stable over time.\n"

    # Backlog analysis
    if backlog_trend == "increasing":
        explanation += "Backlog increases, indicating accumulation of unmet demand.\n"
    elif backlog_trend == "decreasing":
        explanation += "Backlog decreases, indicating effective fulfillment of pending orders.\n"

    # Relationship logic
    if backlog.mean() > delivery.mean():
        explanation += "Backlog being higher than delivery suggests that demand exceeds supply capacity.\n"

    if delivery_trend == "increasing" and backlog_trend == "decreasing":
        explanation += "Improved delivery is helping reduce backlog, indicating system recovery.\n"

    if delivery_trend == "decreasing" and backlog_trend == "increasing":
        explanation += "Reduced delivery is causing backlog accumulation, indicating system stress.\n"

    # Event explanations
    for i, e in delivery_events:
        explanation += f"At time {time.iloc[i]}, delivery shows a {e}, indicating sudden change in supply.\n"

    for i, e in backlog_events:
        explanation += f"At time {time.iloc[i]}, backlog shows a {e}, reflecting system imbalance.\n"

    return explanation


# -----------------------------
# STEP 5: PRINT OUTPUT
# -----------------------------
explanation = generate_explanation()

print("\n📊 SYSTEM EXPLANATION:\n")
print(explanation)

min_len = min(len(time), len(delivery), len(backlog))

time = time[:min_len]
delivery = delivery[:min_len]
backlog = backlog[:min_len]

# -----------------------------
# STEP 6: PLOT GRAPH
# -----------------------------
plt.figure()
plt.plot(time, delivery, label="Delivery")
plt.plot(time, backlog, label="Backlog")

plt.xlabel("Time")
plt.ylabel("Value")
plt.title("Delivery vs Backlog Analysis")
plt.legend()

plt.show()