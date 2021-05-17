import pathlib
import os
import logging
import time
from typing import Union, Iterable, Dict, List

import numpy as np
import tensorflow as tf

from config.preprocessing import INPUT_SIZE
from config.model import ENCODING_CLASS
from src.preprocessing import img_to_numpy, _preprocess

MOUNTED_MODELS_ROOT = pathlib.Path("/storage")


class SeldonModel:
    """
    Model template. You can load your model parameters in __init__ from a location
    accessible at runtime.
    """

    def __init__(self) -> None:
        """
        Add any initialization parameters. These will be passed at runtime from
        the graph definition parameters defined in your seldondeployment kubernetes
        resource manifest.
        """
        self.logger = logging.getLogger(__name__)
        self.last_prediction_time = 0.0
        self.predictions_made = 0

        model_path = self._find_model()
        self.logger.info(f"Loading model at '{str(model_path)}'")
        self.model: tf.keras.models.Sequential = tf.keras.models.load_model(model_path)
        self.logger.info("Model loaded.")

    def predict(
        self, X: np.ndarray, names: Iterable[str], meta: Dict = None
    ) -> Union[str]:
        """
        Return a prediction.

        Parameters
        ----------
        X : array-like
        feature_names : array of feature names (optional)
        """
        pred_started = self._cur_time_millisecs()
        self.logger.debug("Predict called - will run idenity function")
        result = self._predict(X, names, meta)
        self.last_prediction_time = self._cur_time_millisecs() - pred_started
        self.predictions_made += 1
        return result

    def metrics(self) -> List[Dict[str, Union[str, int, float]]]:
        return [
            # a counter which will increase by the given value
            {
                "type": "GAUGE",
                "key": "predictions_made",
                "value": self.predictions_made,
            },
            # a timer which will add sum and count metrics - assumed millisecs
            {
                "type": "TIMER",
                "key": "last_prediction_time",
                "value": self.last_prediction_time,
            },
        ]

    def _find_model(self) -> pathlib.Path:
        env_path = os.environ.get("MODEL_PATH")
        if not env_path:
            # https://github.com/neuro-inc/neuro-extras/blob/master/neuro_extras/seldon.py#L117
            model_path = list(MOUNTED_MODELS_ROOT.glob("**/*.h5"))[0]
        else:
            model_path = pathlib.Path(env_path)
            if not model_path.is_file():
                model_path = list(model_path.glob("**/*.h5"))[0]

        return model_path

    def _cur_time_millisecs(self) -> int:
        return int(round(time.time() * 1000))

    def _predict(self, X: np.ndarray, names: Iterable[str], meta: Dict = None) -> str:
        x = img_to_numpy(X, target_size=INPUT_SIZE)
        x = _preprocess(x)
        model_prediction: tf.Tensor = self.model(x)
        model_prediction: list = model_prediction.numpy().flatten().tolist()
        predict_encoding = model_prediction.index(max(model_prediction))
        return ENCODING_CLASS.get(predict_encoding, "")


seldon_model = SeldonModel
