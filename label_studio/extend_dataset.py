import argparse
import shutil
import json
from pathlib import Path

from config.model import FNAME_CLASS


# Beware: the suffix depends on the Label Studio config
IMG_RECORD_SUFFIX = "?d=%2Flabel-studio%2Fproject%2Fdata%2FImages"
IMG_RECORD_PREFFIX = "/data/"


def extend_dataset(args: argparse.Namespace) -> None:
    cur_data_root = Path(args.cur_dataset)
    cur_dataset_descr = Path(args.cur_dataset_descr)

    if not cur_data_root.exists():
        cur_data_root.mkdir(parents=True)
    if not cur_dataset_descr.exists():
        start_id = 1
        cur_dataset_descr_d = []
    else:
        with cur_dataset_descr.open() as fd:
            try:
                cur_dataset_descr_d = json.load(fd)
                assert (
                    type(cur_dataset_descr_d) == list
                ), "Dataset description should be a JSON list of dicts"
                start_id = max([x["id"] for x in cur_dataset_descr_d]) + 1
            except json.decoder.JSONDecodeError:
                cur_dataset_descr_d = []
                start_id = 1

    cur_files = {x.name for x in cur_data_root.iterdir()}

    is_dir_needed = lambda x: x.name.split("-")[0] in FNAME_CLASS
    breeds_dirs = filter(is_dir_needed, args.full_dataset.iterdir())
    dataset_files = set()
    for breed_dir in breeds_dirs:
        dataset_files.update({x for x in breed_dir.iterdir()})

    i = 0
    for x in dataset_files:
        if i >= args.nmber_of_imgs:
            break
        if x.name not in cur_files:
            breed = [breed for id_, breed in FNAME_CLASS.items() if id_ in x.name][0]
            shutil.copy(x, cur_data_root / x.name)
            cur_dataset_descr_d.append(
                {
                    "image": f"{IMG_RECORD_PREFFIX}{x.name}{IMG_RECORD_SUFFIX}",
                    "id": start_id + i,
                    "choice": breed,
                }
            )
            i += 1
    if not args.skip_annotation_update:
        with cur_dataset_descr.open("w") as fd:
            json.dump(cur_dataset_descr_d, fd, indent=2, sort_keys=True)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--cur_dataset",
        required=True,
        type=Path,
        help="Path to the folder, where image binaries are located",
    )
    parser.add_argument(
        "-i",
        "--cur_dataset_descr",
        required=True,
        type=Path,
        help="Path to the JSON dataset description (info) file",
    )
    parser.add_argument(
        "-f",
        "--full_dataset",
        required=True,
        type=Path,
        help="Path to full dataset, from where new images will be taken",
    )
    parser.add_argument(
        "-n",
        "--nmber_of_imgs",
        default=1,
        type=int,
        help="How many new images to add from dataset into current data",
    )
    parser.add_argument(
        "--skip_annotation_update",
        default=False,
        action="store_true",
    )

    args = parser.parse_args()
    if not args.full_dataset.exists() or not args.full_dataset.is_dir():
        raise ValueError(f"{args.full_dataset} does not exist, or not a directory!")
    if args.nmber_of_imgs < 0:
        raise ValueError(
            "-n/--nmber_of_imgs parameter should be greater than 0, "
            f"given {args.nmber_of_imgs}"
        )

    if args.cur_dataset.exists() and not args.cur_dataset.is_dir():
        raise ValueError(f"{str(args.cur_dataset)} exists, but is not a directory.")
    if (
        not args.skip_annotation_update
        and args.cur_dataset_descr.exists()
        and not args.cur_dataset_descr.is_file()
    ):
        raise ValueError(f"{str(args.cur_dataset_descr)} exists, but is not a file.")

    return args


if __name__ == "__main__":
    extend_dataset(get_args())
