import spacy
import en_core_web_sm
import geocoder
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
nlp = en_core_web_sm.load()

skip = ['mars', 'earth', '\n', 'xi', 'xv']
current_id = 0

def getLocations(text, nameOnly=True):
    return getLabeledEntities(text, ['GPE', 'LOC'], nameOnly)

def getLabeledEntities(text, labels, nameOnly=True):
    doc = nlp(text)
    entities = []
    for i,X in enumerate(doc.ents):
        if X.label_ in labels and X.text.lower() not in skip:
            if nameOnly:
                entities.append(X.text)
            else:
                entities.append([X.text, X.label_, i, X.sent])
    return entities

def getLatLng(locations):
    coordinates = {}
    for i,X in enumerate(locations):
        if type(X) == type([]):
            location_name = X[0]
        else:
            location_name = X
        print(f'{i+1}/{len(locations)}', location_name)
        if location_name not in coordinates:
            coordinates[location_name] = geocoder.osm(location_name.lower())

    latLngs = {}
    for name,item in coordinates.items():
        if item.geojson['features']:
            latLngs[name] = Point(
                item.geojson['features'][0]['properties']['lng'],
                item.geojson['features'][0]['properties']['lat']
            )
    return latLngs

def makeDataFrame(text):
    locs = getLocations(text, False)
    latLngs = getLatLng(locs)
    filtered_locs = []
    for loc in locs:
        if loc[0] in latLngs:
            filtered_locs.append(loc + [latLngs[loc[0]]])

    df = pd.DataFrame(filtered_locs, columns=['text', 'label', 'idx', 'sentence', 'coordinates'])

    gdf = gpd.GeoDataFrame(df, geometry='coordinates')
    return gdf
