import argparse
import logging
import asyncio
import os

import requests
from pathlib import Path
from typing import List, Optional

logging.basicConfig(level=logging.INFO)

AUTH = {"Authorization": f"Token {os.environ.get('LS_TOKEN')}"}
LS_API_URL = f"http://localhost:{os.environ.get('LS_PORT')}/api"


def main(args: argparse.Namespace) -> None:
    cmd = ["label-studio"] + args.label_studio_args
    cmd_str = ' '.join(cmd)
    logging.info(f"Launching label studio with cmd: '{cmd_str}' ")
    return_code = asyncio.run(
        _run_label_studio(
            cmd,
            project_root=args.project_root,
            bucket_name=args.bucket,
            region_name=args.region_name,
            endpoint_url=args.s3_endpoint,
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
        )
    )
    return return_code


async def _run_label_studio(
        cmd: List[str], project_root: Path,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
) -> None:
    use_s3 = all(
        {i is not None for i in (bucket_name, region_name, endpoint_url, aws_access_key_id, aws_secret_access_key)})
    use_local = all(
        {i is None for i in (bucket_name, region_name, endpoint_url, aws_access_key_id, aws_secret_access_key)})
    if not use_local and not use_s3:
        raise ValueError("Invalid combination of S3 arguments passed")
    storage_type = "s3" if use_s3 else "localfiles"

    logging.info('Starting Label Studio...')
    # use start_new_session=True not to send KeyboardInterrupt to subprocess
    ls_proc = await asyncio.create_subprocess_exec(*cmd, start_new_session=True)
    await asyncio.sleep(10)

    response = requests.get(url=f"{LS_API_URL}/storages/{storage_type}/1",
                            headers=AUTH)
    if response.status_code == 404:
        logging.info(f"Creating {storage_type} storage via Label Studio API")
        # Create local storage if it doesn't exist
        data = {
            "project": 1,
            "title": storage_type,
            "use_blob_urls": True,
        }
        if use_s3:
            data.update({
                "bucket": bucket_name,
                "prefix": "images/",
                "region_name": region_name,
                "s3_endpoint": endpoint_url,
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
                "presign_ttl": 60,
                "recursive_scan": False,
            })
        else:
            data.update({
                "path": os.environ.get('DATA_PATH'),
            })
        requests.post(url=f"{LS_API_URL}/storages/{storage_type}",
                      json=data,
                      headers=AUTH)

    # Sync tasks from local storage
    logging.info("Syncing tasks")
    requests.post(url=f"{LS_API_URL}/storages/{storage_type}/1/sync",
                  json={"project": 1},
                  headers=AUTH)

    is_last_iteration = False
    while True:
        try:
            if _all_tasks_finished() or is_last_iteration:
                logging.warning(
                    "All tasks are finished! Uploading labels and terminating Label-studio."
                )
                _save_labeling_results(project_root)
                if ls_proc.returncode is None:
                    ls_proc.terminate()
                await ls_proc.wait()
                is_last_iteration = True
            else:
                await asyncio.sleep(3)
            if is_last_iteration:
                break
        except KeyboardInterrupt:
            logging.info("Interrupted")
            is_last_iteration = True


def _all_tasks_finished() -> bool:
    response = requests.get(url=f"{LS_API_URL}/projects/1/",
                            json={
                                "project": 1,
                            },
                            headers=AUTH).json()
    num_tasks_with_annotations = response['num_tasks_with_annotations']
    task_number = response['task_number']
    return num_tasks_with_annotations >= task_number


def _save_labeling_results(project_root: Path) -> None:
    response = requests.get(f"{LS_API_URL}/projects/1/export?exportType=JSON",
                            headers=AUTH)
    results_file = project_root / "data" / "result.json"
    results_folder = results_file.parent
    results_folder.mkdir(parents=True, exist_ok=True)
    logging.info(f"Saving results to {results_file}")
    with results_file.open("wb") as fd:
        fd.write(response.content)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "label_studio_args",
        nargs="*",
        help="Args passed to launch label-studio",
    )
    parser.add_argument(
        "-r",
        "--project_root",
        type=Path,
        help="Project root path",
    )
    parser.add_argument(
        "--bucket",
        type=str,
        help="AWS S3 bucket name",
    )
    parser.add_argument(
        "--region_name",
        type=str,
        help="AWS S3 region name",
    )
    parser.add_argument(
        "--s3_endpoint",
        type=str,
        help="AWS S3 endpoint url",
    )
    parser.add_argument(
        "--aws_access_key_id",
        type=str,
        help="AWS S3 access key ID",
    )
    parser.add_argument(
        "--aws_secret_access_key",
        type=str,
        help="AWS S3 secret access key",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main(get_args())
