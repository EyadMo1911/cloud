# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import nltk, random, json, pickle, io
from nltk.stem.lancaster import LancasterStemmer
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

# ================== NLP (CHAT) ==================
stemmer = LancasterStemmer()
nltk.download('punkt', quiet=True)

with open("train5.json", encoding="utf-8") as file:
    data = json.load(file)

with open("data.pickle", "rb") as f:
    words, labels, training, output = pickle.load(f)

chat_model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(8, input_shape=(len(training[0]),), activation='relu'),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(len(output[0]), activation='softmax')
])

chat_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
chat_model.load_weights("abosa.weights.h5")


def bag_of_words(s, words):
    bag = [0]*len(words)
    s_words = s.lower().split()
    s_words = [stemmer.stem(w) for w in s_words]

    for w in s_words:
        if w in words:
            bag[words.index(w)] = 1
    return np.array(bag)


def chat_reply(msg):
    results = chat_model.predict(np.array([bag_of_words(msg, words)]))[0]
    idx = np.argmax(results)
    tag = labels[idx]

    if results[idx] > 0.7:
        for t in data["intents"]:
            if t["tag"] == tag:
                return random.choice(t["responses"])

    return "Sorry, I didn't understand that."


@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"]
    return jsonify({"response": chat_reply(msg)})


# ================== SKIN MODEL ==================
skin_model = load_model("disease_classifier_best.keras")

skin_classes = [
    "Acne","Actinic Keratosis","Basal cell carcinoma",
    "Eczema","Healthy","Rosacea"
]

skin_info = {
    "Acne": {"diagnosis": "Acne detected", "treatment": "Topical creams", "doctor": "Dermatologist"},
    "Actinic Keratosis": {"diagnosis": "Precancerous lesion", "treatment": "Cryotherapy", "doctor": "Dermatologist"},
    "Basal cell carcinoma": {"diagnosis": "Skin cancer detected", "treatment": "Surgery", "doctor": "Oncologist"},
    "Eczema": {"diagnosis": "Skin inflammation", "treatment": "Steroid creams", "doctor": "Dermatologist"},
    "Healthy": {"diagnosis": "No disease detected", "treatment": "None", "doctor": "None"},
    "Rosacea": {"diagnosis": "Chronic redness", "treatment": "Antibiotics", "doctor": "Dermatologist"}
}


@app.route("/predict_face", methods=["POST"])
def predict_face():
    file = request.files["file"]
    img = load_img(io.BytesIO(file.read()), target_size=(224,224))
    arr = img_to_array(img)
    arr = np.expand_dims(arr,0)

    pred = skin_model.predict(arr)
    idx = np.argmax(pred)
    confidence = float(np.max(pred))

    # 🔥 threshold for unknown images
    if confidence < 0.60:
        return jsonify({
            "disease": "N/A",
            "diagnosis": "Unknown image",
            "treatment": "-",
            "doctor": "-"
        })

    d = skin_classes[idx]
    info = skin_info[d]

    return jsonify({
        "disease": d,
        "diagnosis": info["diagnosis"],
        "treatment": info["treatment"],
        "doctor": info["doctor"]
    })


# ================== XRAY MODEL ==================
xray_model = load_model("medical_diagnosis_model.h5")

xray_classes = ["covid","Lung_Opacity","Normal","Viral_Pneumonia"]

xray_info = {
    "covid": {"diagnosis": "COVID-19 detected", "treatment": "Antiviral", "doctor": "Pulmonologist"},
    "Lung_Opacity": {"diagnosis": "Lung infection", "treatment": "Antibiotics", "doctor": "Pulmonologist"},
    "Normal": {"diagnosis": "Normal chest", "treatment": "None", "doctor": "None"},
    "Viral_Pneumonia": {"diagnosis": "Pneumonia detected", "treatment": "Rest", "doctor": "Pulmonologist"}
}


@app.route("/predict_xray", methods=["POST"])
def predict_xray():
    file = request.files["file"]
    img = load_img(io.BytesIO(file.read()), target_size=(160,160))
    arr = img_to_array(img)/255.0
    arr = np.expand_dims(arr,0)

    pred = xray_model.predict(arr)
    idx = np.argmax(pred)
    confidence = float(np.max(pred))

    # 🔥 unknown image rule
    if confidence < 0.60:
        return jsonify({
            "disease": "N/A",
            "diagnosis": "Unknown image",
            "treatment": "-",
            "doctor": "-"
        })

    d = xray_classes[idx]
    info = xray_info[d]

    return jsonify({
        "disease": d,
        "diagnosis": info["diagnosis"],
        "treatment": info["treatment"],
        "doctor": info["doctor"]
    })


if __name__ == "__main__":
    app.run(debug=True)