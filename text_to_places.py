import spacy
import en_core_web_sm
import geocoder
from shapely.geometry import Point
nlp = en_core_web_sm.load()

skip = ['mars', 'earth', '\n', 'xi', 'xv']

def getLocations(text):
    return getLabeledEntities(text, ['GPE', 'LOC'])

def getLabeledEntities(text, labels):
    doc = nlp(text)
    locations = [X for X in doc.ents if X.label_ in labels and X.text.lower() not in skip]
    return locations

def getLatLng(locations):

    coordinates = { X.text: geocoder.osm(X.text.lower()) for X in locations}
    latlngs = {}
    for name,item in coordinates.items():
        if item.geojson['features']:
            latlngs[name] = Point(
                item.geojson['features'][0]['properties']['lng'],
                item.geojson['features'][0]['properties']['lat']
            )
    return latlngs
