###############################################
## NI NLP Project
## 1) Append each of 12 justification.txt files
## 2) Parse text into components
## 3) Fix image naming issue
###############################################

import os
from pathlib import Path
import re
import pandas as pd
import numpy as np


this_file_path = os.path.abspath(__file__)
project_root = os.path.split(this_file_path)[0]
j_path = os.path.join(project_root, 'just_0106') + '/'

sys.path # make sure the repo is in the path 

import preprocess as pr

## Load txt document
raw = pr.text_preprocess(j_path)
raw.files

cat_text = raw.nvivo_clumps()

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
df_long["file_id_orig"] = df_long["raw_text"].str.extract(r"(DEFE\w+|PREM\w+|CJ\w+)")
df_long.head

## Fixing File/Image number issue (PREM 15 478, 1010, 1689). 
# Note: 1010/1689 and 487 have overlapping image numbers (1010/1689: IMGs 001-205; 487: IMGs 001-258)
# This will be a problem later if we use IMG as a unique identifier
df_long["image_id_issue"] = df_long["file_id_orig"].str.extract(r"(PREM_15_.*_\S*)") 
df_long["image_id_issue"] = r"IMG_0" + df_long["image_id_issue"].str.extract(r"(\d{3}$)")
df_long["image_id"] = df_long["image_id"].fillna(df_long["image_id_issue"])

df_long["file_id"] = df_long["file_id_orig"].str.extract(r"(PREM_15_.*_\S*)") 
df_long["file_id"] = df_long["file_id"].str.extract(r"(PREM_15_\d*)")
df_long["file_id"] = df_long["file_id"].fillna(df_long["file_id_orig"])

# Merge Image and File names to output the original file name for merging purposes
df_long["img_file"] = df_long.image_id.map(str) + "_" + df_long.file_id

# Maintain original document ID number to merge with .txt from full corpus
df_long["img_file_orig"] = df_long["raw_text"].str.extract(r"(?<=\d{2}\\\\)(.*)(?=.-)")

## Extracts justification text as its own raw-text column (Removes “Reference”)
df_long["just_plain_text_all_ref"] = df_long["raw_text"].str.replace(r"(?<!Files)(.*)(?<=Coverage)", "").str.strip()
df_long["just_plain_text_all_ref"].head
df_long["just_plain_text_all_ref"] = df_long["just_plain_text_all_ref"].str.replace(r"\W+", " ") # This removes all non-letter characters, including \n spaces and punctuation.

## Extracts justification text as its own raw-text column (Retains “Reference” markers which can be used to split each unique code).
df_long["just_text_all_ref"] = df_long["raw_text"].str.replace(r"(?<!Files)(.*)(?<=Coverage])", "").str.strip()
df_long["just_text_all_ref"].head

## Extract the number of unique codes in this justification category a given document received
df_long["ref_count"] = df_long["raw_text"].str.extract(r"(\d\sreference)")
df_long["ref_count"] = df_long["ref_count"].str.extract(r"(\d)")

# split multiple reference text entries into new columns
test = df_long["just_text_all_ref"].str.split(r'.*(?=Reference)',expand = True) 
# 
new_test = pd.concat([df_long[['image_id', 'file_id', 'img_file_orig', 'justification']], test], axis=1).drop([0], axis=1)
new_test.info()

idx = ['image_id', 'file_id', 'img_file_orig', 'justification']

multi_df = new_test.set_index(idx)
multi_df.head

stacked_df = multi_df.stack(dropna=False)
long_df = stacked_df.reset_index()
long_df.columns
long_df.shape
long_df = long_df.rename(columns = {0: 'text'})
long_df.head(10)

# clean up "None" missing text HERE
long_df.iloc[[3]]
long_df.dropna(subset=['text'], inplace=True)
long_df.shape

# clean up "Refernce and weird characters here"
long_df['text'] = long_df['text'].replace({"(Reference.\d)(.*)(Coverage\\n)": ""}, regex=True)
long_df.head(20)

# save the data 
long_df.to_csv(os.path.join(project_root, 'justifications_long_training.csv'))
long_df.columns

# Creating a List within a column (proved to be a headache due to the non characters)
# Create a list within a single column 
# df_long["coded_refs"] = df_long["just_text_all_ref"].str.split(r'.*(?=Reference)',expand = False) 

## Extracts docs that have page capture codes (rather than text codes) and outputs it to a different doc
df_pg_ref = long_df[long_df['text'].str.contains(r"(Page.\d.:)")]
df_pg_ref.shape
df_pg_ref.columns
df_pg_ref.head

df_pg_ref = df_pg_ref[['image_id', 'file_id', 'img_file_orig', 'justification', 'level_4']]
df_pg_ref.to_csv(os.path.join(project_root, 'page_ref.csv'))

## Write out as a csv
## df_long.to_csv(os.path.join(project_root, 'justifications_long_parsed.csv'))