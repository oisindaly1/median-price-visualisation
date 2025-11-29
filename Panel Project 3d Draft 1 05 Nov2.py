import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

df = pd.read_csv("data.csv")

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
regions = sorted(set(df_median["RPPI Region"]))

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

z_vals = [region_data[r].get(period, 0) for r in regions]

cols = 6
xpos = []
ypos = []
for i in range(len(regions)):
    xpos.append(i%cols)
    ypos.append(-(i//cols))

fig3d = plt.figure(figsize = (12,7))
ax3d = fig3d.add_subplot(111, projection ='3d')

width = [0.8] * len(regions)
depth = [0.8] * len(regions)
height = z_vals

colours = plt.cm.viridis(depth/np.max(height))

ax3d.bar3d(xpos, ypos, [0]*len(regions), width, depth, height, color=colours, shade = True, alpha=0.9)
ax3d.view_init(elev=25, azim = 60)

ax3d.set_title("3D Visualisation of Median Price by Region - " + period.strftime("%B %Y"))
ax3d.set_zlabel("Median Price (€)")
ax3d.set_xticks(range(min(xpos), max(xpos) +1))
ax3d.set_yticks(range(min(ypos), max(ypos) +1))

N = max(1, len(regions) //12)
for i, r in enumerate(regions):
    if i% N == 0:
        ax3d.text(xpos[i], ypos[i], height[i], r, fontsize = 8, zdir='x')


#Adding in Slider

plt.subplots_adjust(bottom=0.3)
ax_slider = plt.axes([0.15,0.05, 0.7, 0.03])
slider = Slider(ax_slider, "Date", 0, len(dates) -1, valinit=0, valstep = 1)

def update(val):
    date_index = int(slider.val)
    current_date = dates[date_index]

    for bar, region in zip(bars, regions):
        new_value = region_data[region].get(current_date, np.nan)
        bar.set_height(new_value)

    ax.set_title("Median Price by Region - " + current_date.strftime("%B %Y"))
    fig.canvas.draw_idle()

slider.on_changed(update)    
plt.show()