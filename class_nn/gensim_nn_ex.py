## Gensim how-to and test with subset 
import pandas as pd
import os
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics import classification_report, confusion_matrix

this_file_path = os.path.abspath(__file__)
project_root = os.path.split(os.path.split(this_file_path)[0])[0]

sys.path.append(project_root)
import preprocess as pr

path_corpus = os.path.join(project_root, "orig_text_data/sample_data/") 

# load the training data 
df = pd.read_csv(os.path.join(project_root, 'justifications_clean_text_ohe.csv'))

# Collapse justification categories from 12 to 6 -- approach #2
df['just_category_6'] = df['justification_cat']
df['just_category_6'] = df['just_category_6'].replace(['J_Emergency-Policy', 'J_Intelligence', 'J_Last-resort', 'J_Utilitarian-Deterrence', 'J_Law-and-order'], 'J_Security')
df['just_category_6'] = df['just_category_6'].replace(['J_Legal_Procedure'], 'J_Legal')
df['just_category_6'] = df['just_category_6'].replace(['J_Political-Strategic'], 'J_Political')
df['just_category_6'] = df['just_category_6'].replace(['J_Denial', 'J_Intl-Domestic_Precedent'], 'J_DenyHRVio') #
df['just_category_6'] = df['just_category_6'].replace(['J_Development-Unity'], 'J_Misc')
df['just_categories'] = df['just_category_6']
#df['just_categories'] = df['justification_cat'] # try it with original 12 categories


# Create a unique number id for each justification category
col = ['just_categories', 'clean_text'] 
df = df[col]
df = df[pd.notnull(df['clean_text'])]
df.columns = ['just_categories', 'clean_text']
df['category_id'] = df['just_categories'].factorize()[0]
category_id_df = df[['just_categories', 'category_id']].drop_duplicates().sort_values('category_id')
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['category_id', 'just_categories']].values)
df.head()


## Load corpus document file names
ocr_text = pr.text_preprocess(path_corpus)
ocr_text.files

# run through function to gather all text (as dictionary)
ocr_text_corpus = ocr_text.nvivo_ocr()

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

test = clean_func(ocr_corpus['raw_text'], ocr_corpus) 

text = list(test['clean_text'])

import nltk 
from nltk import word_tokenize

tokenized_docs = [word_tokenize(i) for i in text]
for i in tokenized_docs:
    print(i)

model = Word2Vec(tokenized_docs, min_count=1) # this should train the model
print(model)
words = list(model.wv.vocab) # this should show the words in the model, but it is showing characters rather than words
print(sorted(words))
len(words)

print(model['terrorism']) # will show embeddings 
model.wv.most_similar('terrorism')

# save model
model_name = 'test_embedding_w2v.txt'
model.wv.save_word2vec_format(model_name, binary=False)
# 

#######################################
# ADD YOUR TXT MODEL HERE REPLACE : "test_embedding_w2v.txt"
#######################################
# NOW WE CAN USE THE MODEL (LOAD .bin)
# use model
embeddings_index = {}
f = open(os.path.join(project_root, "class_nn/archive_corpus_embedding_w2v_big.txt"), encoding='utf-8') # Embeddings from full corpus (raw/complete)
#f = open(os.path.join(project_root, "class_nn/archive_corpus_embedding_w2v.txt"), encoding='utf-8') # Embeddings from full corpus (cleaned/reduced)
#f = open(os.path.join(project_root, "class_nn/test_embedding_w2v.txt"), encoding='utf-8') # Embeddings from sample corpus
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:])
    embeddings_index[word] = coefs
f.close() 
embeddings_index #corpus data
len(embeddings_index) #15,523 words

# load .bin 
#from gensim.models import KeyedVectors
#word_vectors = KeyedVectors.load_word2vec_format(os.path.join(project_root, "class_nn/archive_corpus_w2v_model.bin"), binary=True)

