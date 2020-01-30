import os
import os.path as op
import re
import pandas as pd

local_data_path = op.join(op.expanduser('~'), '')

default_processed_filenames = {'merged_hmis': op.join(local_data_path, 'HMIS/2016', 'puget_preprocessed.csv'),
                               'ha_longitudinal': op.join(local_data_path, 'HILD', 'pha_longitudinal.csv'),
                               'ha_longitudinal_king': op.join(local_data_path, 'HILD', 'pha_longitudinal_kc.csv'),
                               'prelinked_data': op.join(local_data_path, 'HILD', 'PreLinkData.csv'),
                               'linked': op.join(local_data_path , 'HILD', 'PHA_HMIS_linked.csv'),
                               'all_merged': op.join(local_data_path, 'HILD', 'merged_agencies.csv'),
                               'clustered': op.join(local_data_path , 'HILD', 'clustered_merged_agencies.csv')}


path = '/Users/josehernandez/Documents/eScience/projects/NIreland_NLP/'

# Get list of files
files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.txt' in file:
            files.append(os.path.join(r, file))
        
# loop through the files exclude Nodes.txt <-- nVivo relic 
# create lists 
p_text = []
cat = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.txt' in file:
            files.append(os.path.join(r, file))

# create method to extract relevant text and appropriate categories from file name
for f in files:
    if "Nodes" not in f:
        print(f)
        # Extract text and parse into df
        docs = open(f, "r")
        text = docs.read()
        docs.close()
        text = re.split(r'.*(?=Files)', text)
        # get the file name 
        cat_code = Path(f).name 
        cat.append(re.sub('.txt', '', cat_code))
        p_text.append(list(filter(None, text)))
# create dict that we can use to create a df
cat_text = dict(zip(cat, p_text))

for key, value in cat_text.items() :
    print (key)