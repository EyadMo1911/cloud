import tensorflow as tf
import numpy as np
import nltk, random, json, pickle, os
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()
nltk.download('punkt', quiet=True)

# ================= LOAD DATA =================
with open("train5.json", encoding="utf-8") as file:
    data = json.load(file)

with open("data.pickle", "rb") as f:
    words, labels, training, output = pickle.load(f)

# ================= MODEL =================
model = tf.keras.Sequential([
    tf.keras.layers.Dense(8, input_shape=(len(training[0]),), activation='relu'),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(len(output[0]), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

weights_file = "abosa.weights.h5"

if os.path.exists(weights_file):
    model.load_weights(weights_file)
else:
    model.fit(np.array(training), np.array(output), epochs=1000, batch_size=8)
    model.save_weights(weights_file)

# ================= NLP =================
def bag_of_words(sentence):
    bag = [0]*len(words)
    s_words = nltk.word_tokenize(sentence.lower())
    s_words = [stemmer.stem(w) for w in s_words]

    for w in s_words:
        if w in words:
            bag[words.index(w)] = 1

    return np.array(bag)

# ================= MAIN FUNCTION (IMPORTANT) =================
def get_response(message):
    bow = bag_of_words(message)
    results = model.predict(np.array([bow]))[0]

    max_index = np.argmax(results)
    tag = labels[max_index]

    if results[max_index] > 0.7:
        for intent in data["intents"]:
            if intent["tag"] == tag:
                return random.choice(intent["responses"])

    return 
