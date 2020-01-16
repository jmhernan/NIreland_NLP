
import os
from pathlib import Path
import re
import pandas as pd

test_file = '/Users/josehernandez/Documents/eScience/projects/NIreland_NLP/justifications_01-06/justifications_txt/J_Denial.txt'

f = open(test_file, "r")
text = f.read()
f.close()

text

path = '/Users/josehernandez/Documents/eScience/projects/NIreland_NLP/'

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.txt' in file:
            files.append(os.path.join(r, file))
            

    

files[1]
name = Path(files[1]).name 
# two different ways  
name.replace('.txt', '')
re.sub('.txt', '', name)

# loop through the files exclude Nodes.txt <-- nVivo relic 
# create lists 
p_text = []
cat = []

# create file paths list 
files = []
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
# Create df this will create a df with lists where each row is the justification
# category (12) followed by a list of the individual "files" within the category
temp_df = pd.DataFrame.from_dict(cat_text, orient='index')

# What we want is a column for the category repeated by each entry of the list 
# which will becore rows 
df_long = temp_df.stack().reset_index(level=1, drop=True).to_frame(name='raw_text')

# The previous created a long df with the category as the index
# we create a column using that index
df_long.reset_index(level=0, inplace=True)

# rename the column 
df_long = df_long.rename(columns = {'index':'justification'})

# we can now proceed with the other regex magic procedures
# JH note: maybe create a function of this...

## Extracts image ID as a unique column
df_long["image_id"] = df_long["raw_text"].str.extract(r"(IMG_\d{4})")
df_long.head

## Extracts file ID as a unique column
df_long["file_id"] = df_long["raw_text"].str.extract(r"(DEFE\w+|PREM\w+|CJ\w+)")
df_long.head

## Extracts justification text as its own raw-text column (Removes “Reference”)
df_long["just_text_lump"] = df_long["raw_text"].str.replace(r"(?<!Files)(.*)(?<=Coverage)", "").str.strip()
df_long["just_text_lump"].head
df_long["just_text_lump2"] = df_long["just_text_lump"].str.replace(r"\W+", " ") # This removes all non-letter characters, including \n spaces and punctuation.

## Extracts justification text as its own raw-text column (Retains “Reference” markers which can be used to split each unique code).
df_long["just_text"] = df_long["raw_text"].str.replace(r"(?<!Files)(.*)(?<=Coverage])", "").str.strip()
df_long["just_text"].head

## Write out as a csv
df_long.to_csv(os.path.join(path, 'denial_long_parsed.csv'))

