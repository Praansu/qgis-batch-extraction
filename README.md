# Chainage Extraction Tool

Takes survey point GPKG files and projects them onto a road centerline to compute chainage values. Outputs CSV files with chainage, easting, northing and elevation.

## Requirements

- QGIS LTR 3.44+ installed at C:\OSGeo4W
- Windows (uses .bat launcher)

## How to use

1. Drag your project folder onto run.bat
2. First time setup will ask for:
   - Which folder has the GPKG survey files
   - Which file is the road centerline
   - Base chainage for each section
3. Output goes to output_chainage\[project name]\

## Project folder structure

Any structure works. On first run the tool scans everything and shows you what it found — just pick the right folders.

Config gets saved in your project folder as chainage_config.json. Future runs skip setup.
