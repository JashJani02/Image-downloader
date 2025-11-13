import streamlit as st
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import re
from urllib.parse import urlparse
import instaloader  # ✅ New for Instagram handling

st.set_page_config(page_title="Universal Image Downloader", page_icon="📸", layout="wide")

st.title("📸 Universal Image Downloader")
st.markdown("Download any **public image** (Instagram posts, DPs, YouTube thumbnails, Reddit, Twitter/X, wallpapers, etc.) in the highest available resolution.")


# ---------- Utility: Image resolution ----------
def get_image_resolution(img_bytes):
    try:
        img = Image.open(BytesIO(img_bytes))
        width, height = img.size
        longest = max(width, height)
        if longest >= 3840:
            label = "4K"
        elif longest >= 1920:
            label = "1080p"
        elif longest >= 1280:
            label = "720p"
        else:
            label = f"{width}×{height}"
        return width, height, label
    except Exception:
        return None, None, "Unknown"


# ---------- Generic HTML image extractor ----------
def extract_images(page_url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
    }
    try:
        res = requests.get(page_url, headers=headers, timeout=10)
        if res.status_code != 200:
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        image_tags = soup.find_all("img")

        image_urls = []
        for img in image_tags:
            src = img.get("src") or img.get("data-src")
            if src and src.startswith(("http://", "https://")):
                image_urls.append(src)

        seen = set()
        unique_urls = [x for x in image_urls if not (x in seen or seen.add(x))]
        return unique_urls
    except Exception:
        return []


# ---------- Instagram (via Instaloader) ----------
def extract_instagram_image(insta_url):
    """Detects whether the Instagram URL is a post or a profile and fetches highest quality images."""
    try:
        L = instaloader.Instaloader(download_comments=False, save_metadata=False)
        # Disable console output from Instaloader
        L.context.log = lambda *a, **kw: None

        parsed = urlparse(insta_url)
        parts = [p for p in parsed.path.split("/") if p]

        if not parts:
            return []

        # ✅ Case 1: Post or Reel
        if parts[0] in ["p", "reel"]:
            shortcode = parts[1]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            image_urls = []

            if post.typename == "GraphSidecar":
                image_urls = [n.display_url for n in post.get_sidecar_nodes()]
            else:
                image_urls = [post.url]

            return image_urls

        # ✅ Case 2: Profile (DP)
        elif len(parts) == 1:
            username = parts[0]
            profile = instaloader.Profile.from_username(L.context, username)
            return [profile.profile_pic_url]

        else:
            return []

    except Exception as e:
        print("Instagram error:", e)
        return []

# ---------- YouTube thumbnail extractor ----------
def extract_youtube_thumbnail(yt_url):
    video_id = None
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", yt_url)
    if match:
        video_id = match.group(1)
    if not video_id:
        return []

    qualities = ["maxresdefault", "sddefault", "hqdefault", "mqdefault", "default"]
    thumbs = [f"https://img.youtube.com/vi/{video_id}/{q}.jpg" for q in qualities]
    return thumbs


# ---------- Reddit ----------
def extract_reddit_images(reddit_url):
    try:
        if not reddit_url.endswith(".json"):
            reddit_url = reddit_url.rstrip("/") + "/.json"

        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(reddit_url, headers=headers, timeout=10)
        if res.status_code != 200:
            return []

        data = res.json()
        image_urls = []

        def traverse(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ("url_overridden_by_dest", "url") and isinstance(v, str) and v.endswith((".jpg", ".png", ".jpeg", ".webp")):
                        image_urls.append(v)
                    traverse(v)
            elif isinstance(obj, list):
                for i in obj:
                    traverse(i)

        traverse(data)
        return list(set(image_urls))
    except Exception:
        return []


# ---------- Twitter / X ----------
def extract_twitter_images(tweet_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(tweet_url, headers=headers, timeout=10)
        if res.status_code != 200:
            return []

        matches = re.findall(r"https://pbs\.twimg\.com/media/[A-Za-z0-9_-]+\.[a-zA-Z]+", res.text)
        return list(set(matches))
    except Exception:
        return []


# ---------- Dispatcher ----------
def get_images(url):
    if "instagram.com" in url:
        return extract_instagram_image(url)
    elif "reddit.com" in url:
        return extract_reddit_images(url)
    elif "x.com" in url or "twitter.com" in url:
        return extract_twitter_images(url)
    elif "youtube.com" in url or "youtu.be" in url:
        return extract_youtube_thumbnail(url)
    else:
        return extract_images(url)


# ---------- Main UI ----------
url = st.text_input("Enter Image / Post / Page URL:")

if url:
    with st.spinner("Fetching images..."):
        image_urls = get_images(url)

    if image_urls:
        st.success(f"✅ Found {len(image_urls)} image(s).")
        for img_url in image_urls:
            try:
                img_data = requests.get(img_url, timeout=10).content
                width, height, label = get_image_resolution(img_data)
                st.markdown(f"**Resolution:** {width}×{height} ({label})")
                st.image(img_data, width="content")
                file_name = img_url.split("/")[-1].split("?")[0] or f"image_{width}x{height}.jpg"
                st.download_button(
                    f"⬇️ Download ({label})",
                    data=img_data,
                    file_name=file_name,
                    mime="image/jpeg"
                )
                st.markdown("---")
            except Exception as e:
                st.warning(f"Could not load {img_url} — {e}")
    else:
        st.warning("No images found at this URL. Make sure the post or DP is public.")
else:
    st.info("Enter a public image or post URL to begin.")
