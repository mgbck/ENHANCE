import sys
import os
import urllib.request
import urllib.error

from pathlib import Path

URL = "https://isic-challenge-data.s3.amazonaws.com/2017/ISIC-2017_Training_Data.zip"


def human_readable_size(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"


def download(url: str, dest_path: Path):
    with urllib.request.urlopen(url) as response:
        total_size = int(response.getheader("Content-Length", "0"))
        print(f"Downloading: {url}")
        if total_size:
            print(f"File size: {human_readable_size(total_size)}")
        else:
            print("File size: unknown")

        temp_path = dest_path.with_suffix(".tmp")
        with open(temp_path, "wb") as out_file:
            downloaded = 0
            block_size = 8192

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded += len(buffer)

                if total_size:
                    percent = downloaded / total_size * 100
                    progress = f"{human_readable_size(downloaded)} /{human_readable_size(total_size)} ({percent:5.1f}%)"
                else:
                    progress = f"{human_readable_size(downloaded)}downloaded"

                print(f"\r{progress}", end="", flush=True)

        print("\nDownload finished.")
        temp_path.rename(dest_path)


def main(target_dir: Path):
    dest = os.path.join(target_dir, os.path.basename(URL))

    if os.path.exists(dest_file):
        resp = (
            input(f"The file '{dest_file}' already exists. Overwrite?[y/N] ")
            .strip()
            .lower()
        )
        if resp != "y":
            print("Aborting – existing file kept.")
            return

    try:
        download(URL, dest)
    except urllib.error.URLError as e:
        print(f"\nError while downloading: {e.reason}")
        sys.exit(1)

    print(f"\nFile saved to: {dest_file}")


if __name__ == "__main__":
    target_directory = Path(os.path.join(os.getcwd(), "external/")).resolve()
    main("external/")
