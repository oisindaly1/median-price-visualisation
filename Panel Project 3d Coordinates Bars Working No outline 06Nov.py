import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

df = pd.read_csv("data.csv")
coords = pd.read_csv("coordinates.csv")
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



coords["x_scaled"] = (coords["CENTROID_X"] - coords["CENTROID_X"].mean())*100
coords["y_scaled"] = (coords["CENTROID_Y"] - coords["CENTROID_Y"].mean())*100

region_xy = {}

for r in regions:
    x = coords.loc[coords["PROPERTY DATA NAME"] == r, "x_scaled"].values[0]
    y = coords.loc[coords["PROPERTY DATA NAME"] == r, "y_scaled"].values[0]
    region_xy[r] = (x,y)

xpos = np.array([region_xy[r][0] for r in regions])
ypos = np.array([region_xy[r][1] for r in regions])

xpos = (xpos-xpos.mean())/1e5
ypos = (ypos-ypos.mean())/1e5
z_vals = [region_data[r].get(period, 0) for r in regions]


'''
#Old 3d graph column making
cols = 6
xpos = []
ypos = []
for i in range(len(regions)):
    xpos.append(i%cols)
    ypos.append(i//cols)


'''



fig3d = plt.figure(figsize = (12,7))
ax3d = fig3d.add_subplot(111, projection ='3d')
global_min = df_median["VALUE"].min()
global_max = df_median["VALUE"].max()
width = [8] * len(regions)
depth = [8] * len(regions)
height = z_vals

colours = plt.cm.viridis(np.array(height)/np.max(height))

bars3d = ax3d.bar3d(xpos, ypos, [0]*len(regions), width, depth, height, color=colours, shade = True, alpha=0.9)
ax3d.view_init(elev=50, azim = -125)
ax3d.set_xlim(min(xpos)-10, max(xpos)+10)
ax3d.set_ylim(min(ypos)-10, max(ypos)+10)
ax3d.set_zlim(global_min, global_max)
ax3d.set_title("3D Visualisation of Median Price by Region - " + period.strftime("%B %Y"))
ax3d.set_zlabel("Median Price (€)")
ax3d.set_xticks([])
ax3d.set_yticks([])

N = max(1, len(regions) //12)
for i, r in enumerate(regions):
    ax3d.text(xpos[i], ypos[i], z_vals[i]+(0.05*max(z_vals)),r, fontsize = 5, zdir='x', zorder =10)
    


#Adding in Slider



def update(val):
    date_index = int(slider.val)
    current_date = dates[date_index]

    for bar, region in zip(bars, regions):
        new_value = region_data[region].get(current_date, np.nan)
        bar.set_height(new_value)

    ax.set_title("Median Price by Region - " + current_date.strftime("%B %Y"))
    fig.canvas.draw_idle()

    #news stuff for the 3d graph
    

    ax3d.cla()
    new_height = []
    for r in regions:
        region_series = region_data[r]
        if current_date in region_series.index:
            new_height.append(region_series.loc[current_date])
        else:
            new_height.append(0)

    new_colours = plt.cm.viridis(np.array(new_height)/np.max(new_height))

    ax3d.bar3d(xpos, ypos, [0]*len(regions), width, depth, new_height, color=new_colours, shade = True, alpha=0.7)
    ax3d.set_zlim(global_min, global_max)
    for i, r in enumerate(regions):
        ax3d.text(xpos[i] +width[i] / 2, ypos[i] + depth[i]/2, new_height[i]+(0.05*max(new_height)),r, fontsize = 5, zdir='x', zorder =10)

    
    ax3d.set_xticks([])
    ax3d.set_yticks([])
    ax3d.set_title("3D Visualisation of Median Price by Region - " + current_date.strftime("%B %Y"))
    fig3d.canvas.draw_idle()

plt.subplots_adjust(bottom=0.3)
ax_slider = fig3d.add_axes([0.15,0.05, 0.7, 0.03])
slider = Slider(ax_slider, "Date", 0, len(dates) -1, valinit=0, valstep = 1)

slider.on_changed(update)    
plt.show()

