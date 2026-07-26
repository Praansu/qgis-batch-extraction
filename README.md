# QGIS Batch Chainage Extraction

Automated tool for projecting survey points onto road centerlines and extracting chainage values. Built for civil engineering workflows — think highway surveying, not web apps.

## The problem this solves

Surveyors collect point data along a road. These points need to be projected onto the road centerline and converted to chainage (station) values. Doing this manually for hundreds of points is tedious. This script batch-processes the whole thing.

## How it works

1. Reads survey points from GeoPackage (.gpkg) files
2. Projects each point onto the nearest road centerline segment
3. Calculates chainage (distance along the centerline)
4. Outputs everything as structured CSV (easting, northing, elevation, chainage)

## Usage

**Prerequisites:** QGIS LTR 3.44+ at `C:\OSGeo4W` (Windows)

1. Drag your project folder onto `run.bat`
2. First run: set up paths (GPKG folder, road centerline, field names, base chainage)
3. Subsequent runs: config is saved, just drag & run

**Output:** `output_chainage/{project_name}/chainage_results.csv`

## Project layout

```
run.bat              — one-click launcher
chainage.py          — core computation
config_manager.py    — saves your settings
requirements.txt     — Python dependencies
```

## Tested on

NH01 and NH02 highway projects. Default CRS: UTM 45N (EPSG:32645).

## Tech

Python, QGIS, Windows Batch

## License

MIT
