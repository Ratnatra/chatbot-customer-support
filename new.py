import random
import json
import pickle
import numpy as np
import tensorflow as tf
import nltk

from nltk.stem import WordNetLemmatizer
from keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json', encoding='utf-8').read())

words = []
classes = []
documents = []
ignoreLetters = ['?','!','.',',']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])
            
words = [lemmatizer.lemmatize(word) for word in words if word not in ignoreLetters]
words = sorted(set(words))

classes = sorted(set(classes))
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []
outputEmpty = [0]*len(classes)

for document in documents:
    bag = []
    wordPattern = document[0]
    wordPattern = [lemmatizer.lemmatize(word.lower()) for word in wordPattern]
    for word in words:
        bag.append(1 if word in wordPattern else 0)
    outputRow = list(outputEmpty)
    outputRow[classes.index(document[1])] = 1
    training.append(bag + outputRow)

random.shuffle(training)
training = np.array(training, dtype=np.float32)

trainX = training[:, :len(words)]
trainY = training[:, len(words):]

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Dense(128, input_shape=(len(trainX[0],),), activation='relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(64, activation='relu'))
model.add(tf.keras.layers.Dense(len(trainY[0],), activation='softmax'))

sgd = tf.keras.optimizers.SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)

model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
hist = model.fit(np.array(trainX), np.array(trainY), epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)       
print("Executed")

