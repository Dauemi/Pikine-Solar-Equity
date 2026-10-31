"""Step 6 - Sensitivity analysis of the equity MCDA.

Tests: one-at-a-time weights, Monte Carlo (10,000 random weightings),
leave-one-out, and rank vs min-max normalisation.
"""
import geopandas as gpd
import numpy as np
import pandas as pd
from config import HEX, OUT, FIG

grid = gpd.read_file(HEX)
g = grid[grid["n_bldg"] >= 20].copy()
print(f"Hexagons analysed: {len(g)} of {len(grid)}")

names = ["solar", "pop", "vuln", "self"]
labels = ["Solar kWp", "Population density", "Vulnerability", "kWp per capita"]


def normalise(df, method="rank"):
    """Scale criteria to 0-1, where 1 = higher priority."""
    raw = pd.DataFrame({
        "solar": df["kWp"],
        "pop":   df["pop_density"],
        "vuln": -df["median_area"],      # smaller buildings = more vulnerable
        "self":  df["kWp_per_cap"],
    })
    if method == "rank":
        return raw.rank(pct=True)
    return (raw - raw.min()) / (raw.max() - raw.min())


def top10(scores):
    return set(scores.nlargest(10).index)


N = normalise(g)
base_w = np.array([0.25] * 4)
base = N @ base_w
base_top = top10(base)

# 1. One-at-a-time
rows = []
for i, c in enumerate(names):
    for wi in np.arange(0.05, 0.71, 0.05):
        w = np.full(4, (1 - wi) / 3)
        w[i] = wi
        s = N @ w
        rows.append({"criterion": c, "weight": round(wi, 2),
                     "top10_overlap": len(top10(s) & base_top),
                     "spearman": round(s.corr(base, method="spearman"), 2)})
oat = pd.DataFrame(rows)
print("\n1. ONE-AT-A-TIME (top-10 overlap with equal weights)")
print(oat.pivot(index="weight", columns="criterion", values="top10_overlap"))

# 2. Monte Carlo
rng = np.random.default_rng(42)
W = rng.dirichlet(np.ones(4), size=10000)
S = N.values @ W.T
ranks = (-S).argsort(axis=0).argsort(axis=0) + 1
g["top10_freq"] = (ranks <= 10).mean(axis=1).round(3)
g["median_rank"] = np.median(ranks, axis=1)
g["rank_p5"] = np.percentile(ranks, 5, axis=1)
g["rank_p95"] = np.percentile(ranks, 95, axis=1)
g["stability"] = pd.cut(g["top10_freq"], [-0.01, 0.2, 0.5, 0.8, 1.0],
                        labels=["Rarely top 10", "Weight-dependent", "Robust", "Very robust"])

mc_cols = ["top10_freq", "median_rank", "rank_p5", "rank_p95",
           "kWp", "pop_density", "median_area", "stability"]
mc = g[g["top10_freq"] >= 0.2].sort_values("top10_freq", ascending=False)[mc_cols]
print("\n2. MONTE CARLO: hexagons in the top 10 in at least 20% of runs")
print(mc.round(2))
print("\nStability classes:")
print(g["stability"].value_counts())

# 3. Leave-one-out
print("\n3. LEAVE-ONE-OUT (criterion removed -> top-10 overlap, Spearman)")
for i, c in enumerate(names):
    w = np.full(4, 1 / 3)
    w[i] = 0
    s = N @ w
    print(f"  without {c:5s}: {len(top10(s) & base_top)}/10, "
          f"rho = {s.corr(base, method='spearman'):.2f}")

# 4. Normalisation method
s_mm = normalise(g, "minmax") @ base_w
print(f"\n4. MIN-MAX vs RANK: {len(top10(s_mm) & base_top)}/10 overlap, "
      f"rho = {s_mm.corr(base, method='spearman'):.2f}")

# Save
oat.to_csv(OUT / "sensitivity_oat.csv", index=False)
mc.to_csv(OUT / "sensitivity_montecarlo.csv")
out = grid.join(g[["top10_freq", "median_rank", "rank_p5", "rank_p95", "stability"]])
out["stability"] = out["stability"].astype(str).replace("nan", None)
out.to_crs(3857).to_file(OUT / "Pikine_sensitivity_3857.gpkg", driver="GPKG")

# Chart
try:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    for c, lab in zip(names, labels):
        d = oat[oat["criterion"] == c]
        ax.plot(d["weight"] * 100, d["top10_overlap"], marker="o", label=lab)
    ax.axvline(25, color="grey", ls="--", lw=1)
    ax.text(25.5, 0.4, "Equal weights (baseline)", color="grey", fontsize=9)
    ax.set(xlabel="Weight of criterion (%)", ylabel="Top-10 areas unchanged (of 10)",
           title="Sensitivity of Pikine equity ranking to criterion weights", ylim=(0, 10.5))
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "sensitivity_chart.png", dpi=300)
    print("\nChart saved: figures/sensitivity_chart.png")
except ImportError:
    print("\n(Install matplotlib for the chart: pip install matplotlib)")
