import os
import shutil
import argparse
import logging
import time
from datetime import datetime
from typing import List

# Define the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sync.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()


def get_args() -> argparse.Namespace:
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Path to source directory")
    parser.add_argument("destination", help="Path to destination directory")
    parser.add_argument("-l", "--loop_time", type=int, default=1,
                        help="Time in minutes between syncs (default: 1)")
    return parser.parse_args()


def copy_files(source_folder: str, destination_folder: str, files: List[str]) -> None:
    # Copy changed files from source to destination folder.
    for file_name in files:
        source_path = os.path.join(source_folder, file_name)
        destination_path = os.path.join(destination_folder, file_name)

        if os.path.isfile(source_path):
            if os.path.exists(destination_path) and os.stat(source_path).st_mtime <= os.stat(destination_path).st_mtime:
                # file has not been modified, no need to copy
                continue
            shutil.copy2(source_path, destination_path)
            logging.info(f"Copied file {file_name} from {source_folder} to {destination_folder}")
        elif os.path.isdir(source_path):
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)
            copy_files(source_path, destination_path, os.listdir(source_path))


def sync_folders(source_folder: str, destination_folder: str) -> None:
    # Synchronize two folders by copying changed files from source to destination.
    for root, _, files in os.walk(source_folder):
        copy_files(root, destination_folder, files)


def main() -> None:
    # Main function.
    args = get_args()
    loop_time = args.loop_time * 60
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logging.info(f"Sync started at {now} with loop time {args.loop_time} minutes")

    while True:
        sync_folders(args.source, args.destination)
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        logging.info(f"Synced folders at {now}")
        time_to_sleep = loop_time - time.time() % loop_time
        logging.info(f"Sleeping for {time_to_sleep} seconds")
        # Sleep until next sync time
        time.sleep(time_to_sleep)


if __name__ == "__main__":
    main()