# Model will take in a group of sentences per class 
# convert  into tokenized vector
# You will have a tokenized vector for each entry of varying sizes
#sentences = df['stem_text'].values # include stopwords, stemmed
sentences = df['clean_text'] # include stopwords, unstemmed
y = df['just_categories']
df['just_categories'].values

from keras.preprocessing.text import Tokenizer
tokenizer = Tokenizer()
tokenizer.fit_on_texts(sentences)
sequences = tokenizer.texts_to_sequences(sentences)

word_index = tokenizer.word_index # word and their token # ordered by most frequent
print('Found %s unique tokens.' % len(word_index))

max_words = 5620 # total words of vocabulary we will consider

num_words = [len(words.split()) for words in sentences]
max_seq_len = max(num_words) + 1

# More than one way of doing this
# another way
import string
from nltk.tokenize import word_tokenize

just_entries = list()
sentences = df['clean_text'].values.tolist()

for group in sentences:
    tokens = word_tokenize(group)
    just_entries.append(tokens)

len(just_entries)
just_entries
######

# paddding ... we want to make sure we have a uniform length tensor to input in the model
from keras.preprocessing.sequence import pad_sequences

text_vector_pad = pad_sequences(sequences, maxlen=max_seq_len+1)

#
# We can loon at both input and output shapes
# ourput needs processing from categorical string
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from keras import utils

encoder = LabelEncoder()
encoder.fit(y)
labels = encoder.transform(y)

num_classes = np.max(labels) + 1 #index at 0
labels = utils.to_categorical(labels, num_classes)

print('Shape of data tensor:', text_vector_pad.shape)
print('Shape of label tensor:', labels.shape)

# create label reference
y_labels = np.argmax(labels, axis=1)
y_labels_s = pd.Series(y_labels)
y_labels_s.value_counts(normalize=True) * 100

len(y)
y.value_counts()
y.value_counts(normalize=True) * 100
# PREP WORD EMBEDDINGS
#embeddings_index = # or load the w2v model

# you specify this when you train the embeddings (i think default is 100) google has 300
num_words = max_words + 1 # vocabulary_size
embedding_dim = 100
embedding_matrix = np.zeros((num_words, embedding_dim))

for word, i in word_index.items():
	embedding_vector = embeddings_index.get(word)
	if embedding_vector is not None:
		embedding_matrix[i] = embedding_vector

len(embedding_matrix)
embedding_matrix.shape

# check how many zero entries...
nonzero_elements = np.count_nonzero(np.count_nonzero(embedding_matrix, axis=1))
nonzero_elements / max_words

# mostly zero entries
embedding_matrix[9]
embedding_matrix[15]

# ADD FULL W2V MODEL fix to work .bin or change to .txt
# num_words = max_words + 1 # vocabulary_size
# embedding_dim = 100
# embedding_matrix = np.zeros((num_words, embedding_dim))

# for word, i in word_index.items():
# 	embedding_vector = embeddings_index.get(word)
# 	if embedding_vector is not None:
# 		embedding_matrix[i] = embedding_vector

# len(embedding_matrix)
# embedding_matrix.shape

########CHECK THIS .bin 
# for word, i in word_index.items():
#    if i>max_words:
#        continue
#    try:
#        embedding_vector = word_vectors[word]
#        embedding_matrix[i] = embedding_vector
#    except KeyError:
#        embedding_matrix[i]=np.random.normal(0,np.sqrt(0.25),embedding_dim)
#########

# check how many zero entries...
# nonzero_elements = np.count_nonzero(np.count_nonzero(embedding_matrix, axis=1))
# nonzero_elements / max_words

### Modeling part 
# split training data into test, validation
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(text_vector_pad, labels, stratify=labels,test_size=0.2, random_state = 42)



train_labels = np.argmax(y_train, axis=1)
train_labels_s = pd.Series(train_labels)
train_labels_s.value_counts(normalize=True) * 100
test_labels = np.argmax(y_test, axis=1)
test_labels_s = pd.Series(test_labels)
test_labels_s.value_counts(normalize=True) * 100
# invert first example
from numpy import array
from numpy import argmax
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()

