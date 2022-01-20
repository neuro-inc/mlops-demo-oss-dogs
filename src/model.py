import tensorflow as tf
from keras import models, layers
from keras.applications.vgg16 import VGG16

from config.preprocessing import INPUT_SIZE
from config.model import INPUT_LAYER_SHAPE


def get_model() -> models.Model:
    model = models.Sequential()
    encoder = VGG16(weights="imagenet", include_top=False, input_shape=(*INPUT_SIZE, 3))
    encoder.trainable = False
    model.add(encoder)
    model.add(layers.Flatten(input_shape=INPUT_LAYER_SHAPE))
    model.add(layers.Dense(256, activation="relu", input_shape=INPUT_LAYER_SHAPE))
    model.add(layers.Dense(2, activation="softmax"))

    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss="sparse_categorical_crossentropy",
        metrics=["acc"],
    )

    model.summary()

    return model
