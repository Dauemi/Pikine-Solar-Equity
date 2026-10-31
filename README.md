# Inclusive Rooftop Solar in Pikine, Dakar

Spatial multi-criteria analysis of where rooftop solar could most benefit residents of
Pikine (Dakar, Senegal). Part of a group project for an Energy Transition Policies module
on inclusive solar policy for Dakar's suburbs; this repository holds the spatial analysis.

![Equity map](figures/Pikine_Equity_Map.png)

## Key results

- **9,315 buildings** with about **203 MWp** of rooftop PV potential (about 0.76 kWp per resident)
- **4 areas** are top-10 priorities in more than 80% of 10,000 random weighting scenarios
- The most informal neighbourhoods (Dalifort, A1/rail corridor) rank **#1 under need-led weights**
  but around **#20 under potential-led weights**
- The ranking is stable to the solar weight but highly sensitive to the vulnerability weight:
  **who benefits is a policy choice, not a technical one**

![Sensitivity chart](figures/sensitivity_chart.png)

## Method

1. Rooftop PV capacity per building from OpenStreetMap footprints
2. 250 m hexagon grid; rooftop kWp summed per hexagon
3. Population from WorldPop 2026 (100 m, constrained) summed per hexagon
4. Criteria (rank-normalised, 1 = higher priority):

   | Criterion | Indicator | Direction |
   |---|---|---|
   | Solar potential | total kWp | higher |
   | Beneficiaries | population density | higher |
   | Vulnerability | median building footprint (informality proxy) | smaller |
   | Self-sufficiency | kWp per resident | higher |

5. Weighted sum under three scenarios (weights: solar / population / vulnerability / self-sufficiency):
   - Equal: 25 / 25 / 25 / 25
   - Need-focused: 15 / 30 / 40 / 15
   - Tech-focused: 40 / 20 / 15 / 25
6. Sensitivity: one-at-a-time weights, Monte Carlo (10,000 Dirichlet weightings),
   leave-one-out, rank vs min-max normalisation

Only residential hexagons (20 or more buildings) enter the MCDA (43 of 64).

## Repository structure

```
data/      input data (see Data below)
scripts/   analysis scripts, run in numbered order
outputs/   generated GeoPackages and CSV tables
figures/   maps and charts
qgis/      QGIS project and layer style
```

## How to run

```bash
pip install -r requirements.txt
cd scripts
python 01_reproject.py
python 02_hex_grid.py
python 03_population.py
python 04_vulnerability.py
python 05_mcda.py
python 06_sensitivity.py
```

All paths are relative (`scripts/config.py`), so the scripts run on any computer.

## Data

- **Buildings:** © OpenStreetMap contributors, available under the
  [Open Database Licence (ODbL)](https://www.openstreetmap.org/copyright)
- **Population:** WorldPop, Senegal 2026, 100 m constrained (CC BY 4.0).
  Not included because of file size: download `sen_pop_2026_CN_100m_R2025A_v1.tif` from
  [hub.worldpop.org](https://hub.worldpop.org) and place it in `data/`.

## Limitations

- OpenStreetMap building coverage is incomplete, so rooftop potential is likely underestimated.
- Median building size is a proxy for informality, not a measured poverty rate.
- Roof orientation, shading, structural capacity and grid constraints are not modelled.
- Criterion weights are illustrative scenarios, not derived from stakeholder input.

## Tools

QGIS, Python (GeoPandas, rasterstats, NumPy, pandas, Matplotlib)
