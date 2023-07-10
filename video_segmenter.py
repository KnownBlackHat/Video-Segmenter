#!/bin/python3

import subprocess
import sys
from pathlib import Path
from typing import Tuple


def get_video_duration_size(video_path: Path) -> Tuple[float, float]:
    """Returns the duration & size of a video in Minutes & Mb."""
    command = ['ffprobe', '-v', 'error', '-show_entries',
               'format=duration', '-of',
               'default=noprint_wrappers=1:nokey=1', video_path]
    result = subprocess.run(command, capture_output=True, text=True)
    duration = float(result.stdout)
    return (duration,
            video_path.stat().st_size / (1024 ** 2))


def recheck(dir: Path, max_size: int):
    files = [file for file in dir.iterdir() if file.is_file()]
    for file in files:
        file_size = file.stat().st_size / (1024 ** 2)
        segment_duration = media_stats(file, round(file_size/2)).segment_duration
        if (file_size >= max_size):
            trim(media=file,
                 segment_duration=segment_duration,
                 out_path=dir, file_name=f"{file.name}%02d.mp4")
            file.unlink()


def media_stats(media: Path, max_size: int):
    duration, size = get_video_duration_size(media)
    segment_duration = ((duration / size) * max_size)

    class Meta_data:
        def __init__(self):
            self.size = size
            self.duration = duration
            self.segment_duration = segment_duration
    return Meta_data()


def trim(media: Path,
         segment_duration: float,
         out_path: Path,
         file_name: str = "%03d.mp4"):
    command = ['ffmpeg', '-i', media, '-c', 'copy', '-map', '0',
               '-segment_time', str(segment_duration), '-f',
               'segment', '-reset_timestamps', '1',
               f'{out_path.absolute()}/{file_name}']
    subprocess.run(command, capture_output=True)


def main():
    USAGE = (f"[?] Usage: python {sys.argv[0]} [file path] [max size in mb] "
             "[directory to save the segments]")

    try:
        media = Path(sys.argv[1])
        max_size = int(sys.argv[2])
        save_dir = Path(sys.argv[3])
    except IndexError:
        print(USAGE)
        sys.exit(1)

    out_path = Path(f'{save_dir}/{media.name[:-len(media.suffix)]}')
    try:
        out_path.mkdir()
    except FileExistsError:
        ...
    stats = media_stats(media, max_size)
    if (stats.size <= max_size):
        raise ValueError(f"Video Size is Already less than {max_size} Mb")
    elif (stats.segment_duration <= 0):
        raise ValueError("Max Size Is Too Low")
    print(f"[+] Trimming {media.name}")
    print(f"[+] Max Size: {max_size} Mb")
    print(f"[+] Duration: {stats.duration} Minutes")
    print(f"[+] Size: {stats.size} Mb")
    print(f"[+] Segment Duration: {stats.segment_duration / 60} Minutes")
    print(f"[+] Saving To: {out_path.absolute()}")
    trim(media, stats.segment_duration, out_path)
    recheck(out_path, max_size)


main()
