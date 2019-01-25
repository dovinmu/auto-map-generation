import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import geopandas

def getDataFrame(latlngs):
    df = pd.DataFrame(list(latlngs.values()), index=list(latlngs.keys()), columns=['Coordinates'])

    gdf = gpd.GeoDataFrame(df, geometry='Coordinates')
    return gdf

def getBoundingBox(gdf):
    return { 'xmax': 10, 'xmin': -10, 'ymax': 53, 'ymin': 45}



def mapCategory(gdf, ax, color):
    gdf.plot(ax=ax, color=color)
    for idx,row in gdf.iterrows():
        text_coords = [arr.tolist()[0] for arr in row.Coordinates.xy]
        plt.annotate(s=idx, xy=text_coords, horizontalalignment='center', size="medium")

    return ax
