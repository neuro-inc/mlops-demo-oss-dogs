import argparse
import logging
import asyncio
import os

import requests
from pathlib import Path
from typing import List

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
        )
    )
    return return_code


async def _run_label_studio(
        cmd: List[str], project_root: Path
) -> None:
    logging.info('Starting Label Studio...')
    # use start_new_session=True not to send KeyboardInterrupt to subprocess
    ls_proc = await asyncio.create_subprocess_exec(*cmd, start_new_session=True)
    await asyncio.sleep(10)

    response = requests.get(url=f"{LS_API_URL}/storages/localfiles/1",
                            headers=AUTH)
    if response.status_code == 404:
        logging.info("Creating local storage via Label Studio API")
        # Create local storage if it doesn't exist
        requests.post(url=f"{LS_API_URL}/storages/localfiles",
                      json={
                          "project": 1,
                          "title": "Pachyderm",
                          "path": os.environ('DATA_PATH'),
                          "use_blob_urls": True
                      },
                      headers=AUTH)

    # Sync tasks from local storage
    requests.post(url=f"{LS_API_URL}/storages/localfiles/1/sync",
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
    # return False
    return num_tasks_with_annotations >= task_number


def _save_labeling_results(project_root: Path) -> None:
    response = requests.get(f"{LS_API_URL}/projects/1/export?exportType=JSON",
                            headers=AUTH)
    results_file = project_root / "data" / "result.json"
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

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main(get_args())