inverted = label_encoder.inverse_transform([argmax(y_train[0, :])])
y_test.value_counts()
# CNN Paper 
# Setting parameters for the NN
nb_filters = 128
filter_size_a = 3
drop_rate = 0.5
my_optimizer = 'adam'

from keras.layers import Input, Embedding, Dropout, Conv1D, GlobalMaxPooling1D, Dense, Concatenate, MaxPooling1D, Flatten
from keras.models import Model, load_model

## Build the neural network

my_input = Input(shape=(max_seq_len + 1,))

embedding = Embedding(num_words, # vocab size, including the 0-th word used for padding
                        embedding_dim,
                        weights=[embedding_matrix], # we pass our pre-trained embeddings
                        input_length=max_seq_len + 1,
                        trainable=False
                        )(my_input)

# Kernel size is how big your window is. Putting x number of words into the NN together at a time from each sentence.
x = Conv1D(filters = nb_filters, kernel_size = filter_size_a,
    activation = 'relu',)(embedding)

x = MaxPooling1D(pool_size=5)(x)

# You can add many more of these Conv + Max_pooling 

x = Flatten()(x)
#### ENDS CONVOLUTIONS 

x = Dense(128, activation='relu')(x)

prob = Dense(6, activation = 'softmax',)(x)
#prob = Dense(12, activation = 'softmax',)(x)

model = Model(my_input, prob)
    
model.compile(loss='categorical_crossentropy', optimizer = my_optimizer,
    metrics = ['accuracy']) 

x = model.fit(x_train, y_train, # Target vector
    epochs=20, # Three epochs
    verbose=1, # No output
    batch_size=100, # Number of observations per batch
    validation_data=(x_test, y_test))

### Making predictions
from sklearn.metrics import classification_report

y_pred = model.predict(x_test)
pred_labels = np.argmax(y_pred, axis=-1)
from sklearn import preprocessing

lb = preprocessing.LabelBinarizer()

pred_labels = lb.fit_transform(pred_labels)

print(classification_report(y_test, pred_labels))
len(y_test)


Xnew = ['internment of individuals will continue to mitigate security risks']

tokenizer_test = Tokenizer()
tokenizer_test.fit_on_texts(Xnew)
test_sequences = tokenizer.texts_to_sequences(Xnew)

test_data = pad_sequences(test_sequences, maxlen=max_seq_len+1)
test_data
predictions = model.predict(test_data)
predictions

###
label_dict = y.factorize()
label_names = list(label_dict[1])

label_values = list(range(0,6))
#label_values = list(range(0,12))

labels_index = dict(zip(label_names, label_values))

score_dict = {label_index: predictions[0][idx] for idx, label_index in enumerate(labels_index)}

score_dict

###
# this part is from github...link?
#matrix = confusion_matrix(y_test.argmax(axis=1), y_pred.argmax(axis=1))

#this is existing code for confusious matric in the multiclass.py 
titles_options = [("Confusion matrix, without normalization", None, "not_normalized"),
                  ("Normalized confusion matrix", 'true', "normalized")]
for title, normalize, short_title in titles_options:
    disp = plot_confusion_matrix(THIS_IS_YOU_MODEL_THAT_PREDICTS_NEW_INPUTS, sentences_test, y_test,
                                 #display_labels=id_to_category,
                                 display_labels=category_to_id,
                                 cmap=plt.cm.Blues,
                                 normalize=normalize)
    disp.ax_.set_title(title)

    plt.xticks(np.arange(0, len(category_to_id)), category_to_id, rotation=60, ha='right')

    print(title)
    print(disp.confusion_matrix)

    #plt.savefig('multiclass_NB/confusion_matrix12_' + short_title + '.png')
    plt.savefig('multiclass_NB/confusion_matrix7_' + short_title + '.png')

    plt.close()

