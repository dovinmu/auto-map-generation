import pandas as pd

# make keywords reference lemmas, not strings
topics = {
    'birth': ['was born', ' born'],
    'death': [' died'],
    'travel': ['went to ', ' moved to', 'traveled', 'travelled', 'visited'],
    'lived':  [' lived in', ' lived at', ' live in', ' reside', 'resided', 'residence at', 'stayed in ', 'stay in ', ' spent '],
    'education': ['university', 'school ', 'studied', 'to study ' 'schooling', 'education ', 'educated', ' degree in ' 'College', 'graduate', 'graduating', 'worked as a', 'worked at', 'job as', 'jobs'],
    'parents': ['father', ' mother', 'grandfather', 'grandmother', 'grandparents']
}

def getTopics(gdf):
    gdf['topic'] = pd.Series([None for n in range(len(gdf))])
    for i,sentence in enumerate(gdf['sentence']):
        for topic,phrases in topics.items():
            for phrase in phrases:
                if phrase in sentence.text:
                    gdf.topic[i] = topic
    return gdf

def getDates(gdf):
    gdf['date'] = pd.Series([[None] for n in range(len(gdf))])
    for i,sentence in enumerate(gdf['sentence']):
        gdf['date'][i] = [x.text for x in sentence.ents if x.label_ == 'DATE'][:1]
    return gdf
