import io
import json
import logging
import numpy as np
from pathlib import Path
from urllib.parse import urlparse
from typing import Tuple, Union, List

from keras.preprocessing import image
from keras.applications import VGG16
from keras.applications.vgg16 import preprocess_input
from PIL import Image, ImageOps

from config.preprocessing import INPUT_SIZE
from config.model import INPUT_LAYER_SHAPE


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


def split_json(dataset_description: Path) -> Tuple[List[str], List[int]]:
    raw_data = json.loads(dataset_description.read_text())
    images = []
    labels = []
    for item in raw_data:
        images.append(item["data"]["image"])
        labels.append(item["annotations"][0]["result"][0]["value"]["choices"][0])
    return (images, labels)
