import argparse
import shutil
from pathlib import Path


def extend_dataset(args: argparse.Namespace) -> None:
    cur_data_root = Path(args.cur_dataset)
    if cur_data_root.exists() and not cur_data_root.is_dir():
        raise ValueError(f"{str(cur_data_root)} exists, but is not a directory.")
    if not cur_data_root.exists():
        cur_data_root.mkdir(parents=True)
    cur_files = {x.name for x in cur_data_root.iterdir()}

    full_dataset_root = Path(args.full_dataset)
    breeds_dirs = ["n02085936-Maltese_dog", "n02088094-Afghan_hound"]
    dataset_files = set()
    for breed_dir in breeds_dirs:
        dataset_files.update({x for x in (full_dataset_root / breed_dir).iterdir()})

    i = args.nmber_of_imgs
    for x in dataset_files:
        if x.name not in cur_files:
            shutil.copy(x, cur_data_root / x.name)
            i -= 1
        if i == 0:
            break


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--cur_dataset",
        required=True,
        type=Path,
        help="Path to current data",
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

    args = parser.parse_args()
    if not args.full_dataset.exists() or not args.full_dataset.is_dir():
        raise ValueError(f"{args.full_dataset} does not exist, or not a directory!")
    if args.nmber_of_imgs < 0:
        raise ValueError(
            "-n/--nmber_of_imgs parameter should be greater than 0, "
            f"given {args.nmber_of_imgs}"
        )
    return args


if __name__ == "__main__":
    extend_dataset(get_args())
