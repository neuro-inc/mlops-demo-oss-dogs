import io
import json
import logging
import numpy as np
from pathlib import Path
from urllib.parse import urlparse
from typing import Mapping, Tuple, Union

from keras.preprocessing import image
from keras.applications import VGG16
from keras.applications.vgg16 import preprocess_input
from PIL import Image, ImageOps

from config.preprocessing import INPUT_SIZE
from config.model import INPUT_LAYER_SHAPE


def extract_features_labels(
    dataset_path: Path,
    dataset_description: Path,
    class_encoding: Mapping[str, int],
) -> Tuple[np.ndarray, np.ndarray]:
    # Load in the convolutional base
    conv_base = VGG16(
        weights="imagenet", include_top=False, input_shape=(*INPUT_SIZE, 3)
    )

    ds_descr = json.loads(dataset_description.read_text())

    sample_count = len(ds_descr)
    features = np.zeros(
        shape=(sample_count, *INPUT_LAYER_SHAPE)
    )  # Must be equal to the output of the convolutional base
    labels = np.zeros(shape=(sample_count))

    # Pass data through convolutional base

    # Stream each image from data folder and transform
    for i in range(0, sample_count):
        img_name = Path(urlparse(ds_descr[i]["image"]).path).name
        img_path = dataset_path / img_name
        x = img_to_numpy(img_path, target_size=INPUT_SIZE)
        x = _preprocess(x)

        # Predict VGG features for this image
        features[i] = conv_base.predict(x)
        # Get the class label
        label_code = ds_descr[i].get("choice")
        if label_code is None:
            logging.warning(
                f"Label is not defined for {str(img_path)}. "
                f"Task ID: {ds_descr[i]['id']}"
            )
            continue
        labels[i] = class_encoding[label_code]

        if i % 10 == 0 and i > 0:
            print("Now processing image " + str(i) + " of " + str(sample_count) + ".")

    return features, labels


def img_to_numpy(
    im: Union[str, Path, io.BytesIO, bytes, np.ndarray],
    target_size: Union[int, int],
) -> np.ndarray:
    if isinstance(im, np.ndarray):
        return im
    if isinstance(im, bytes):
        img_pil = Image.open(io.BytesIO(im))
    if isinstance(im, (str, Path, io.BytesIO)):
        img_pil = Image.open(im)
        # capture and ignore this bug:
        # https://github.com/python-pillow/Pillow/issues/3973
        try:
            img_pil = ImageOps.exif_transpose(image)
        except Exception:
            pass
    if not isinstance(im, (str, Path, io.BytesIO, bytes, np.ndarray)):
        raise ValueError(f"Unexpected input type: {type(im)}")
    # Keras does not allow to process images in form of bytes
    # https://github.com/keras-team/keras/issues/11684
    img_pil = img_pil.convert("RGB")
    img_pil = img_pil.resize(INPUT_SIZE, Image.NEAREST)
    return image.img_to_array(img_pil)


def _preprocess(X: np.ndarray) -> np.ndarray:
    X = np.expand_dims(X, axis=0)
    X = preprocess_input(X)
    return X
