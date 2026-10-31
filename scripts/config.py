"""Shared paths for all scripts. Works on any computer once the repo is cloned."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"        # inputs (buildings, WorldPop raster)
OUT = ROOT / "outputs"      # generated layers and tables
FIG = ROOT / "figures"      # charts and exported maps

BUILDINGS = DATA / "Pikine_Buildings_Solar_32628.gpkg"
WORLDPOP = DATA / "sen_pop_2026_CN_100m_R2025A_v1.tif"
HEX = OUT / "Pikine_hex_250m.gpkg"

for d in (OUT, FIG):
    d.mkdir(exist_ok=True)
