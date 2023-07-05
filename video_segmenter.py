#!/bin/python3

import subprocess
import sys
from pathlib import Path
from typing import Tuple

USAGE = (f"[?] Usage: python {sys.argv[0]} [file path] [max size in mb] "
         "[directory to save the segments]")

try:
    media = Path(sys.argv[1])
    max_size = int(sys.argv[2])
    save_dir = Path(sys.argv[3])
except IndexError:
    print(USAGE)
    sys.exit(1)


def get_video_duration_size(video_path: Path) -> Tuple[int, int]:
    """Returns the duration & size of a video in Minutes & Mb."""
    command = ['ffprobe', '-v', 'error', '-show_entries',
               'format=duration', '-of',
               'default=noprint_wrappers=1:nokey=1', video_path]
    result = subprocess.run(command, capture_output=True, text=True)
    duration = float(result.stdout)
    return (round(duration),
            round(video_path.stat().st_size / (1000 ** 2)))


def main():
    duration, size = get_video_duration_size(media)
    print(f"\n[+] File: {media.name}")
    print(f"[-] Duration: {duration} minutes")
    print(f"[-] Size: {size} Mb")
    segment_duration = round((duration / size) * max_size) - 30
    print(f"[-] Segment Duration: {round(segment_duration / 60)} minutes")
    command = ['ffmpeg', '-i', media, '-c', 'copy', '-map', '0',
               '-segment_time', str(segment_duration), '-f',
               'segment', '-reset_timestamps', '1',
               f'{save_dir}/{media.name.split(".")[-2]}%03d.mp4']
    subprocess.run(command, capture_output=True)


main()
