import os
import json
import random
import pathlib
import logging

from locust import HttpUser, task

from config.model import CLASS_ENCODING, FNAME_CLASS


IMGS_DIR = pathlib.Path(os.environ["IMGS_DIR"])
DOG_IDS = os.environ["DOG_IDS"].split(", ")
JPG_FILES = [
    x for x in IMGS_DIR.glob("**/*.jpg") if any(map(lambda id_: id_ in str(x), DOG_IDS))
]


class LoadGenerator(HttpUser):
    @task
    def prediction(self) -> None:
        target_image = random.choice(JPG_FILES)
        for file_name, breed in FNAME_CLASS.items():
            if file_name in target_image.name:
                break

        payload = dict(binData=target_image.read_bytes())
        with self.client.post("", files=payload, catch_response=True) as response:
            model_responce = json.loads(response.text)["data"]
            model_predicted_class = model_responce["tensor"]["values"][0]

            if not CLASS_ENCODING[breed] == model_predicted_class:
                if (
                    abs(CLASS_ENCODING[breed] - model_predicted_class) > 1e-10
                ):  # deviation
                    response.failure(
                        "Wrong model prediction, "
                        f"got {int(model_predicted_class)}, "
                        f"need {CLASS_ENCODING[breed]}!"
                    )
                    logging.warning(
                        f"Model predicted incorrect class for {target_image.name}: "
                        f"got {model_predicted_class} "
                        f"instead of {CLASS_ENCODING[breed]}."
                    )
