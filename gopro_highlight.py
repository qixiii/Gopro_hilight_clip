#!/usr/bin/env python3
"""Extract GoPro 'highlight' clips from MP4 chapters.

Usage:
    python gopro_highlight.py /path/to/file.mp4 --pre 1.0 --post 1.0

This script uses ffprobe to read chapters and ffmpeg to trim clips.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from typing import List


def run_cmd(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8')


def probe_mp4(path: str) -> dict:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_chapters", "-show_format", path]
    out = run_cmd(cmd)
    return json.loads(out)


def ensure_ffmpeg_available():
    """Ensure ffmpeg and ffprobe are available.

    This function checks PATH first, then looks for bundled binaries when
    running as a bundled executable (PyInstaller) or when ffmpeg/ffprobe are
    placed next to the script or interpreter on Windows.
    If found, the directory is prepended to PATH so subprocess calls can find
    the binaries.
    """
    ffmpeg = shutil.which('ffmpeg')
    ffprobe = shutil.which('ffprobe')

    # Search common locations for bundled binaries (PyInstaller _MEIPASS, script dir,
    # and interpreter dir). On Windows the binaries are named ffmpeg.exe/ffprobe.exe.
    possible_dirs = []
    if hasattr(sys, '_MEIPASS'):
        possible_dirs.append(sys._MEIPASS)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_dirs.append(script_dir)
    possible_dirs.append(os.path.dirname(sys.executable))

    for d in possible_dirs:
        if not d:
            continue
        ffmpeg_name = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
        ffprobe_name = 'ffprobe.exe' if os.name == 'nt' else 'ffprobe'
        ffmpeg_path = os.path.join(d, ffmpeg_name)
        ffprobe_path = os.path.join(d, ffprobe_name)
        if not ffmpeg and os.path.isfile(ffmpeg_path):
            os.environ['PATH'] = d + os.pathsep + os.environ.get('PATH', '')
            ffmpeg = shutil.which('ffmpeg')
        if not ffprobe and os.path.isfile(ffprobe_path):
            os.environ['PATH'] = d + os.pathsep + os.environ.get('PATH', '')
            ffprobe = shutil.which('ffprobe')
        if ffmpeg and ffprobe:
            break

    if not ffmpeg or not ffprobe:
        print('ffmpeg and ffprobe are required. Install them (e.g. sudo apt install ffmpeg) or place ffmpeg/ffprobe next to the executable.')
        sys.exit(1)


def mkdir_p(path: str):
    os.makedirs(path, exist_ok=True)


def secs_to_ts(s: float) -> str:
    """Format seconds to HH-MM-SS.mmm for filenames."""
    total_ms = int(round(s * 1000))
    ms = total_ms % 1000
    sec = (total_ms // 1000) % 60
    minute = (total_ms // 1000) // 60 % 60
    hour = (total_ms // 1000) // 3600
    return f"{hour:02d}-{minute:02d}-{sec:02d}.{ms:03d}"


def extract_clips(path: str, pre: float, post: float, outdir: str, reencode: bool = False, mode: str = 'chapter', name_with_ts: bool = False):
    data = probe_mp4(path)
    chapters = data.get('chapters', [])
    if not chapters:
        print('No chapters found in file; cannot detect highlights.')
        return []

    fmt = data.get('format', {})
    duration = None
    if 'duration' in fmt:
        try:
            duration = float(fmt['duration'])
        except Exception:
            duration = None

    # If duration missing, approximate from max chapter end_time
    if duration is None:
        max_end = 0.0
        for ch in chapters:
            end_time = float(ch.get('end_time', ch.get('end', 0)))
            max_end = max(max_end, end_time)
        duration = max_end

    print(f'Found {len(chapters)} chapter(s); file duration ~ {duration:.3f}s')

    mkdir_p(outdir)
    base = os.path.splitext(os.path.basename(path))[0]
    outputs = []

    for idx, ch in enumerate(chapters, start=1):
        start = float(ch.get('start_time', ch.get('start', 0)))
        end = float(ch.get('end_time', ch.get('end', start)))

        if mode == 'anchor':
            # fixed-length clip around the chapter START: [start - pre, start + post]
            out_start = max(0.0, start - pre)
            clip_duration = max(0.01, min(duration - out_start, pre + post))
            out_end = out_start + clip_duration
        else:
            # default: use chapter range extended with pre/post
            out_start = max(0.0, start - pre)
            out_end = min(duration, end + post)
            clip_duration = max(0.01, out_end - out_start)

        if name_with_ts and mode == 'anchor':
            ts = secs_to_ts(start)
            out_file = os.path.join(outdir, f"{base}_highlight_{ts}.mp4")
        else:
            out_file = os.path.join(outdir, f"{base}_highlight_{idx:02d}_{out_start:.3f}-{out_end:.3f}.mp4")

        if reencode:
            cmd = [
                'ffmpeg', '-y', '-ss', f'{out_start}', '-i', path, '-t', f'{clip_duration}',
                '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '128k', out_file
            ]
        else:
            # fast copy; seeks to nearest keyframe
            cmd = ['ffmpeg', '-y', '-ss', f'{out_start}', '-i', path, '-t', f'{clip_duration}', '-c', 'copy', out_file]

        print('Running:', ' '.join(cmd))
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print('Created', out_file)
            outputs.append(out_file)
        except subprocess.CalledProcessError as e:
            print('ffmpeg failed for chapter', idx, '(', e, ')')

    return outputs


def main():
    parser = argparse.ArgumentParser(description='Extract highlight clips from GoPro MP4 (chapters-based)')
    parser.add_argument('file', help='Path to MP4 file')
    parser.add_argument('--pre', type=float, default=1.0, help='Seconds before chapter start to include')
    parser.add_argument('--post', type=float, default=1.0, help='Seconds after chapter end to include')
    parser.add_argument('--outdir', default='highlights', help='Directory to write clips')
    parser.add_argument('--reencode', action='store_true', help='Re-encode clips for frame-accurate trim')
    parser.add_argument('--mode', choices=['chapter', 'anchor'], default='anchor', help='"chapter" uses full chapter range; "anchor" creates fixed-length clip around chapter start (pre+post length)')
    parser.add_argument('--recursive', action='store_true', help='Recurse into directories when input is a directory')
    parser.add_argument('--name-with-ts', action='store_true', help='Name output clips using highlight timestamp (HH-MM-SS.mmm)')
    parser.add_argument('--csv', default=None, help='Optional path to write a CSV summary of created clips')
    args = parser.parse_args()

    ensure_ffmpeg_available()

    # allow directory input
    if os.path.isdir(args.file):
        all_outputs = process_directory(args.file, args.outdir, args.pre, args.post, args.mode, args.recursive, args.name_with_ts, args.reencode, args.csv, None)
        if not all_outputs:
            print('No clips created from directory.')
        else:
            print('\nCreated clips:')
            for o in all_outputs:
                print(' -', o)
            if args.csv and os.path.isfile(args.csv):
                print('CSV summary written to', args.csv)
    else:
        if not os.path.isfile(args.file):
            print('File not found:', args.file)
            sys.exit(2)
        outputs = extract_clips(args.file, args.pre, args.post, args.outdir, args.reencode, args.mode, args.name_with_ts)
        if not outputs:
            print('No clips created.')
        else:
            print('\nCreated clips:')
            for o in outputs:
                print(' -', o)
            if args.csv:
                import csv
                with open(args.csv, 'w', newline='') as cf:
                    writer = csv.writer(cf)
                    writer.writerow(['clip','source'])
                    for o in outputs:
                        writer.writerow([o, os.path.abspath(args.file)])
                print('CSV summary written to', args.csv)

def process_directory(input_dir: str, outdir: str, pre: float, post: float, mode: str = 'anchor', recursive: bool = False, name_with_ts: bool = False, reencode: bool = False, csv_path: str = None, progress_callback=None):
    """Process all video files in a directory and return list of created clips.

    progress_callback can be either:
      - callback(message: str)
      - or callback(message: str, percent: int)

    The second form allows updating a progress bar in a UI.
    """
    files = []
    if recursive:
        for root, dirs, files_in in os.walk(input_dir):
            for f in files_in:
                if f.lower().endswith(('.mp4', '.mov')):
                    files.append(os.path.join(root, f))
    else:
        for f in os.listdir(input_dir):
            if f.lower().endswith(('.mp4', '.mov')):
                files.append(os.path.join(input_dir, f))

    def _cb(msg: str, percent: int = None):
        if progress_callback:
            try:
                # try calling with (msg, percent)
                progress_callback(msg, percent)
            except TypeError:
                # fallback to single-arg
                progress_callback(msg)
        else:
            print(msg)

    _cb(f'Found {len(files)} video file(s) in directory {input_dir}', 0)

    all_outputs = []
    total = len(files) if files else 1
    for i, f in enumerate(files, start=1):
        _cb(f'Processing {f}...', int((i-1)/total*100))
        try:
            outs = extract_clips(f, pre, post, outdir, reencode, mode, name_with_ts)
            if outs:
                all_outputs.extend(outs)
                for o in outs:
                    _cb(f'Created {o}', int(i/total*100))
            else:
                _cb(f'No highlights in {f}', int(i/total*100))
        except Exception as e:
            _cb(f'Error processing {f}: {e}', int(i/total*100))

    if csv_path:
        import csv
        with open(csv_path, 'w', newline='') as cf:
            writer = csv.writer(cf)
            writer.writerow(['clip', 'source'])
            for o in all_outputs:
                writer.writerow([o, os.path.abspath(input_dir)])
        _cb(f'CSV summary written to {csv_path}', 100)

    _cb('Processing complete', 100)
    return all_outputs




if __name__ == '__main__':
    main()
