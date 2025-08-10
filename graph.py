# generate_figures.py
# Produces:
#   fig_rq1_rf_importance.png
#   fig_rq2_roi_top10_all.png
#   fig_rq2_roi_top_vancouver.png
#   fig_rq2_roi_top_victoria.png
#   fig_rq3_license_share_prepost.png
#   fig_rq3_avg_price_prepost.png

import os
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Config: input/output paths
# ----------------------------
DATA_DIR = "./cleaned_data"  # change if your CSVs are in another folder
OUT_DIR = "./reports/figures"

PATH_TOP_PREDICTORS = os.path.join(DATA_DIR, "top_predictors_rq1.csv")
PATH_ROI_FULL       = os.path.join(DATA_DIR, "roi_merged_full.csv")
PATH_DID_SUMMARY    = os.path.join(DATA_DIR, "did_rq3_summary.csv")  # legacy (unused)
PATH_RQ3_PRICE_SUM  = os.path.join(DATA_DIR, "rq3_price_summary.csv")
PATH_RQ3_LIC_SHARE  = os.path.join(DATA_DIR, "rq3_license_share.csv")

# ----------------------------
# Helpers
# ----------------------------
def ensure_dir(path: str):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def save_current_fig(path: str):
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()

# ----------------------------
# Bar label helpers
# ----------------------------
def _label_bars(ax, bars, *, orientation: str = "v", fmt=lambda v: f"{v:.2f}", offset=3, fontsize=9):
    """Attach a text label to each bar in *bars* (vertical or horizontal).
    orientation: 'v' for vertical bars (bar), 'h' for horizontal bars (barh).
    fmt: function to format numeric value into string.
    offset: pixel offset from the bar end.
    """
    ax.figure.canvas.draw_idle()  # ensure transforms are ready
    for rect in bars:
        if orientation == "v":
            height = rect.get_height()
            x = rect.get_x() + rect.get_width() / 2
            y = rect.get_y() + height
            ax.annotate(
                fmt(height),
                xy=(x, y),
                xytext=(0, offset),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=fontsize,
                rotation=0,
            )
        else:
            width = rect.get_width()
            x = rect.get_x() + width
            y = rect.get_y() + rect.get_height() / 2
            ax.annotate(
                fmt(width),
                xy=(x, y),
                xytext=(offset, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=fontsize,
                rotation=0,
            )

# ----------------------------
# Figure 1: RF Top-10 importance
# ----------------------------
def plot_rf_importance(top_predictors_csv: str, out_path: str):
    tp = pd.read_csv(top_predictors_csv)
    if not {"model", "rank", "feature", "importance"}.issubset(tp.columns):
        raise ValueError("top_predictors_rq1.csv must have columns: model, rank, feature, importance")

    rf = (
        tp.loc[tp["model"].astype(str).str.lower() == "randomforest"]
        .sort_values("rank")
        .head(10)
    )

    fig, ax = plt.subplots()
    bars = ax.barh(rf["feature"], rf["importance"])
    ax.invert_yaxis()
    ax.set_xlabel("Importance")
    ax.set_title("RQ1: Random Forest Top-10 Predictors of Annual Revenue")
    _label_bars(ax, bars, orientation="h", fmt=lambda v: f"{v:.3f}")
    save_current_fig(out_path)

# ----------------------------
# Figure 2: ROI Top-10 overall
# ----------------------------
def plot_roi_top10_all(roi_csv: str, out_path: str):
    df = pd.read_csv(roi_csv)
    required = {"city", "neighbourhood", "roi_ratio"}
    if not required.issubset(df.columns):
        raise ValueError("roi_merged_full.csv must have columns: city, neighbourhood, roi_ratio")

    # Collapse potential duplicates per (city, neighbourhood)
    df_agg = (
        df.groupby(["city", "neighbourhood"], as_index=False)["roi_ratio"].mean()
    )
    top = df_agg.sort_values("roi_ratio", ascending=False).head(10).copy()
    labels = top["neighbourhood"] + " (" + top["city"].astype(str) + ")"

    fig, ax = plt.subplots()
    bars = ax.barh(labels, top["roi_ratio"])
    ax.invert_yaxis()
    ax.set_xlabel("ROI (Revenue / Price)")
    ax.set_title("RQ2: Top-10 Neighbourhoods by ROI (All)")
    _label_bars(ax, bars, orientation="h", fmt=lambda v: f"{v:.4f}")
    save_current_fig(out_path)

# ----------------------------
# Figure 3–4: ROI Top by city
# ----------------------------
def plot_roi_top_by_city(roi_csv: str, city: str, out_path: str, top_n: int = 10):
    df = pd.read_csv(roi_csv)
    required = {"city", "neighbourhood", "roi_ratio"}
    if not required.issubset(df.columns):
        raise ValueError("roi_merged_full.csv must have columns: city, neighbourhood, roi_ratio")

    # Filter city then collapse duplicates per neighbourhood
    sub = df.loc[df["city"].astype(str).str.lower() == city.lower()]
    sub = (
        sub.groupby("neighbourhood", as_index=False)["roi_ratio"].mean()
        .sort_values("roi_ratio", ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots()
    bars = ax.barh(sub["neighbourhood"], sub["roi_ratio"])
    ax.invert_yaxis()
    ax.set_xlabel("ROI (Revenue / Price)")
    ax.set_title(f"RQ2: Top Neighbourhoods by ROI — {city}")
    _label_bars(ax, bars, orientation="h", fmt=lambda v: f"{v:.4f}")
    save_current_fig(out_path)

# ----------------------------
# RQ3 Figures: Avg Price and License Share (Pre vs Post) by City
# ----------------------------
def plot_rq3_avg_price(price_summary_csv: str, out_path: str):
    df = pd.read_csv(price_summary_csv)
    required = {"City", "Period", "mean_price"}
    if not required.issubset(df.columns):
        raise ValueError("rq3_price_summary.csv must have columns: City, Period, mean_price (plus std_price, n)")

    # enforce period order
    period_order = ["Pre", "Post"]
    cities = list(df["City"].dropna().unique())
    cities.sort()

    # pivot to matrix (City x Period)
    pivot = df.pivot_table(index="City", columns="Period", values="mean_price", aggfunc="mean")
    pivot = pivot.reindex(index=cities, columns=period_order)

    x = range(len(cities))
    width = 0.38

    fig, ax = plt.subplots()
    pre_vals = pivot["Pre"].values if "Pre" in pivot.columns else [0]*len(cities)
    post_vals = pivot["Post"].values if "Post" in pivot.columns else [0]*len(cities)

    b1 = ax.bar([i - width/2 for i in x], pre_vals, width, label="Pre", color="#9aa0a6")
    b2 = ax.bar([i + width/2 for i in x], post_vals, width, label="Post", color="#1a73e8")

    ax.set_xticks(list(x))
    ax.set_xticklabels(cities, rotation=0)
    ax.set_ylabel("Average Price ($)")
    ax.set_title("RQ3: Average Nightly Price — Pre vs Post")
    ax.legend()

    _label_bars(ax, b1, orientation="v", fmt=lambda v: f"${v:.0f}")
    _label_bars(ax, b2, orientation="v", fmt=lambda v: f"${v:.0f}")

    save_current_fig(out_path)


def plot_rq3_license_share(share_csv: str, out_path: str):
    df = pd.read_csv(share_csv)
    required = {"City", "Period", "licensed_share"}
    if not required.issubset(df.columns):
        raise ValueError("rq3_license_share.csv must have columns: City, Period, licensed_share (plus licensed_n, n)")

    # enforce period order
    period_order = ["Pre", "Post"]
    cities = list(df["City"].dropna().unique())
    cities.sort()

    pivot = df.pivot_table(index="City", columns="Period", values="licensed_share", aggfunc="mean")
    pivot = pivot.reindex(index=cities, columns=period_order)

    x = range(len(cities))
    width = 0.38

    fig, ax = plt.subplots()
    pre_vals = (pivot["Pre"].values if "Pre" in pivot.columns else [0]*len(cities)) * 100
    post_vals = (pivot["Post"].values if "Post" in pivot.columns else [0]*len(cities)) * 100

    b1 = ax.bar([i - width/2 for i in x], pre_vals, width, label="Pre", color="#9aa0a6")
    b2 = ax.bar([i + width/2 for i in x], post_vals, width, label="Post", color="#ea4335")

    ax.set_xticks(list(x))
    ax.set_xticklabels(cities, rotation=0)
    ax.set_ylabel("Licensed Share (%)")
    ax.set_ylim(0, max(100, float(max(list(pre_vals)+list(post_vals)))*1.15 if len(cities)>0 else 100))
    ax.set_title("RQ3: Licensed Listings Share — Pre vs Post")
    ax.legend()

    _label_bars(ax, b1, orientation="v", fmt=lambda v: f"{v:.1f}%")
    _label_bars(ax, b2, orientation="v", fmt=lambda v: f"{v:.1f}%")

    save_current_fig(out_path)


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    ensure_dir(OUT_DIR)

    # 1) RF importance
    plot_rf_importance(
        PATH_TOP_PREDICTORS,
        os.path.join(OUT_DIR, "fig_rq1_rf_importance.png")
    )

    # 2) ROI Top-10 overall
    plot_roi_top10_all(
        PATH_ROI_FULL,
        os.path.join(OUT_DIR, "fig_rq2_roi_top10_all.png")
    )

    # 3) ROI Top Vancouver
    plot_roi_top_by_city(
        PATH_ROI_FULL, "Vancouver",
        os.path.join(OUT_DIR, "fig_rq2_roi_top_vancouver.png")
    )

    # 4) ROI Top Victoria
    plot_roi_top_by_city(
        PATH_ROI_FULL, "Victoria",
        os.path.join(OUT_DIR, "fig_rq2_roi_top_victoria.png")
    )

    # 5) RQ3: Average price (Pre vs Post) by City
    if os.path.exists(PATH_RQ3_PRICE_SUM):
        plot_rq3_avg_price(
            PATH_RQ3_PRICE_SUM,
            os.path.join(OUT_DIR, "fig_rq3_avg_price_prepost.png")
        )
    else:
        print(f"Warning: {PATH_RQ3_PRICE_SUM} not found; skipping RQ3 avg price figure.")

    # 6) RQ3: Licensed share (Pre vs Post) by City
    if os.path.exists(PATH_RQ3_LIC_SHARE):
        plot_rq3_license_share(
            PATH_RQ3_LIC_SHARE,
            os.path.join(OUT_DIR, "fig_rq3_license_share_prepost.png")
        )
    else:
        print(f"Warning: {PATH_RQ3_LIC_SHARE} not found; skipping RQ3 license share figure.")

    print("All figures saved.")
