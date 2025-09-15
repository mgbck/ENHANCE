import sys
import os
import urllib.request
import zipfile
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


def unzip(zip_path: Path, extract_to: Path) -> None:
    if not zip_path.is_file():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    extract_to.mkdir(parents=True, exist_ok=True)
    print(f"Extracting {zip_path.name} → {extract_to}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        members = zf.infolist()
        total_members = len(members)

        for i, member in enumerate(members, start=1):
            if member.is_dir():
                continue

            data = zf.read(member)
            dest_path = extract_to / Path(member.filename).name

            with open(dest_path, "wb") as out_fp:
                out_fp.write(data)

            print(
                f"\r  [{i:3}/{total_members}] " f"{member.filename[:60]:60}",
                end="",
                flush=True,
            )

    print("\nExtraction finished.")


def main(target_dir: Path):
    dest = target_dir / os.path.basename(URL)

    if dest.exists():
        resp = (
            input(f"The file '{dest}' already exists. Overwrite?[y/N] ").strip().lower()
        )
        if resp != "y":
            print("Aborting – existing file kept.")
            try:
                unzip(dest, target_dir)
            except Exception as exc:
                print(f"\nError while extracting: {exc}")
                sys.exit(1)

            return
        else:
            dest.unlink()

    try:
        download(URL, dest)
    except urllib.error.URLError as e:
        print(f"\nError while downloading: {e.reason}")
        sys.exit(1)

    try:
        unzip(dest, target_dir)
    except Exception as exc:
        print(f"\nError while extracting: {exc}")
        sys.exit(1)

    print(f"\nFile saved to: {dest}")


if __name__ == "__main__":
    target_directory = Path(os.path.join(os.getcwd(), "external/")).resolve()
    main(target_directory)
