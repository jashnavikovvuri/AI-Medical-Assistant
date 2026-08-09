import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# Load trained model
model = tf.keras.models.load_model("model/brain_tumor_model.h5")

# Class names (must match Training folder)
classes = ["glioma", "meningioma", "notumor", "pituitary"]


def predict_image(img_path):

    # Load image
    img = image.load_img(img_path, target_size=(224, 224))
    img = image.img_to_array(img)
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    # Predict
    prediction = model.predict(img, verbose=0)

    # Print probabilities in terminal
    print("\n==============================")
    print("Prediction Probabilities:")
    print(prediction)
    print("==============================\n")

    # Highest probability
    index = np.argmax(prediction)
    disease = classes[index]
    confidence = round(float(prediction[0][index] * 100), 2)

    print("Class Index :", index)
    print("Classes :", classes)
    print("Predicted Class :", disease)
    print("Confidence :", confidence)

    return disease, confidence