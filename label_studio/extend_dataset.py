import argparse
import shutil
from pathlib import Path

from config.model import FNAME_CLASS


def check_non_negative(value):
    int_value = int(value)
    if int_value < 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid non-negative int value")
    return int_value


def check_directory_exists(value):
    path_value = Path(value)
    if not path_value.exists() or not path_value.is_dir():
        raise argparse.ArgumentTypeError(f"{value} does not exist or not a directory")
    return path_value


def extend_dataset(args: argparse.Namespace) -> None:
    cur_data_root = Path(args.cur_dataset)
    full_data_root = Path(args.full_dataset)

    if not cur_data_root.exists():
        cur_data_root.mkdir(parents=True)

    # Images we already have
    cur_files = {x.name for x in cur_data_root.iterdir()}
    # Folders with breeds of interest
    breed_dirs = {breed_dir for breed_dir in full_data_root.iterdir() if breed_dir.name.split('-')[0] in FNAME_CLASS}

    # Images in these folders except the ones we already have
    available_breed_images = []
    for breed_dir in breed_dirs:
        available_breed_images.extend([x for x in breed_dir.iterdir() if x.name not in cur_files])

    # Select and copy new images
    new_breed_images = available_breed_images[:args.nmber_of_imgs]
    for image in new_breed_images:
        shutil.copy(image, cur_data_root / image.name)

    print(f"{len(new_breed_images)} images copied")


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--cur_dataset",
        required=True,
        type=check_directory_exists,
        help="Path to the folder, where image binaries are located",
    )
    parser.add_argument(
        "-f",
        "--full_dataset",
        required=True,
        type=check_directory_exists,
        help="Path to full dataset, from where new images will be taken",
    )
    parser.add_argument(
        "-n",
        "--nmber_of_imgs",
        default=1,
        type=check_non_negative,
        help="How many new images to add from dataset into current data",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    extend_dataset(get_args())
