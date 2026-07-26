# 📐 QGIS Batch Chainage Extraction

Automated pipeline for projecting survey points onto road centerlines and extracting chainage values in bulk using QGIS.

## 📋 Overview

This tool processes survey point data from GeoPackage (`.gpkg`) files, projects them onto a road centerline, and outputs chainage (station) values as CSV. Built for civil engineering and surveying workflows.

## ⚙️ How It Works

1. Loads survey points from multiple GPKG files in a project folder
2. Projects each point onto the nearest road centerline segment
3. Calculates chainage (distance along the centerline)
4. Outputs structured CSV with easting, northing, elevation, and chainage

## 🚀 Quick Start

### Prerequisites
- **QGIS LTR 3.44+** installed at `C:\OSGeo4W` (Windows only)
- Survey data in GPKG format
- Road centerline layer with sectioned segments

### Usage

1. **Drag your project folder** onto `run.bat`
2. **First-time setup:** You'll be prompted for:
   - GPKG data folder location
   - Road centerline file
   - Field names (easting, northing, elevation)
   - Base chainage for each section
3. **Subsequent runs:** Config is saved — just drag & run

### Output

```
output_chainage/
└── {project_name}/
    └── chainage_results.csv
```

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![QGIS](https://img.shields.io/badge/QGIS-589632?style=flat-square&logo=qgis&logoColor=white)
![Batch](https://img.shields.io/badge/Windows_Batch-4D4D4D?style=flat-square&logo=windows&logoColor=white)

## 📁 Project Structure

```
qgis-batch-extraction/
├── run.bat              # One-click launcher
├── chainage.py          # Core chainage computation
├── config_manager.py    # Configuration persistence
├── requirements.txt     # Python dependencies
└── README.md
```

## 📝 Notes

- Tested with **NH01** and **NH02** highway projects
- Default CRS: **UTM 45N (EPSG:32645)**
- Road layer requires segments split by a field (default: `"layer"`)

## 📄 License

MIT © 2026 Praansu Karmacharya
