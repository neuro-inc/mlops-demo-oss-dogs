import argparse
import time
import logging
import json
import shutil
import asyncio
import zipfile
import requests
import io
from urllib.parse import urlparse, quote
from pathlib import Path
from typing import Optional, List

logging.basicConfig(level=logging.INFO)


def main(args: argparse.Namespace) -> None:
    cmd = ["label-studio"] + args.label_studio_args
    logging.info(f"Launching label studio with cmd: '{' '.join(cmd)}' ")
    loop = asyncio.get_event_loop()
    return_code = loop.run_until_complete(
        _run_label_studio(
            cmd,
            ls_project_root=args.ls_project_root,
            project_root=args.project_root,
        )
    )
    return return_code


async def _run_label_studio(
        cmd: List[str], ls_project_root: Path, project_root: Path
) -> None:
    # use start_new_session=True not to send KeyboardInterrupt to subprocess
    print('starting ls...')
    ls_proc = await asyncio.create_subprocess_exec(*cmd, start_new_session=True)
    # let label studio start
    print('started ls, waiting 10 seconds')
    await asyncio.sleep(10)
    print('wait completed')
    requests.post(url=f"http://localhost:443/api/storages/localfiles",
                  json={
                      "project": 1,
                      "title": "Pachyderm",
                      "path": "/usr/project/data/Images/",
                      "use_blob_urls": True
                  },
                  headers={
                      "Authorization": "Token token12356"
                  })
    requests.post(url=f"http://localhost:443/api/storages/localfiles/1/sync",
                  json={
                      "project": 1,
                  },
                  headers={
                      "Authorization": "Token token12356"
                  })
    is_last_iteration = False
    while True:
        try:
            if _all_tasks_finished(ls_project_root, project_root) or is_last_iteration:
                logging.warning(
                    "All tasks are finished! Uploading labels and terminating Label-studio."
                )
                _save_labeling_results(project_root, _find_ls_port(ls_project_root, cmd))
                if ls_proc.returncode is None:
                    ls_proc.terminate()
                await ls_proc.wait()
                _migrate_uploaded_completions(ls_project_root, project_root)
                is_last_iteration = True
            else:
                await asyncio.sleep(1)
            if is_last_iteration:
                break
        except KeyboardInterrupt:
            logging.info("Interrupted")
            is_last_iteration = True


async def _read_stream(stream: Optional[asyncio.StreamReader], level: int) -> None:
    if not stream:
        logging.log(msg="Stream is not available!", level=level)
    else:
        while not stream.at_eof():
            line = await stream.readline()
            logging.log(msg=line.decode(), level=level)


def _all_tasks_finished(ls_project_root: Path, project_root: Path) -> bool:
    completions_dir = ls_project_root / "completions"
    imgs_dir = project_root / "data" / "Images"
    uploaded_imgs_dir = ls_project_root / "upload"
    completions = 0  # finished labels
    imgs = 0  # images in dataset
    uploaded_imgs = 0  # uploaded images into label studio
    if completions_dir.exists() and completions_dir.is_dir():
        completions = len(list(completions_dir.glob("*.json")))
    if imgs_dir.exists() and imgs_dir.is_dir():
        imgs = len(list(imgs_dir.iterdir()))
    if uploaded_imgs_dir.exists() and uploaded_imgs_dir.is_dir():
        uploaded_imgs = len(list(uploaded_imgs_dir.iterdir()))
    if completions >= imgs + uploaded_imgs:
        return True  # all tasks, including the uploaded ones are annotated, terminating
    else:
        return False


def _save_labeling_results(project_root: Path, label_studio_port: str) -> None:
    for retry in range(5, 0, -1):
        try:
            addr = f"http://localhost:{label_studio_port}/api/project/export?format=JSON_MIN"
            response = requests.get(addr)
            break
        except requests.RequestException as e:
            logging.warning(f"Retry {retry}: cannot retrieve results from {addr}: {e}")
            time.sleep(2)
    results_archive = zipfile.ZipFile(io.BytesIO(response.content))
    results = results_archive.read("result.json").decode("UTF-8")
    results_file = project_root / "data" / "result.json"
    logging.info(f"Saving results to {results_file}")
    with results_file.open("w") as fd:
        fd.write(results)


def _find_ls_port(ls_project_root: Path, launch_cmd: List[str]) -> str:
    if "--port" in launch_cmd:
        port = launch_cmd[launch_cmd.index("--port") + 1]
    else:
        ls_config = json.loads((ls_project_root / "config.json").read_text())
        port = ls_config.get("port")
        if not port:
            # Default for Label-studio, if nothing else is provided.
            port = 8080  # type: ignore
    return str(port)


def _migrate_uploaded_completions(ls_project_root: Path, project_root: Path) -> None:
    "migrate completions for uploaded tasks via web GUI"
    upload_dir = ls_project_root / "upload"
    if not upload_dir.exists() or not upload_dir.is_dir():
        logging.info(f"Upload dir was not found under {str(upload_dir.resolve())}.")
        return
    complitions_dir = ls_project_root / "completions"
    for completion_p in complitions_dir.iterdir():
        completion = json.loads(completion_p.read_text())
        if "task_path" in completion.keys():
            # it is not an uploaded task
            continue
        task_url = urlparse(completion["data"]["image"])
        f_name = Path(task_url.path).name
        data_root_abs = (project_root / "data" / "Images").resolve()

        completion["task_path"] = str(data_root_abs / f_name)
        img_url = f"/data/{f_name}?d={quote(str(data_root_abs), safe='')}"
        completion["data"]["image"] = img_url
        shutil.move(upload_dir / f_name, data_root_abs / f_name)  # type: ignore

        with open(completion_p, "w") as completion_fd:
            json.dump(completion, completion_fd, indent=2)
        logging.info(f"Migrated uploaded completion {str(completion_p),}")


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
        help="Project root path (loaded from GH)",
    )
    parser.add_argument(
        "-l",
        "--ls_project_root",
        type=Path,
        help="Label studio project root path",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main(get_args())
