import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import geopandas
import numpy as np
from scipy import ndimage

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

def getDataFrame(latlngs):
    print("getDataFrame DEPRECATED, use makeDataFrame instead")
    df = pd.DataFrame(list(latlngs.values()), index=list(latlngs.keys()), columns=['coordinates'])

    gdf = gpd.GeoDataFrame(df, geometry='coordinates')
    return gdf

def getBoundingBox(gdf):
    return { 'xmax': 10, 'xmin': -10, 'ymax': 53, 'ymin': 45}

def mapCategory(gdf, ax, color, label):
    '''
    Plot the entire dataframe passed in with a single color.
    '''
    gdf.plot(ax=ax, color=color, label=label)
    for idx,row in gdf.iterrows():
        text_coords = [arr.tolist()[0] for arr in row.coordinates.xy]
        plt.annotate(s=row.text, xy=text_coords, horizontalalignment='center', size="large")
    return ax

def heatmap(d, bins=(400,400), smoothing=3, cmap='Greys'):
    def getx(pt):
        return pt.coords[0][0]

    def gety(pt):
        return pt.coords[0][1]
    ax = world.plot(
        color='white', edgecolor='black', figsize= (12,12), alpha=0.15
    )

    x = list(d.geometry.apply(getx))
    y = list(d.geometry.apply(gety))
    heatmap, xedges, yedges = np.histogram2d(y, x, bins=bins)
    extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
    #extent = (-180,180,-90,90)
    logheatmap = np.log(heatmap)
    logheatmap[np.isneginf(logheatmap)] = 0
    logheatmap = ndimage.filters.gaussian_filter(logheatmap, smoothing, mode='nearest')

    plt.imshow(logheatmap, cmap=cmap, extent=extent)
    #plt.colorbar()
    plt.gca().invert_yaxis()

    plt.xlim(-120, 50)
    plt.ylim(-75, 75)
    plt.show()

def mapByCategory(gdf, labels=False):
    '''
    Plot subsets of the dataframe by 'category' column
    '''
    ax = world.plot(
        color='white', edgecolor='gray', figsize=(20,20)
    )
    colors = ['red', 'orange', 'green', 'blue', 'indigo', 'purple', 'brown']
    for i,cat in enumerate(gdf.category.unique()):
        gdf[gdf.category == cat].plot(ax=ax, color=colors[i%len(colors)], label=cat, alpha=0.25)
    if labels:
        for idx,row in gdf.iterrows():
            text_coords = [arr.tolist()[0] for arr in row.coordinates.xy]
            plt.annotate(s=idx, xy=text_coords, horizontalalignment='center', size="medium")
    plt.legend()
    plt.show()

def mapWithLines(gdf, labels=False):
    '''
    Plot all points with lines connecting successive points in the dataframe.
    '''
    ax = world.plot(
        color='white', edgecolor='gray', figsize=(20,20)
    )
    gdf.plot(ax=ax, color='red')
    line_colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'xkcd:purple', 'xkcd:sky blue', 'xkcd:lavender', 'xkcd:aqua', 'xkcd:lilac']
    prev_point = None
    prev_text = None
    for idx,row in gdf.iterrows():
        curr_text = row.text
        curr_point = row.coordinates
        print(row.text, curr_point.x, curr_point.y)
        if prev_point and curr_text != prev_text:
            plt.plot([prev_point.x, curr_point.x], [prev_point.y, curr_point.y],
                      color=line_colors[idx%len(line_colors)], linewidth=2,
                      linestyle=':', label=f'{prev_text} to {curr_text}')
        prev_point = curr_point
        prev_text = curr_text
    if labels:
        for idx,row in gdf.iterrows():
            text_coords = [arr.tolist()[0] for arr in row.coordinates.xy]
            plt.annotate(s=row.text, xy=text_coords, horizontalalignment='center', size="medium")
