## Neural network boiler plate 
## using pretrained word2vec

# You will need to download the models first
# Glove is smaller and might be esier to work with initially 
# download here: [GloVe: Global Vectors for Word Representation](https://nlp.stanford.edu/projects/glove/)
    # SKD downloaded glove.840B.300d (Common Crawl (840B tokens, 2.2M vocab, cased, 300d vectors, 2.03 GB download)
# Google world news vectors:
# download here: [GoogleNews-vectors-negative300.bin.gz - Google Drive](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing)

# Load models 

## Glove	

import os
from pathlib import Path
import gensim
from gensim.models import Word2Vec
import numpy as np
import pandas as pd

this_file_path = os.path.abspath(__file__)
project_root = os.path.split(this_file_path)[0]
path = os.path.join(project_root, 'wordvec') + '/'

from gensim.scripts.glove2word2vec import glove2word2vec
glove_input_file = os.path.join(path, 'glove.6B/glove.6B.100d.txt')
word2vec_output_file = os.path.join(path, 'glove.6B.100d.txt.word2vec')
glove2word2vec(glove_input_file, word2vec_output_file)

from gensim.models import KeyedVectors
# load the Stanford GloVe model
filename = word2vec_output_file
glove_model = KeyedVectors.load_word2vec_format(filename, binary=False)

# calculate: (king - man) + woman = ?
result = glove_model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
result = glove_model.most_similar(positive=['london', 'germany'], negative=['berlin'], topn=1)

print(result)

# import numpy as np

# with open('LOCATION/glove.6B.50d.txt', 'rb') as lines:
#    w2v_glove = {line.split()[0]: np.array(map(float, line.split()[1:]))
#            for line in lines}

## google

# w2v_google = gensim.models.Word2Vec.load_word2vec_format(‘WHERE YOU DOWNLOADED THE MODEL/GoogleNews-vectors-negative300.bin', binary=True)  
from gensim.models import KeyedVectors

filename = os.path.join(path, 'GoogleNews-vectors-negative300.bin')

google_model = KeyedVectors.load_word2vec_format(filename, binary=True)

## Then you can inspect the models 
result = google_model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
result = google_model.most_similar(positive=['sushi', 'italian'], negative=['pizza'], topn=1)

print(result)

###### Our archive corpus

import preprocess as pr

path_corpus = '/Users/sarahdreier/OneDrive/Incubator/NI_docs/'

## Load txt document file names
ocr_text = pr.text_preprocess(path_corpus)
ocr_text.files

# run through function to gather all text (as dictionary)
ocr_text_corpus = ocr_text.nvivo_ocr()
len(ocr_text_corpus)

# Convert to Dataframe
ocr_corpus = pd.DataFrame(ocr_text_corpus.items())
ocr_corpus.columns = ['img_file', 'raw_text']

# Function to clean text
def clean_func(column, df):
    new_col = column.str.lower()
    new_col = new_col.replace(r"\n", " ", regex=True)
    #new_col = new_col.replace(r"[^0-9a-z #+_]", "", regex=True)
    new_col = new_col.replace(r"[^a-z #+_]", "", regex=True)
    new_col = new_col.replace(r"#", " ", regex=True)
    new_col = new_col.replace(r'\b\w{1,3}\b', '', regex=True)
    df['clean_text'] = new_col
    return(df)

clean_func(ocr_corpus['raw_text'], ocr_corpus) 

# Subset to pages that contain a justification
j_path = '/Users/sarahdreier/OneDrive/Incubator/NIreland_NLP'
df = pd.read_csv(os.path.join(j_path, 'justifications_clean_text_ohe.csv'))
just_imgs = np.ndarray.tolist(df['img_file_orig'].unique())
ocr_corpus_subset = ocr_corpus.loc[ocr_corpus['img_file'].isin(just_imgs)]

# Count the number of unique tokens in the subseted corpus
#sentences = ocr_corpus['clean_text']
sentences = ocr_corpus_subset['clean_text']

from keras.preprocessing.text import Tokenizer
tokenizer = Tokenizer()
tokenizer.fit_on_texts(sentences)
sequences = tokenizer.texts_to_sequences(sentences)

word_index = tokenizer.word_index # word and their token # ordered by most frequent
print('Found %s unique tokens.' % len(word_index))
type(word_index) ### Move this from a dictionary to a string and see if that fixes the model.
text = str(word_index)
model = Word2Vec(tokens_sentences)

words = list(model.wv.vocab)
print(words)
len(words)