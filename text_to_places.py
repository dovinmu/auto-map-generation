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
    Given raw text, outputs a list of lists of the form [text, entity label, word index, sentence (if includesents=True)]
    '''
    doc = nlp(text, disable=['textcat', 'tagger']) if includesents else nlp(text, disable=['parser', 'textcat', 'tagger'])
    entities = []
    for i,X in enumerate(doc.ents):
        if X.label_ in labels and X.text.lower() not in skip:
            entities.append([X.text, X.label_, i, X.sent] if includesents else [X.text, X.label_, i])

    return entities

def getGeojson(locations, locator=geocoder.osm, output=False):
    '''
    Given the output of getLocations, query a text-to-location service and return
    a dictionary mapping { text: geojson from query result }
    '''
    geojsonDict = {}
    for i,X in enumerate(locations):
        location_name = X[0]
        if output:
            print(f'{i+1}/{len(locations)}', location_name)
        if location_name not in geojsonDict:
            geojsonDict[location_name] = locator(location_name.lower()).geojson
    return geojsonDict

def getLatLng(locations, locator=geocoder.osm, output=False):
    '''
    Given the output of getLocations, query a text-to-location service and return
    a dictionary mapping { text: Point(lat,lng) }
    '''
    geojsonDict = getGeojson(locations, locator, output)
    return geojsonToLatLng(geojsonDict)

def geojsonToLatLng(coordinates):
    '''
    Extract the lat,lng from geojson objects and return a new dictionary mapping
    { text: Point(lat,lng) }
    '''
    latLngs = {}
    for name,geojson in coordinates.items():
        if geojson['features']:
            latLngs[name] = Point(
            geojson['features'][0]['properties']['lng'],
            geojson['features'][0]['properties']['lat']
            )
    return latLngs

def geojsonFilter(geojsons, locator='osm', output=False):
    '''
    Given a geojson dictionary, filter based on properties in the geojson using
    a per-locator service whitelist.
    '''
    osm_allowed = ['place', 'boundary']
    arcgis_allowed = ['Locality']

    locations = {}
    for name,geojson in geojsons.items():
        for f in geojson['features']:
            quality = f['properties']['quality']
            if locator == 'osm':
                geotype = f['properties']['raw']['type']
                category = f['properties']['raw']['category']
            else:
                geotype = category = None
            if output:
                print(name, '(qual, cat, type) :',quality,category,geotype)
            if locator=='osm':
                if category in osm_allowed:
                    locations[name] = geojson
                    break
            elif locator=='arcgis':
                if quality in arcgis_allowed:
                    locations[name] = geojson
                    break
            else:
                raise Exception("Locator unknown:", locator)
            if output:
                print("...filtered", name)
    return locations

def sizeFilter(geojsons, min_size=0, max_size=1_000_000):
    def size(bbox):
        xlen = abs(float(bbox[0]) - float(bbox[1]))
        ylen = abs(float(bbox[2]) - float(bbox[3]))
        return xlen * ylen
    result = {}
    for name,geojson in geojsons.items():
        bbox = geojson['features'][0]['properties']['raw']['boundingbox']
        # print(name, size(bbox))
        sz = size(bbox)
        if sz > 0.005 and sz < 2:
            result[name] = geojson
        else:
            print('filtered', name, 'of size', round(sz,4))
    return result

def wikipediaFilter(df):
    to_keep = []
    for row in df.itertuples():
        name = row.text
        try:
            lat,lng = wikipedia.page(name).coordinates
        except wikipedia.DisambiguationError:
            print('disambiguation error', name)
            to_keep.append(row.Index)
            continue
        except:
            print("no coordinates for", name, '...filtered')
            continue
        print('got lat,lng:', name, round(lat,2), round(lng,2))
        to_keep.append(row.Index)
        df.at[row.Index, 'coordinates'] = Point(lng, lat)
        # if abs(a-lat) < 1 and abs(b-lng) < 1:
        #     print('coords matched for', name)
        #     to_keep.append(row.Index)
        # else:
        #     print('found coords did not match for', name)

    return df.iloc[to_keep]

def makeDataFrame(text, includesents=True, output=False, locator=geocoder.osm):
    locs = getLocations(text, includesents)
    geojsons = getGeojson(locs, locator, output)
    geojsons = geojsonFilter(geojsons, locator.__name__, output)
    latLngs = geojsonToLatLng(geojsons)

    # there will have been some locations that get an error from the locator API--filter these
    filtered_locs = []
    for loc in locs:
        if loc[0] in latLngs:
            filtered_locs.append(loc + [latLngs[loc[0]]])

    df = pd.DataFrame(filtered_locs, columns=['text', 'label', 'idx', 'sentence', 'coordinates']) if includesents else pd.DataFrame(filtered_locs, columns=['text', 'label', 'idx', 'coordinates'])

    gdf = gpd.GeoDataFrame(df, geometry='coordinates')
    return gdf
