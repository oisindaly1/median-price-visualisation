import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

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

period = df_median["Month"].iloc[0]
print(period)
df_month = df_median[df_median["Month"] == period]

plt.bar(df_month["RPPI Region"], df_month["VALUE"])
plt.title("Median Price by Region - " + period.strftime("%B %Y"))
plt.xlabel("RPPI Region")
plt.ylabel("Median Price (€)")
plt.xticks(rotation = 90)
plt.show()

dates = sorted(set(df_median["Month"]))
regions = sorted(set(df_median["RPPI Region"]))

#Using dictionary to make it easier to get my data

region_data = {
    region: group.set_index("Month")["VALUE"]
    for region, group in df_median.groupby("RPPI Region")
}
