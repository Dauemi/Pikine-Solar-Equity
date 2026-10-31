"""Step 5 - Equity MCDA: rank-normalised weighted sum under three weighting scenarios."""
import geopandas as gpd
from config import HEX, OUT

grid = gpd.read_file(HEX)

# Residential hexagons only (>= 20 buildings)
grid["residential"] = grid["n_bldg"] >= 20
g = grid[grid["residential"]].copy()
print("Hexagons in MCDA:", len(g), "of", len(grid))

# Normalise 0-1 by rank (robust to outliers); 1 = higher priority
g["n_solar"] = g["kWp"].rank(pct=True)
g["n_pop"] = g["pop_density"].rank(pct=True)
g["n_vuln"] = g["median_area"].rank(pct=True, ascending=False)   # smaller buildings = more vulnerable
g["n_self"] = g["kWp_per_cap"].rank(pct=True)

crit = ["n_solar", "n_pop", "n_vuln", "n_self"]
scenarios = {                      # solar, pop, vuln, self
    "equal":        [0.25, 0.25, 0.25, 0.25],
    "need_focused": [0.15, 0.30, 0.40, 0.15],
    "tech_focused": [0.40, 0.20, 0.15, 0.25],
}
for name, w in scenarios.items():
    g["score_" + name] = sum(wi * g[c] for wi, c in zip(w, crit))

# Priority class 1 (lowest) to 5 (highest) from the equal-weight score
g["priority"] = (g["score_equal"].rank(pct=True) * 5).clip(upper=4.999).astype(int) + 1

# Top-10 comparison across scenarios
top = {n: set(g.nlargest(10, "score_" + n).index) for n in scenarios}
eq, nd, tc = top["equal"], top["need_focused"], top["tech_focused"]
print("Top-10 overlap, equal vs need-focused:", len(eq & nd), "/10")
print("Top-10 overlap, equal vs tech-focused:", len(eq & tc), "/10")
print(g[["score_equal", "score_need_focused", "score_tech_focused"]]
      .corr(method="spearman").round(2))

core = eq & nd & tc
need_only = nd - eq - tc
tech_only = (eq | tc) - nd


def label(i):
    if i in core:
        return "Robust priority"
    if i in (eq & nd) - tc:
        return "Priority unless tech-weighted"
    if i in need_only:
        return "Priority only if need-weighted"
    if i in tech_only:
        return "Drops out when need-weighted"
    return None


score_cols = [c for c in g.columns if c.startswith("score_")]
out = grid.join(g[crit + score_cols + ["priority"]])
out["top10_group"] = [label(i) for i in out.index]

print(out["top10_group"].value_counts())
print(out.loc[out["top10_group"].notna(),
              ["top10_group", "kWp", "pop_density", "median_area"]].round(0))

out.to_file(OUT / "Pikine_equity_mcda.gpkg", driver="GPKG")
out.to_crs(3857).to_file(OUT / "Pikine_equity_mcda_3857.gpkg", driver="GPKG")
