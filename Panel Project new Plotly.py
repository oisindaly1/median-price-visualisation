import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import plotly.graph_objects as go


df = pd.read_csv("data.csv")
coords = pd.read_csv("coordinates.csv")
counties = gpd.read_file("Administrative_Areas___OSi_National_Statutory_Boundaries_-978765968693620525.geojson")

counties = counties.to_crs(epsg=2157)

print("counties CRS:", counties.crs)
print("coords sample", coords[['CENTROID_X', 'CENTROID_Y']].head())
'''
Median Price Manipulation
Col 1 -  median price
Col 2 - Change data type
Col 3 - only all dwelling status
Col 4 - executions
col 5 - get rid of 'all'
Col 6 - all buyer types
'''

df_median = df[(df["Statistic Label"] == "Median Price") & 
               (df["RPPI Region"] != "All") & 
               (df["Stamp Duty Event"] == "Executions") &
               (df["Dwelling Status"] == "All Dwelling Statuses") & 
               (df["Type of Buyer"] == "All Buyer Types")].copy()

df_median["Month"] = pd.to_datetime(df_median["Month"], format = "%Y %B")

region_data = {
    region: group.set_index("Month")["VALUE"]
    for region, group in df_median.groupby("RPPI Region")
}
dates = sorted(set(df_median["Month"]))
regions = sorted(set(coords["PROPERTY DATA NAME"]))

period = dates[0]
df_month = df_median[df_median["Month"] == period]


origin_x = coords["CENTROID_X"].mean()
origin_y = coords["CENTROID_Y"].mean()

coords["x_scaled"] = (coords["CENTROID_X"] - origin_x)/1e4
coords["y_scaled"] = (coords["CENTROID_Y"] - origin_y)/1e4

region_xy = {}

for r in regions:
    x = coords.loc[coords["PROPERTY DATA NAME"] == r, "x_scaled"].values[0]
    y = coords.loc[coords["PROPERTY DATA NAME"] == r, "y_scaled"].values[0]
    region_xy[r] = (x,y)

xpos = np.array([region_xy[r][0] for r in regions])
ypos = np.array([region_xy[r][1] for r in regions])

z_vals = [region_data[r].get(period, 0) for r in regions]


fig_go = go.Figure()
for arr in outline_lines:
    fig_go.add_trace(go.Scatter3d(x=arr[:,0], y= arr[:,1], z=arr[:,2], mode='lines', line=dict(color = 'black', width=2), hoverinfo = 'skip'))

fig_go.update_layout(scene=dict(xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False)),showlegend = False)


w = 0.8
d = 0.8


region_name="Sligo"
cx,cy = region_xy[region_name]

test_height = df_median[df_median["RPPI Region"] == region_name]["VALUE"].iloc[0]

left = cx-w/2
right = cx+w/2
front = cy-d/2
back = cy+d/2

v0 = (left, front,0)
v1 = (right, front,0)
v2 = (right, back,0)
v3 = (left, back,0)

v4 = (left, front, test_height)
v5 = (right, front,test_height)
v6 = (right, back,test_height)
v7 = (left, back,test_height)

verts =[v0,v1,v2,v3,v4,v5,v6,v7]

xv=[v[0] for v in verts]
yv=[v[1] for v in verts]
zv=[v[2] for v in verts]

i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],

fig_go.add_trace(go.Mesh3d(x=xv,y=yv,z=zv, i=i,j=j,k=k, color = "royalblue", opacity = 0.8, name=region_name))
fig_go.show()