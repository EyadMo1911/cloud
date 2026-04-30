
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16

# ===================== [Auto Paths - same folder] =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

train_dir = os.path.join(BASE_DIR, "DATA", "train")
validation_dir = os.path.join(BASE_DIR, "DATA", "testing")
model_path = os.path.join(BASE_DIR, "disease_classifier_model.h5")

# ===================== [Check dataset] =====================
if not os.path.exists(train_dir):
    raise FileNotFoundError(f"Train folder not found: {train_dir}")

if not os.path.exists(validation_dir):
    raise FileNotFoundError(f"Validation folder not found: {validation_dir}")

print("Dataset found successfully!")

# ===================== [Data Augmentation] =====================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

validation_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='categorical'
)

validation_generator = validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='categorical'
)

class_indices = train_generator.class_indices
print("Classes:", class_indices)

# ===================== [Base Model VGG16] =====================
base_model = VGG16(
    weights='imagenet',
    include_top=False,
    input_shape=(150, 150, 3)
)

base_model.trainable = False

# ===================== [Custom Head] =====================
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(len(class_indices), activation='softmax')
])

# ===================== [Compile Model] =====================
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ===================== [Train Model] =====================
history = model.fit(
    train_generator,
    epochs=20,
    validation_data=validation_generator
)

# ===================== [Save Model] =====================
model.save(model_path)
print(f"Model saved at: {model_path}")

# ===================== [Save class labels] =====================
class_labels = {v: k for k, v in class_indices.items()}

labels_path = os.path.join(BASE_DIR, "class_labels.npy")
np.save(labels_path, class_labels)


