import pathlib
import os
import logging
import time
from typing import Union, Iterable, Dict, List

import numpy as np
import tensorflow as tf
from keras.applications import VGG16

from config.preprocessing import INPUT_SIZE
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
        self.avg_predict_time = 0.0

        model_path = self._find_model()
        self.logger.info(f"Loading model at '{str(model_path)}'")
        self.model: tf.keras.models.Sequential = tf.keras.models.load_model(model_path)
        self.conv_base_preprocessor = VGG16(
            weights="imagenet", include_top=False, input_shape=(*INPUT_SIZE, 3)
        )
        self.logger.info("Model loaded.")

    def predict(
        self, X: np.ndarray, names: Iterable[str], meta: Dict = None
    ) -> Union[np.ndarray, List, str, bytes]:
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
        time_elapsed = self._cur_time_millisecs() - pred_started
        self.avg_predict_time = (self.avg_predict_time + time_elapsed) / 2
        return result

    def metrics(self) -> List[Dict[str, Union[str, int, float]]]:
        return [
            {
                "type": "COUNTER",
                "key": "mycounter",
                "value": 1,
            },  # a counter which will increase by the given value
            {
                "type": "GAUGE",
                "key": "mygauge",
                "value": 100,
            },  # a gauge which will be set to given value
            {
                "type": "TIMER",
                "key": "mytimer",
                "value": 20.2,
            },  # a timer which will add sum and count metrics - assumed millisecs
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

    def _predict(
        self, X: np.ndarray, names: Iterable[str], meta: Dict = None
    ) -> Union[np.ndarray, List, str, bytes]:

        x = img_to_numpy(X, target_size=INPUT_SIZE)
        x = _preprocess(x)
        features = self.conv_base_preprocessor.predict(x)

        model_prediction: tf.Tensor = self.model(features)
        return model_prediction.numpy().tolist()


seldon_model = SeldonModel
