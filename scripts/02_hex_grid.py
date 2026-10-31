"""Step 2 - Build a hexagonal grid and sum rooftop kWp per hexagon."""
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
from config import BUILDINGS, HEX

SIZE = 250  # hexagon circumradius in metres

b = gpd.read_file(BUILDINGS)
if b.crs is None:
    b = b.set_crs(epsg=32628)
b = b.to_crs(32628)


def hex_grid(bounds, size=SIZE):
    xmin, ymin, xmax, ymax = bounds
    w, h = size * 2, np.sqrt(3) * size
    hexes = []
    for i, x in enumerate(np.arange(xmin, xmax + w, 1.5 * size)):
        for y in np.arange(ymin - h, ymax + h, h):
            y0 = y + (h / 2 if i % 2 else 0)
            hexes.append(Polygon([(x + size * np.cos(a), y0 + size * np.sin(a))
                                  for a in np.radians(range(0, 360, 60))]))
    return gpd.GeoDataFrame(geometry=hexes, crs=32628)


grid = hex_grid(b.total_bounds)
pts = b.copy()
pts["geometry"] = b.centroid
j = gpd.sjoin(pts, grid, predicate="within")
grid["kWp"] = j.groupby("index_right")["Solar_kWp"].sum()
grid = grid[grid["kWp"] > 0].reset_index(drop=True)

grid.to_file(HEX, driver="GPKG")
grid.to_crs(3857).to_file(str(HEX).replace(".gpkg", "_3857.gpkg"), driver="GPKG")
print("Hexagons with buildings:", len(grid))
print("Total kWp:", round(grid["kWp"].sum()))
