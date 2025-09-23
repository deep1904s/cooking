#!/usr/bin/env python3
"""
Train Food Classification Model
Creates models/food_classifier.h5
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import pickle
import os

# Paths
dataset_dir = "data/data1/images"
model_path = "models/food_classifier.h5"
label_map_path = "models/label_map.pkl"

# Image settings
img_size = (224, 224)
batch_size = 32

# Data generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_gen = train_datagen.flow_from_directory(
    dataset_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="training"
)

val_gen = train_datagen.flow_from_directory(
    dataset_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="validation"
)

# Save class indices (label map)
os.makedirs("models", exist_ok=True)
with open(label_map_path, "wb") as f:
    pickle.dump(train_gen.class_indices, f)

# Build model (transfer learning with MobileNetV2)
base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # freeze base model

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(len(train_gen.class_indices), activation="softmax")
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Train model
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=5
)

# Save trained model
model.save(model_path)
print(f"✅ Model saved at {model_path}")
