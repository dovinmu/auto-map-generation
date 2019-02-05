import spacy
import en_core_web_sm
import geocoder
import pandas as pd
import geopandas as gpd
import wikipedia
from shapely.geometry import Point
nlp = en_core_web_sm.load()

skip = ['mars', 'earth', '\n', 'xi', 'xv']
current_id = 0

def getLocations(text, includesents=True):
    return getLabeledEntities(text, ['GPE', 'LOC'], includesents)

def getLabeledEntities(text, labels, includesents=True):
    '''
    Outputs a list of lists of the form [location text]
    '''
    doc = nlp(text, disable=['textcat', 'tagger']) if includesents else nlp(text, disable=['parser', 'textcat', 'tagger'])
    entities = []
    for i,X in enumerate(doc.ents):
        if X.label_ in labels and X.text.lower() not in skip:
            entities.append([X.text, X.label_, i, X.sent] if includesents else [X.text, X.label_, i])

    return entities

def getGeojson(locations, locator=geocoder.osm, output=False):
    coordinates = {}
    for i,X in enumerate(locations):
        if type(X) == type([]):
            location_name = X[0]
        else:
            location_name = X
        if output:
            print(f'{i+1}/{len(locations)}', location_name)
        if location_name not in coordinates:
            coordinates[location_name] = locator(location_name.lower()).geojson
    return coordinates

def getLatLng(locations, locator=geocoder.osm, output=False):
    geojsons = getGeojson(locations, locator, output)
    return coordinatesToLatLng(geojsons)

def geojsonToLatLng(coordinates):
    latLngs = {}
    for name,geojson in coordinates.items():
        if geojson['features']:
            latLngs[name] = Point(
            geojson['features'][0]['properties']['lng'],
            geojson['features'][0]['properties']['lat']
            )
    return latLngs

def wikipediaFilter(geojsondict):                #probably too strict
    filtered = {}
    for name,geojson in geojsondict.items():
        try:
            a,b = wikipedia.page(name).coordinates
            a,b = float(a), float(b)
        except:
            a,b = (0.0, 0.0)
    if abs(a-lat) < 1 and abs(b-lng) < 1:
        filtered[name] = geojson
    return filtered

def makeDataFrame(text, includesents=True, output=False):
    locs = getLocations(text, includesents)
    latLngs = getLatLng(locs, output)
    filtered_locs = []
    for loc in locs:
        if loc[0] in latLngs:
            filtered_locs.append(loc + [latLngs[loc[0]]])

    df = pd.DataFrame(filtered_locs, columns=['text', 'label', 'idx', 'sentence', 'coordinates']) if includesents else pd.DataFrame(filtered_locs, columns=['text', 'label', 'idx', 'coordinates'])

    gdf = gpd.GeoDataFrame(df, geometry='coordinates')
    return gdf
