"""Step 3 - Add WorldPop 2026 population and density to each hexagon."""
import geopandas as gpd
from rasterstats import zonal_stats
from config import HEX, WORLDPOP

grid = gpd.read_file(HEX)                       # EPSG:32628
grid_4326 = grid.to_crs(4326)                   # WorldPop is EPSG:4326
stats = zonal_stats(grid_4326, str(WORLDPOP), stats=["sum"],
                    all_touched=False, nodata=-99999)
grid["pop"] = [s["sum"] or 0 for s in stats]
grid["area_km2"] = grid.geometry.area / 1e6
grid["pop_density"] = grid["pop"] / grid["area_km2"]

print(grid[["kWp", "pop", "pop_density"]].describe().round(0))
print("Total population in hexagons:", round(grid["pop"].sum()))

grid.to_file(HEX, driver="GPKG")
grid.to_crs(3857).to_file(str(HEX).replace(".gpkg", "_3857.gpkg"), driver="GPKG")
