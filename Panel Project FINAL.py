import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import geopandas as gpd

df = pd.read_csv("data.csv")
coords = pd.read_csv("coordinates.csv")
counties = gpd.read_file("Administrative_Areas___OSi_National_Statutory_Boundaries_-978765968693620525.geojson")
counties = counties.to_crs(epsg=2157)



counties = counties.to_crs(epsg=2157)

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

dates = sorted(set(df_median["Month"]))
regions = sorted(set(coords["PROPERTY DATA NAME"]))


#Using dictionary to make it easier to get my data

region_data = {
    region: group.set_index("Month")["VALUE"]
    for region, group in df_median.groupby("RPPI Region")
}
fig, ax = plt.subplots(figsize=(12,6))
period = dates[0]
df_month = df_median[df_median["Month"] == period]

#Basic Bar Chart - v1

bars = ax.bar(regions, [region_data[r].get(period, np.nan) for r in regions])
plt.title("Median Price by Region - " + period.strftime("%B %Y"))
plt.xlabel("RPPI Region")
plt.ylabel("Median Price (€)")
plt.xticks(rotation = 90)

#Adding in basic 3d Graph at first, followed by slider

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
plt.rcParams['axes3d.automargin'] = True

origin_x = coords["CENTROID_X"].mean()
origin_y = coords["CENTROID_Y"].mean()

coords["x_scaled"] = (coords["CENTROID_X"] - origin_x)/1e4
coords["y_scaled"] = (coords["CENTROID_Y"] - origin_y)/1e4

region_xy = {}

for r in regions:
    x = coords.loc[coords["PROPERTY DATA NAME"] == r, "x_scaled"].values[0]
    y = coords.loc[coords["PROPERTY DATA NAME"] == r, "y_scaled"].values[0]
    region_xy[r] = (x,y)

heights_by_date = {
    date: [region_data[r].get(date, 0) for r in regions] for date in dates
}

xpos = np.array([region_xy[r][0] for r in regions])
ypos = np.array([region_xy[r][1] for r in regions])

z_vals = [region_data[r].get(period, 0) for r in regions]

#PLOTLY
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'
import shapely
from shapely.geometry import Polygon, MultiPolygon

ireland = counties.dissolve()
geom = ireland.geometry.iloc[0]
if geom.geom_type == 'MultiPolygon':
    geom = max(geom.geoms, key = lambda x: x.area)

geom_simplified = geom.simplify(tolerance=2000, preserve_topology = True)

x,y = geom_simplified.exterior.xy
x_scaled = (np.array(x)-origin_x)/1e4
y_scaled = (np.array(y)-origin_y)/1e4 
z = np.zeros(len(x))


w = 0.8
d = 0.8
all_heights = [region_data[r].get(d, 0) for r in regions for d in dates]
h_min = min(all_heights)
h_max = max(all_heights)
fig_go = go.Figure()

fig_go.add_trace(go.Scatter3d(x=x_scaled, y=y_scaled, z=z, mode='lines', line=dict(color = 'black', width=3), hoverinfo = 'skip'))

fig_go.update_layout(template = 'simple_white',
                     font = dict(family = "Playfair Display, serif", size = 16),
                     paper_bgcolor = "#FFF1E5",
                     plot_bgcolor = "#FFF1E5",
                     scene=dict(aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.7),
                                camera=dict(eye=dict(x=1, y=-1, z=0.8), up = dict(x=0,y=0,z=1)),
                                xaxis=dict(visible=False, range=[-25, 25]),
                                yaxis=dict(visible=False, range=[-25, 25]),
                                zaxis=dict(visible=False, range=[0, h_max])),
                                showlegend=False, title=dict(text=f"3D Visualisation of Median Price by Region - {period.strftime('%B %Y')}" + "<br><sup>Source: Central Statistics Office (CSO), Table HPM03 -https://data.cso.ie/ </sup>", font = dict(family = "Playfair Display, serif", size = 28)))

print(h_min, h_max)
mesh_indices = []

for region_name in regions:
    cx,cy = region_xy[region_name]
    height = region_data[region_name].get(period, 0)
    
    left = cx-w/2
    right = cx+w/2
    front = cy-d/2
    back = cy+d/2

    v0 = (left, front,0)
    v1 = (right, front,0)
    v2 = (right, back,0)
    v3 = (left, back,0)

    v4 = (left, front, height)
    v5 = (right, front,height)
    v6 = (right, back,height)
    v7 = (left, back,height)

    verts =[v0,v1,v2,v3,v4,v5,v6,v7]

    xv=[v[0] for v in verts]
    yv=[v[1] for v in verts]
    zv=[v[2] for v in verts]

    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    date_str = period.strftime("%B %Y")
    trace = go.Mesh3d(x=xv,y=yv,z=zv, i=i,j=j,k=k, intensity = [height]*len(i), 
                      customdata=[[height, date_str]]*len(i),colorscale ='Viridis',
                      cmin = h_min, cmax = h_max,
                      opacity = 0.8, name=region_name, flatshading=False,
                      hovertemplate = "Region: " + region_name + "<br>%{customdata[1]}" + "<br>Median Price: €%{customdata[0]:,.0f}" + "<extra></extra>", hoverlabel=dict(font_color='black'))
    fig_go.add_trace(trace)
    mesh_indices.append(len(fig_go.data) - 1)

frames = []

for d in dates:
    date_str = d.strftime("%B %Y")
    heights = heights_by_date[d]    
    frame_data = [dict(type="scatter3d")]
    for h in heights:
        new_z = [0,0,0,0,h,h,h,h]
        frame_data.append(dict(type='mesh3d', z=new_z, intensity = [h]*len(i), customdata = [[h, date_str]]*len(i), intensitymode = 'cell',colorscale = 'Viridis', cmin = h_min, cmax = h_max))

    frames.append(go.Frame(data=frame_data, name = str(d), layout=dict(title=dict(text=f"3D Visualisation of Median Price by Region - {d.strftime('%B %Y')}" + "<br><sup>Source: Central Statistics Office (CSO), Table HPM03</sup>"))))

fig_go.frames = frames

slider_steps = []
for d in dates:
    date_str = d.strftime("%B %Y")
    slider_steps.append(dict(label = str(date_str), method = 'animate',args=[[str(d)],
            {"frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}, "mode": "immediate"}]))

fig_go.update_layout(
    sliders=[dict(steps = slider_steps, active = 0, currentvalue = dict(prefix='Date: ',font=dict(size=16,color="#4a4a4a",family='Georgia')))],
)


fig_go.show()



