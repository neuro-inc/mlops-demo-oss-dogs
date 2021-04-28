from keras import models, layers, optimizers

from config.model import INPUT_LAYER_SHAPE


def get_model() -> models.Sequential:
    # Define fully connected feed-forward model and its hyperparameters
    model = models.Sequential()
    model.add(layers.Flatten(input_shape=INPUT_LAYER_SHAPE))
    model.add(layers.Dense(256, activation="relu", input_shape=INPUT_LAYER_SHAPE))
    model.add(layers.Dense(1, activation="sigmoid"))
    model.summary()

    # Compile model
    model.compile(
        optimizer=optimizers.Adam(), loss="binary_crossentropy", metrics=["acc"]
    )
    return model
