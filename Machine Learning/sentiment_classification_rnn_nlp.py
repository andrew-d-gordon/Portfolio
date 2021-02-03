# -*- coding: utf-8 -*-
"""sentiment_classification_rnn_nlp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OUU3apQpahXblRZc6ySW-momQ4uLUlLr
"""

import tensorflow as tf
from tensorflow.keras.datasets import reuters
import matplotlib.pyplot as plt
import numpy as np
import string
import textwrap
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Embedding, Dense, Dropout, Input, LSTM, GRU, Bidirectional, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2

"""Uses the [Reuters newswire](https://keras.io/api/datasets/reuters/) classification dataset, which has text paired with 46 topics as labels. You can see what these labels represent [here](https://martin-thoma.com/nlp-reuters/)."""

(X_train, y_train), (_, _) = reuters.load_data()

# https://stackoverflow.com/questions/42821330/restore-original-text-from-keras-s-imdb-dataset
# Needed to encode our own reviews later

word_dict = reuters.get_word_index()
word_dict = {k:(v+3) for k,v in word_dict.items()}
word_dict["<PAD>"] = 0
word_dict["<START>"] = 1
word_dict["<UNK>"] = 2
word_dict["<UNUSED>"] = 3

vocab_size = len(word_dict.keys())

# Needed to decode training data into readable text

inverse_word_dict = {value:key for key,value in word_dict.items()}

X_train = np.array(X_train)
X_train = pad_sequences(X_train)

max_sequence_len = X_train[0].shape[0]
print('Padded to longest sequence length: ', max_sequence_len)

y_train = to_categorical(y_train, 46)
y_train = np.array(y_train)

print('Number of words in vocabulary: ', vocab_size)

def encode_text(text, word_dict, maxlen):
  encoded_text = []
  for raw_word in text.split(' '):
    word = raw_word.strip().strip(string.punctuation).lower()
    if word is '' or word is '\n':
      continue
    try:
      encoded_text.append(word_dict[word])
    except KeyError as e:
      # raise KeyError(f'{e} not in word dictionary, text not encoded.')
      continue
  return pad_sequences(np.array(encoded_text).reshape(1,-1), maxlen=maxlen)

def decode_text(encoded_text, inverse_word_dict):
  sentence = []
  for encoded_word in encoded_text:
    if encoded_word == 0:
      continue
    sentence.append(inverse_word_dict[encoded_word])
  w = textwrap.TextWrapper(width=120,break_long_words=False,replace_whitespace=False)
  return '\n'.join(w.wrap(' '.join(sentence)))

"""A look at an article in the training data:"""

idx = 144

print(decode_text(X_train[idx], inverse_word_dict), end='\n\n')

print('Topic: ', y_train[idx])

"""Creates model using an RNN layer (LSTM as opposed to GRU). Aims to achieve at least 60% validation accuracy in 10 epochs or less:"""

input_layer = Input(shape=(max_sequence_len))
x = Embedding(vocab_size, 64)(input_layer)

x = LSTM(64)(x)

x = Dense(16384, activation='relu')(x) # 1024 on both, .2 on both, lr .001
x = Dropout(0.8)(x) #.1, or .15

x = Dense(46, activation='softmax')(x)
reuters_model = Model(input_layer, x) #sentiment at the moment

# Reminder: We have 46 categories. What final activation do we need to use?

"""Compile your model and display the summary:"""

loss = tf.keras.losses.CategoricalCrossentropy()

opt = tf.keras.optimizers.Adam(2e-3) #tf.keras.optimizers.RMSprop(lr = 0.001) # 

metrics = ['accuracy']

reuters_model.compile(loss=loss,
              optimizer=opt,
              metrics=metrics)

reuters_model.summary()

"""Train your model:"""

batchsize = 200

history = reuters_model.fit(X_train, y_train, batch_size=batchsize, epochs=10, validation_split=0.2, shuffle=True)

"""Plot the training and validation losses and accuracies:"""

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'test'])
plt.show()

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(['train', 'test'])
#plt.ylim([0,1])
plt.show()