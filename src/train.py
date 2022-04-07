import argparse
import random as rn
import pathlib
from src.dataset import DogsDataset
from typing import Optional, List

import tensorflow as tf
import numpy as np
import mlflow
from sklearn.model_selection import train_test_split

from src.preprocessing import split_json
from src.model import get_model
from config.model import (
    CLASS_ENCODING,
    RD_SEED,
    SPLIT_SEED,
    TEST_SIZE,
    EPOCHS,
)


def train(args: argparse.Namespace) -> None:
    """
    Training script copied from here
    https://github.com/elleobrien/Dog_Breed_Classifier/blob/master/breed_classifier.py
    """
    # todo: try PYTHONHASHSEED
    np.random.seed(RD_SEED)
    tf.random.set_seed(RD_SEED)
    rn.seed(RD_SEED)

    mlflow.log_metric("test_size", TEST_SIZE)
    images, labels = split_json(args.data_description)

    X_train, X_test, Y_train, Y_test = train_test_split(
        images, labels, test_size=TEST_SIZE, stratify=labels, random_state=SPLIT_SEED
    )

    train_ds = DogsDataset(
        args.data_dir,
        X_train,
        Y_train,
        CLASS_ENCODING,
    )
    validation_ds = DogsDataset(
        args.data_dir,
        X_test,
        Y_test,
        CLASS_ENCODING,
    )

    model = get_model()

    print(train_ds)

    history = model.fit(
        train_ds,
        epochs=EPOCHS,
        validation_data=validation_ds,
    )

    final_val_acc = history.history["val_acc"][-1]

    print("Validation Accuracy: %1.3f" % (final_val_acc))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sample training script")
    parser.add_argument(
        "-d", "--data_dir", required=True, type=pathlib.Path, help="Path to the dataset"
    )
    parser.add_argument(
        "-f",
        "--data_description",
        required=True,
        type=pathlib.Path,
        help="Path to the dataset description file",
    )
    return parser


def get_args(provided_args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = get_parser()
    args = parser.parse_args(provided_args)

    if not args.data_dir.exists():
        raise ValueError(f"{args.data_dir} does not exist!")
    if not args.data_dir.is_dir():
        raise ValueError(f"{args.data_dir} is not a directory!")
    if not args.data_description.exists():
        raise ValueError(f"{args.data_description} does not exist!")
    if not args.data_description.is_file():
        raise ValueError(f"{args.data_dir} is not a file!")

    return args


if __name__ == "__main__":
    mlflow.keras.autolog()
    args = get_args()
    train(args)
