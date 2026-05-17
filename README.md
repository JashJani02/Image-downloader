# Image-downloader
A simple image and post downloader built with Python, supporting Instagram and YouTube. Powered by Instaloader under the hood, and Streamlit as its interface, it automatically fetches available image resolutions (720p, 1080p, 4K where possible) and makes downloading quick and easy.

## Project Structure
```
Image-downloader
    |
    |----app.py
    |----requirements.txt
    |----README.md
```

## Python Libraries
1) requests
2) Beautiful Soup
3) Streamlit
4) Pillow
5) urllib
6) Instaloader

### Project-setup
1) Clone the project<br><pre><code>git clone https://github.com/JashJani02/Image-downloader.git</code></pre>
2) Change directory to Parent folder<br><pre><code>cd Image-downloader</code></pre>
3) Create Python Virtual Environment<br><pre><code>python -m venv </code></pre>
4) Activate venv <br><ol><li>Windows cmd <pre><code>.\\Scripts\Activate.ps1</code></pre></li><li>Bash/zsh <pre><code>source /bin/activate</code></pre></li></ol>

## Function Reference
| Function Name                        | Parameters                                    | Returns                  | Description                                                                                                                         |
| ------------------------------------ | --------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `get_image_resolution(img_bytes)`    | `img_bytes` → Raw image bytes                 | `(width, height, label)` | Detects image dimensions and categorizes quality labels like `4K`, `1080p`, `720p`, or custom resolution.                         |
| `extract_images(page_url)`           | `page_url` → Website URL                      | `list[str]`              | Extracts all valid image URLs from generic HTML pages using BeautifulSoup.                                                          |
| `extract_instagram_image(insta_url)` | `insta_url` → Instagram post/reel/profile URL | `list[str]`              | Fetches highest-quality Instagram images or profile pictures using Instaloader. Supports posts, reels, and profile DPs.           |
| `extract_youtube_thumbnail(yt_url)`  | `yt_url` → YouTube video URL                  | `list[str]`              | Generates multiple YouTube thumbnail URLs in different quality levels (`maxresdefault`, `hqdefault`, etc.).                       |
| `extract_reddit_images(reddit_url)`  | `reddit_url` → Reddit post URL                | `list[str]`              | Retrieves image URLs from Reddit JSON responses recursively.                                                                        |
| `extract_twitter_images(tweet_url)`  | `tweet_url` → Twitter/X post URL              | `list[str]`              | Extracts image URLs from Twitter/X posts using regex matching on HTML content.                                                      |
| `get_images(url)`                    | `url` → Any supported platform URL            | `list[str]`              | Dispatches the URL to the correct extractor based on domain detection (Instagram, Reddit, Twitter/X, YouTube, or generic websites). |
