"""Step 1 - Reproject building footprints (UTM 28N) to Web Mercator for display over OpenStreetMap."""
import geopandas as gpd
from config import BUILDINGS, OUT

gdf = gpd.read_file(BUILDINGS)
if gdf.crs is None:
    gdf = gdf.set_crs(epsg=32628)
print("Input CRS:", gdf.crs)

gdf_3857 = gdf.to_crs(epsg=3857)
print("Bounds (EPSG:3857):", gdf_3857.total_bounds)
gdf_3857.to_file(OUT / "Pikine_Buildings_Solar_3857.gpkg", driver="GPKG")
print("Buildings:", len(gdf), "| Total kWp:", round(gdf["Solar_kWp"].sum()))
