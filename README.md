# Bilibili Song Downloader

A Python script that automatically searches for songs on Bilibili, selects a video shorter than 10 minutes, and downloads its audio track as an MP3 file.

## Description

This tool reads a list of song names from a text file, use Bilibili's public search API to search for each song, filters results by duration (≤10 minutes), and downloads the audio from the first suitable video using `yt-dlp`. It solves common issues like missing cookies (avoiding 412 errors) and connection failures by retrying with different videos.

## Features

- Searches Bilibili for videos matching given song titles.
- Filters videos longer than 10 minutes.
- Extracts audio and saves it as MP3.
- Mimics a real browser with proper headers and cookies to bypass API restrictions.
- Automatically tries up to 3 different videos per song if downloads fail.
- Sanitizes filenames to remove invalid characters.

## Requirements

- **Python 3.6+** (with standard library modules: `os`, `re`, `json`, `subprocess`, `urllib.parse`)
- External Python packages:
  - `requests` – for Bilibili API calls
  - `yt-dlp` – for downloading and converting video to MP3

## Installation

### 1. Clone or download the script

Save the provided Python script (e.g., `music.py`) to your computer.

### 2. Install dependencies

It is strongly recommended to use a virtual environment to avoid conflicts with system packages:

```bash
python -m venv bilibili_env
source bilibili_env/bin/activate   # Linux/macOS
# or bilibili_env\Scripts\activate  # Windows
```

Then install the required packages:

```bash
pip install requests yt-dlp
```

If you prefer not to use a virtual environment, you can install them with:

```bash
pip install --user requests yt-dlp
```

> **Note on Arch Linux / externally-managed environments**:  
> If you get an "externally-managed-environment" error, create a virtual environment as shown above, or install system packages with:
> ```bash
> sudo pacman -S python-requests yt-dlp
> ```

## Usage

1. **Create a song list file**  
   Make a plain text file named `songs.txt` (or any name you prefer) with one song title per line(the song name can be not accurate, just ensure it can be searched), for example:
   ```
   溯
   phoenix (fall out boys)
   murder in my mind
   evening punk
   ```

2. **Run the script**  
   ```bash
   python music.py
   ```
   By default, the script expects `songs.txt` in the current directory. You can change the filename by editing the `main("songs.txt")` line at the bottom.

3. **Output**  
   For each successfully downloaded song, an MP3 file will be created in the same folder, named after the original song query (e.g., `溯.mp3`). If multiple songs have the same name, they will be overwritten.

## Notes

- The script uses Bilibili's public search API (`https://api.bilibili.com/x/web-interface/search/type`). If Bilibili changes this endpoint, the script may need updating.
- The script selects the first video from the search results that meets the duration criteria. You can modify `pick_best_video()` to implement different sorting (e.g., by view count, upload date).
- Downloaded filenames are based on the original song query, not the video title, to keep them consistent.