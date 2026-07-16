# chainage extraction

takes survey points from gpkg files and projects them onto a road centerline to get chainage values. outputs csv.

## setup

- qgis ltr 3.44+ installed at C:\OSGeo4W
- windows only (uses .bat)

## usage

drag your project folder onto run.bat

first time it will ask for:
- which folder has the gpkg files
- which file is the road centerline
- what field names to use (easting, northing, elevation)
- base chainage for each section

after that it saves a config file in your project folder so you can just drag and run again.

output goes to output_chainage\projectname\

## notes

- tested with nh01 and nh02 projects
- expects utm 45n coordinates by default (epsg:32645)
- road layer needs to have sections split by a field (default "layer")
