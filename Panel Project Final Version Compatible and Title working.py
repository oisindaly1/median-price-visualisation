# Scripts/OisinPaulDaly.py

def run_panel(): #Function added for compatability 
        
    '''
    Panel 1 – Oisín Daly - 24374553 - 3D median price map with time slider
    Uses Plotly for 3D visualisation with slider to show change in median price by region over time.
    Data Source: Central Statistics Office (CSO), Table HPM03
    
    '''
    import pandas as pd 
    import numpy as np
    import geopandas as gpd
    import plotly.graph_objects as go
    from shapely.geometry import Polygon, MultiPolygon
    from pathlib import Path

    # --- Paths --- for compatability
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "Data" 

    df = pd.read_csv(DATA_DIR / "data.csv") # Main data file
    coords = pd.read_csv(DATA_DIR / "coordinates.csv") # Region co-ordinates
    counties = gpd.read_file(DATA_DIR / "Administrative_Areas___OSi_National_Statutory_Boundaries_-978765968693620525.geojson") # Outline GeoJSON File 

    counties = counties.to_crs(epsg=2157)

    # Filter data for relevant data for visualisation
    df_median = df[
        (df["Statistic Label"] == "Median Price")
        & (df["RPPI Region"] != "All")
        & (df["Stamp Duty Event"] == "Executions")
        & (df["Dwelling Status"] == "All Dwelling Statuses")
        & (df["Type of Buyer"] == "All Buyer Types")
    ].copy()

    df_median["Month"] = pd.to_datetime(df_median["Month"], format="%Y %B") # Change formatting for legibility

    dates = sorted(set(df_median["Month"])) # create a set of unique dates, will be used for slider steps later
    regions = sorted(set(coords["PROPERTY DATA NAME"])) # create a set of unique regions, will be used for sorting

    region_data = {
        region: group.set_index("Month")["VALUE"]
        for region, group in df_median.groupby("RPPI Region")
    } # Dictionary of region data for easy indexing of each value

    origin_x = coords["CENTROID_X"].mean()
    origin_y = coords["CENTROID_Y"].mean()
    # scaling the x and y coordinates for better visualisation
    coords["x_scaled"] = (coords["CENTROID_X"] - origin_x) / 1e4 
    coords["y_scaled"] = (coords["CENTROID_Y"] - origin_y) / 1e4

    region_xy = {} # list of coordinates for each region
    for r in regions:
        x = coords.loc[coords["PROPERTY DATA NAME"] == r, "x_scaled"].values[0]
        y = coords.loc[coords["PROPERTY DATA NAME"] == r, "y_scaled"].values[0]
        region_xy[r] = (x, y)

    heights_by_date = {
        date: [region_data[r].get(date, 0) for r in regions] for date in dates
    } # Dictionary of heights for each date

    # --- Outline geometry ---
    ireland = counties.dissolve() # gets rid of inner county boundaries
    geom = ireland.geometry.iloc[0]
    if geom.geom_type == "MultiPolygon":
        geom = max(geom.geoms, key=lambda x: x.area)

    geom_simplified = geom.simplify(tolerance=2000, preserve_topology=True) # Tolerance added as entire country is large, not fully needed

    #Setting values for the outline drawing
    x, y = geom_simplified.exterior.xy 
    x_scaled = (np.array(x) - origin_x) / 1e4
    y_scaled = (np.array(y) - origin_y) / 1e4
    z = np.zeros(len(x))

    w = 0.8
    d = 0.8
    all_heights = [region_data[r].get(d, 0) for r in regions for d in dates] # Flattened list of all heights for color scaling
    h_min = min(all_heights) 
    h_max = max(all_heights)

    fig_go = go.Figure()

    fig_go.add_trace(
        go.Scatter3d(
            x=x_scaled,
            y=y_scaled,
            z=z,
            mode="lines",
            line=dict(color="black", width=3),
            hoverinfo="skip",
        )
    ) # Country outline trace

    # Drawing Bars

    period = dates[0] # Initial period for the first frame - Jan 2010
    mesh_indices = []

    for region_name in regions:
        cx, cy = region_xy[region_name] # coordinates for region center
        height = region_data[region_name].get(period, 0) # Indexing Height

        left = cx - w / 2 
        right = cx + w / 2
        front = cy - d / 2
        back = cy + d / 2

        #Creating vertices for the bar
        #v0->v3: bottom face, v4->v7: top face

        v0 = (left, front, 0)
        v1 = (right, front, 0)
        v2 = (right, back, 0)
        v3 = (left, back, 0)

        v4 = (left, front, height)
        v5 = (right, front, height)
        v6 = (right, back, height)
        v7 = (left, back, height)

        verts = [v0, v1, v2, v3, v4, v5, v6, v7]

        xv = [v[0] for v in verts]
        yv = [v[1] for v in verts]
        zv = [v[2] for v in verts]

        # Vertices taken from Plotly Development Team - see reflection for reference 

        i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
        j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
        k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

        date_str = period.strftime("%B %Y")

        #Drawing the mesh for each bar
        fig_go.add_trace(
            go.Mesh3d(
                x=xv,
                y=yv,
                z=zv,
                i=i,
                j=j,
                k=k,
                intensity=[height] * len(i),
                customdata=[[height, date_str]] * len(i),
                colorscale="Viridis",
                cmin=h_min,
                cmax=h_max,
                opacity=0.8,
                name=region_name,
                flatshading=False,
                hovertemplate=(
                    "Region: "
                    + region_name
                    + "<br>%{customdata[1]}"
                    + "<br>Median Price: €%{customdata[0]:,.0f}<extra></extra>"
                ),
                hoverlabel=dict(font_color="black"),
            )
        )
        mesh_indices.append(len(fig_go.data) - 1)

    # Creating Animation Frames for Slider
    frames = []

    for d in dates:
        date_str = d.strftime("%B %Y")
        heights = heights_by_date[d]

        frame_data = [dict(type="scatter3d")] # enabled it like this so that it ignores the first trace - the outline
        for h in heights:
            new_z = [0, 0, 0, 0, h, h, h, h]
            frame_data.append(
                dict(
                    type="mesh3d",
                    z=new_z,
                    intensity=[h] * len(i),
                    customdata=[[h, date_str]] * len(i),
                    intensitymode="cell",
                    colorscale="Viridis",
                    cmin=h_min,
                    cmax=h_max,
                )
            )

        # Adding frame to frames list

        frames.append(
            go.Frame(
                data=frame_data,
                name=str(d),
            )
        )

    fig_go.frames = frames # setting the frames to plotly global figure

    #Slider 
    slider_steps = []
    for d in dates:
        date_str = d.strftime("%B %Y")
        slider_steps.append(
            dict(
                label=date_str, # sets the label for each step as the date string
                method="animate", # done for smooth animation
                args=[
                    [str(d)],
                    {
                        "frame": {"duration": 0, "redraw": True},
                        "transition": {"duration": 0},
                        "mode": "immediate",
                    },
                ],
            )
        )

    sliders = [
        dict(
            active=0,
            steps=slider_steps,
            x=0.1,
            xanchor="left",
            y=0,
            yanchor="top",
            len=0.8,
            pad=dict(t=30, b=10),
        )
    ] # defining slider properties

    #Layout tuned for dashboard cell - FT Styling as well
    fig_go.update_layout(
        autosize=True,
        height=None,
        margin=dict(t=60, b=90, l=0, r=0),
        template="simple_white",
        font=dict(
            family="Georgia, 'Times New Roman', serif",
            size=20,
            color="#3C3C3C",
        ),
        paper_bgcolor="#FFF1E5", # FT hexcode
        plot_bgcolor="#FFF1E5",
        scene=dict(
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.7),
            camera=dict(eye=dict(x=1, y=-1, z=0.8), up=dict(x=0, y=0, z=1)),
            xaxis=dict(visible=False, range=[-25, 25]),
            yaxis=dict(visible=False, range=[-25, 25]),
            zaxis=dict(visible=False, range=[0, h_max]),
        ),
        showlegend=False,
        title=dict(
                    text=((
                            "3D Visualisation of Median Price by Region"
                            "<br><sup>Source: Central Statistics Office (CSO), Table HPM03</sup>"
                        )),
            font=dict(
                family="Georgia, 'Times New Roman', serif",
                size=14,
                color="#3C3C3C",
            ),
        ),
        sliders=sliders,
    )

    return fig_go