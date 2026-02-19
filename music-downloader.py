import os
import re
import json
import subprocess
import requests
from urllib.parse import quote

# ------------------------------
# Configuration
# ------------------------------
SEARCH_API = "https://api.bilibili.com/x/web-interface/search/type"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Origin": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Connection": "keep-alive",
}
MAX_DURATION = 600  # seconds (10 minutes)
MAX_DOWNLOAD_ATTEMPTS = 3  # try up to 3 videos per song

# ------------------------------
# Helper functions
# ------------------------------
def get_session_with_cookies():
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get("https://www.bilibili.com", timeout=10)
    except Exception as e:
        print(f"Warning: Could not fetch homepage cookies: {e}")
    return session

def parse_duration(duration_str):
    parts = list(map(int, duration_str.split(':')))
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    else:
        return 0

def search_bilibili(session, keyword, page=1, page_size=20):
    params = {
        "search_type": "video",
        "keyword": keyword,
        "page": page,
        "page_size": page_size
    }
    try:
        resp = session.get(SEARCH_API, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data["code"] != 0:
            print(f"API error: {data.get('message', 'Unknown error')}")
            return []

        videos = []
        for item in data["data"]["result"]:
            video_url = item.get("arcurl")
            if not video_url:
                continue
            duration_str = item.get("duration", "0:00")
            duration_sec = parse_duration(duration_str)
            videos.append({
                "title": item.get("title", ""),
                "url": video_url,
                "duration": duration_sec
            })
        return videos
    except Exception as e:
        print(f"Search failed for '{keyword}': {e}")
        return []

def filter_videos(videos, max_seconds):
    return [v for v in videos if v["duration"] <= max_seconds]

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def download_audio(video_url, output_path, attempt=1):
    """
    Use yt-dlp with extra headers and options to mimic a browser.
    Returns True if successful, False otherwise.
    """
    # Add extra yt-dlp options to improve compatibility
    cmd = [
        "yt-dlp",
        "-x",                          # extract audio
        "--audio-format", "mp3",       # convert to mp3
        "--user-agent", HEADERS["User-Agent"],
        "--referer", "https://www.bilibili.com",
        "--add-header", f"Origin:{HEADERS['Origin']}",
        "--add-header", f"Accept:{HEADERS['Accept']}",
        "--add-header", f"Accept-Language:{HEADERS['Accept-Language']}",
        "--no-check-certificate",      # sometimes needed for CDNs with weird certs
        "--retries", "5",
        "--fragment-retries", "5",
        "-o", output_path,
        video_url
    ]
    try:
        print(f"Download attempt {attempt} for {video_url}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Downloaded: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"yt-dlp error (attempt {attempt}): {e.stderr}")
        return False

# ------------------------------
# Main routine
# ------------------------------
def main(song_list_file):
    if not os.path.isfile(song_list_file):
        print(f"File not found: {song_list_file}")
        return

    session = get_session_with_cookies()

    with open(song_list_file, 'r', encoding='utf-8') as f:
        songs = [line.strip() for line in f if line.strip()]

    for song in songs:
        print(f"\nProcessing: {song}")
        videos = search_bilibili(session, song)
        if not videos:
            print(f"No search results for '{song}'")
            continue

        short_videos = filter_videos(videos, MAX_DURATION)
        if not short_videos:
            print(f"No video under {MAX_DURATION//60} minutes found for '{song}'")
            continue

        # Try up to MAX_DOWNLOAD_ATTEMPTS videos
        downloaded = False
        for idx, video in enumerate(short_videos[:MAX_DOWNLOAD_ATTEMPTS]):
            print(f"Trying video {idx+1}: {video['title']} ({video['duration']//60}:{video['duration']%60:02d})")
            safe_title = sanitize_filename(song)
            output_template = f"{safe_title}.%(ext)s"
            success = download_audio(video['url'], output_template, attempt=idx+1)
            if success:
                downloaded = True
                break
            else:
                print("Download failed, trying next video...")

        if not downloaded:
            print(f"Could not download any video for '{song}' after {MAX_DOWNLOAD_ATTEMPTS} attempts.")

if __name__ == "__main__":
    main("songs.txt")
