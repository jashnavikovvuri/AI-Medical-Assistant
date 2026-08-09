import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout

# Dataset paths
train_path = "dataset/Training"
test_path = "dataset/Testing"

# Image Generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    zoom_range=0.2,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(
    rescale=1./255
)

# Load Training Data
train_data = train_datagen.flow_from_directory(
    train_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode="categorical"
)

# Load Testing Data
test_data = test_datagen.flow_from_directory(
    test_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode="categorical"
)

# Print class order
print("\nClass Order:")
print(train_data.class_indices)

# CNN Model
model = Sequential([
    Input(shape=(224, 224, 3)),

    Conv2D(32, (3,3), activation="relu"),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(2,2),

    Conv2D(128, (3,3), activation="relu"),
    MaxPooling2D(2,2),

    Flatten(),

    Dense(128, activation="relu"),
    Dropout(0.5),

    Dense(4, activation="softmax")
])

# Compile Model
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("\nTraining Started...\n")

# Train Model
history = model.fit(
    train_data,
    validation_data=test_data,
    epochs=10
)

# Create model folder
os.makedirs("model", exist_ok=True)

# Save Model
model.save("model/brain_tumor_model.h5")

print("\n===================================")
print("Model saved successfully!")
print("Location: model/brain_tumor_model.h5")
print("===================================")