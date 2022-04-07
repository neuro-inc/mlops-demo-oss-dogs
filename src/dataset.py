import logging
from pathlib import Path
import math
from src.preprocessing import img_to_numpy
from typing import List, Mapping
from random import shuffle
from keras.utils import Sequence
from urllib.parse import urlparse
from config.preprocessing import INPUT_SIZE
from config.model import BATCH_SIZE
import numpy as np
from keras.applications.vgg16 import preprocess_input


class DogsDataset(Sequence):
    def __init__(
        self,
        dataset_path: Path,
        images: List[str],
        labels: List[str],
        class_encoding: Mapping[str, int],
        batch_size=BATCH_SIZE,
    ) -> None:
        super().__init__()
        assert len(images) == len(labels)
        self.dataset_path = dataset_path
        self.images = images
        self.labels = labels
        self.class_encoding = class_encoding
        self.sample_count = len(self.images)
        self.indices = list(range(self.sample_count))
        shuffle(self.indices)
        self.batch_size = batch_size

    def on_epoch_end(self, epoch=None, logs=None) -> None:
        shuffle(self.indices)

    def __len__(self) -> int:
        return math.ceil(len(self.images) / self.batch_size)

    def __getitem__(self, i: int):
        batch_indices = self.indices[i * self.batch_size : (i + 1) * self.batch_size]

        images = []
        labels = []

        for bi in batch_indices:
            img_name = Path(urlparse(self.images[bi]).path).name
            img_path = self.dataset_path / img_name
            print(f'img_name={img_name} img_path={img_path} url={self.images[bi]}')
            x = img_to_numpy(img_path, target_size=INPUT_SIZE)
            x = preprocess_input(x)
            images.append(x)

            labels.append(self.class_encoding[self.labels[bi]])
            print(f'labels[bi]={self.labels[bi]}')

        return (np.array(images), np.array(labels))
