import os
import json
import random
import pathlib

from locust import HttpUser, task

from config.model import FNAME_CLASS


IMGS_DIR = pathlib.Path(os.environ["IMGS_DIR"])
DOG_IDS = FNAME_CLASS.keys()
JPG_FILES = [
    x for x in IMGS_DIR.glob("**/*.jpg") if any(map(lambda id_: id_ in str(x), DOG_IDS))
]


class LoadGenerator(HttpUser):
    @task
    def prediction(self) -> None:
        target_image = random.choice(JPG_FILES)
        for file_name, sent_breed in FNAME_CLASS.items():
            if file_name in target_image.name:
                break

        payload = dict(binData=target_image.read_bytes())
        with self.client.post("", files=payload, catch_response=True) as response:
            predicted_breed = json.loads(response.text)["strData"]
            if sent_breed != predicted_breed:
                response.failure(
                    f"Incorrect prediction for {target_image.name} ({sent_breed}) got {predicted_breed}."
                )
