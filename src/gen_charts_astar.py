import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# graph_names = ["random512-10-0", "arena","maze512-1-0","16room_002"]
# graph_names = ["Map18","random512-10-0", "arena","maze512-1-0","16room_002"]
graph_names = ["Map18"]

# Paths
csv_dir = "./results/csv/"
save_path = f"./results/img/{graph_names[0]}/"

if len(graph_names) > 1:
    save_path = "./results/img/combined/"
if len(graph_names) > 1 and "Map18" in graph_names:
    save_path = "./results/img/combinedWithMap18/"

os.makedirs(save_path, exist_ok=True)

# Load all DataFrames first to determine min length
df_sources = {}
min_len = float("inf")

for graph_name in graph_names:
    csv_file = os.path.join(csv_dir, f"{graph_name}_evaluation.csv")
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df["graph_name"] = graph_name
        df_sources[graph_name] = df
        if len(df) < min_len:
            min_len = len(df)
    else:
        print(f"❌ File not found: {csv_file}")

if not df_sources:
    raise FileNotFoundError("No valid CSVs loaded. Check graph_names and paths.")

# Take equal number of rows from each DataFrame
df = pd.concat(
    [df.head(min_len) for df in df_sources.values()],
    ignore_index=True
)

# Normalize column names
df.columns = [col.lower() for col in df.columns]

# Set seaborn style
sns.set(style="whitegrid")

# -------------------------------
# A. Mean & Median Time per Heuristic
# -------------------------------
time_stats = df.groupby("heuristic")["time_sec"].agg(["mean", "median"]).reset_index()
time_melted = pd.melt(time_stats, id_vars="heuristic", var_name="stat", value_name="time")

plt.figure(figsize=(8, 6))
sns.barplot(data=time_melted, x="heuristic", y="time", hue="stat", palette="muted")
plt.title("Mean vs Median Time per Heuristic")
plt.ylabel("Time (seconds)")
plt.xlabel("Heuristic")
for container in plt.gca().containers:
    plt.bar_label(container, fmt="%.4f", padding=3)
plt.legend(title="Statistic")
plt.tight_layout()
plt.savefig(save_path + "mean_median_time_per_heuristic.png")
plt.close()

# ----------------------------------
# B. Mean & Median Visited Nodes
# ----------------------------------
visited_stats = df.groupby("heuristic")["visited_nodes"].agg(["mean", "median"]).reset_index()
visited_melted = pd.melt(visited_stats, id_vars="heuristic", var_name="stat", value_name="visited_nodes")

plt.figure(figsize=(8, 6))
sns.barplot(data=visited_melted, x="heuristic", y="visited_nodes", hue="stat", palette="pastel")
plt.title("Mean vs Median Visited Nodes per Heuristic")
plt.ylabel("Visited Nodes")
plt.xlabel("Heuristic")
for container in plt.gca().containers:
    plt.bar_label(container, fmt="%.0f", padding=3)
plt.legend(title="Statistic")
plt.tight_layout()
plt.savefig(save_path + "mean_median_visited_nodes.png")
plt.close()

# -----------------------------
# C. Mean & Median Path Length
# -----------------------------
path_stats = df.groupby("heuristic")["path_length"].agg(["mean", "median"]).reset_index()
path_melted = pd.melt(path_stats, id_vars="heuristic", var_name="stat", value_name="path_length")

plt.figure(figsize=(8, 6))
sns.barplot(data=path_melted, x="heuristic", y="path_length", hue="stat", palette="deep")
plt.title("Mean vs Median Path Length per Heuristic")
plt.ylabel("Path Length")
plt.xlabel("Heuristic")
for container in plt.gca().containers:
    plt.bar_label(container, fmt="%.2f", padding=3)
plt.legend(title="Statistic")
y_max = path_melted["path_length"].max()
plt.ylim(0, y_max * 1.5)
plt.tight_layout()
plt.savefig(save_path + "mean_median_path_length.png")
plt.close()

# -----------------------------
# D. Total Cost vs. Expected Cost by Case
# -----------------------------
df_cost = df.dropna(subset=["expected_cost", "actual_cost"])
df_cost_melted = pd.melt(
    df_cost,
    id_vars=["case_id", "heuristic"],
    value_vars=["expected_cost", "actual_cost"],
    var_name="cost_type",
    value_name="cost"
)

plt.figure(figsize=(14, 6))
sns.barplot(
    data=df_cost_melted,
    x="case_id",
    y="cost",
    hue="cost_type",
    palette="Set2",
    ci=None
)

xticks = plt.gca().get_xticks()
xticklabels = plt.gca().get_xticklabels()
plt.xticks(ticks=xticks[::3], labels=[label.get_text() for label in xticklabels[::3]], rotation=45)

plt.title("Expected vs Actual Cost by Case (Bar Chart)")
plt.ylabel("Cost")
plt.xlabel("Case ID")
plt.legend(title="Cost Type")
plt.tight_layout()
plt.savefig(save_path + "cost_comparison_bar_chart.png")
plt.close()

# -----------------------------
# E. Time with Error Bars
# -----------------------------
plt.figure(figsize=(8, 6))
sns.barplot(data=df, x="heuristic", y="time_sec", ci="sd", estimator="mean", palette="dark")
plt.title("Time per Heuristic with Standard Deviation")
plt.ylabel("Time (seconds)")
plt.xlabel("Heuristic")
for container in plt.gca().containers:
    plt.bar_label(container, fmt="%.4f", padding=3)
plt.tight_layout()
plt.savefig(save_path + "time_with_error_bars.png")
plt.close()

# -----------------------------
# F. Avg Expected vs Actual Cost per Heuristic
# -----------------------------
df_cost_grouped = df_cost.groupby("heuristic")[["expected_cost", "actual_cost"]].mean().reset_index()
grouped_melted = pd.melt(
    df_cost_grouped,
    id_vars="heuristic",
    value_vars=["expected_cost", "actual_cost"],
    var_name="cost_type",
    value_name="avg_cost"
)

plt.figure(figsize=(8, 6))
sns.barplot(
    data=grouped_melted,
    x="heuristic",
    y="avg_cost",
    hue="cost_type",
    palette="Set2"
)
plt.title("Average Expected vs Actual Cost per Heuristic")
plt.ylabel("Average Cost")
plt.xlabel("Heuristic")
for container in plt.gca().containers:
    plt.bar_label(container, fmt="%.3f", padding=3)
y_max = grouped_melted["avg_cost"].max()
plt.ylim(0, y_max * 1.5)
plt.tight_layout()
plt.savefig(save_path + "avg_cost_per_heuristic.png")
plt.close()

print("✅ All graphs with mean & median successfully generated and saved.")