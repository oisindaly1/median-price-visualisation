Oisín Daly - 24374553 - MIS20080
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Panel Project - 3D Visualisation of Median Price of Residential Dwellings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

This project requires the following libraries in order to be able to run the final version of the code:
pandas - Used for data manipulation 
matplotlib  - Used for initial visualisation and creating of bars variable
numpy - Used for numeric operations
geopandas - Used for importing the map of Ireland and reading the GeoJSON
plotly - Used for final 3D Visualisation
shapely - Used to efficiently handle Polygons and MultiPolygons

Install all libraries by using:

pip install pandas matplotlib numpy geopandas plotly shapely

------------------------------------------------------------------------------------------------------------------------

This project effectively visualises the inflation in housing prices per region in the housing market from 2010 to 2025, using Plotly as a 3D Graphing tool, and allows the user to use the slider in order to interact with the graph.

------------------------------------------------------------------------------------------------------------------------

The Data can be obtained by the following links or the data commited to GitHub already.

'df'/'data.csv' ->  Market-based Household Purchases of Residential Dwellings -> 'https://data.cso.ie/table/HPM03'
'coords'/'coordinates.csv' -> Co-ordinates for regions - where bars are drawn -> 'https://data-osi.opendata.arcgis.com/datasets/osi::local-authorities-national-statutory-boundaries-ungeneralised-2024/explore'
'counties'/GeoJSON file for Outline -> 'https://data-osi.opendata.arcgis.com/datasets/osi::administrative-areas-national-statutory-boundaries-2019/about'
