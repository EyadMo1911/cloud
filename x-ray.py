# ===================== [1. Import Libraries] =====================
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import numpy as np
import os

# ===================== [2. Auto Paths (same folder)] =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

train_dir = os.path.join(BASE_DIR, "DATA", "train")
valid_dir = os.path.join(BASE_DIR, "DATA", "validation") 
model_path = os.path.join(BASE_DIR, "medical_diagnosis_model.h5")

# ===================== [3. Check dataset] =====================
if not os.path.exists(train_dir):
    raise FileNotFoundError(f"Train folder not found: {train_dir}")

if not os.path.exists(valid_dir):
    raise FileNotFoundError(f"Validation folder not found: {valid_dir}")

print("📂 Dataset loaded successfully!")

# ===================== [4. Train or Load Model] =====================
if not os.path.exists(model_path):

    print("🔧 Training model for the first time...")

    # ===================== [Data Augmentation] =====================
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    valid_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(160, 160),
        batch_size=32,
        class_mode='categorical'
    )

    valid_generator = valid_datagen.flow_from_directory(
        valid_dir,
        target_size=(160, 160),
        batch_size=32,
        class_mode='categorical'
    )

    num_classes = len(train_generator.class_indices)
    print("Classes:", train_generator.class_indices)

    # ===================== [Base Model] =====================
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(160, 160, 3)
    )
    base_model.trainable = False

    # ===================== [Head] =====================
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # ===================== [Callbacks] =====================
    callbacks = [
        EarlyStopping(monitor='val_accuracy', patience=7, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-7),
        ModelCheckpoint("best_model.h5", monitor='val_accuracy', save_best_only=True)
    ]

    # ===================== [Train] =====================
    model.fit(
        train_generator,
        validation_data=valid_generator,
        epochs=20,
        callbacks=callbacks
    )

    # ===================== [Save Model] =====================
    model.save(model_path)
    print("✅ Model trained and saved.")

else:
    print("✅ Loading pre-trained model...")
    model = load_model(model_path)