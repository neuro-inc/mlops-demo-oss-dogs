import os
import pathlib
import requests

IMGS_DIR = pathlib.Path(os.environ.get("IMGS_DIR") or "./data/Images/")


def try_inference_sample(endpoint_uri: str, image_name: str) -> str:
    img_path = IMGS_DIR / image_name

    request = requests.post(
        endpoint_uri,
        files=dict(binData=img_path.read_bytes()),
    )

    resp = request.text
    assert request.status_code == 200, request.text
    return resp


if __name__ == "__main__":
    responce = try_inference_sample(
        "https://seldon.onprem-poc.org.neu.ro"
        "/seldon/seldon/neuro-model/api/v1.0/predictions",
        "n02088094_1003.jpg",
    )
    print(responce)
