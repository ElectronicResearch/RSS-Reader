# -*- coding: utf-8 -*-

import feedparser
from flask import Flask, render_template_string, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>RSS Reader & Zusammenfasser</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .container { max-width: 800px; margin-top: 40px; }
        .feed-item { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 1.5rem; margin-bottom: 1.5rem; display: flex; gap: 1.5rem; }
        .feed-item-img { max-width: 180px; max-height: 120px; object-fit: cover; border-radius: 6px; }
        .feed-item-content { flex: 1; }
        .feed-item h3 { margin-top: 0; }
        .summary { color: #444; }
        .feed-title { margin-top: 2rem; margin-bottom: 2rem; }
        .footer { text-align: center; color: #888; margin-top: 3rem; font-size: 0.95em; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">RSS Reader & Zusammenfasser</h1>
        <form method="get" class="mb-4">
            <div class="input-group">
                <input type="text" class="form-control" name="url" placeholder="RSS Feed URL" value="{{ url }}" required>
                <button class="btn btn-primary" type="submit">Feed laden</button>
            </div>
        </form>
        {% if entries %}
            <h2 class="feed-title text-center">Feed: {{ feed_title }}</h2>
            {% for entry in entries %}
                <div class="feed-item">
                    {% if entry.image %}
                        <img src="{{ entry.image }}" class="feed-item-img" alt="Vorschaubild">
                    {% endif %}
                    <div class="feed-item-content">
                        <h3><a href="{{ entry.link }}" target="_blank">{{ entry.title }}</a></h3>
                        <div class="summary">{{ entry.summary }}</div>
                    </div>
                </div>
            {% endfor %}
        {% elif url %}
            <div class="alert alert-warning text-center">Kein Feed gefunden oder ungültige URL.</div>
        {% endif %}
        <div class="footer">
            <hr>
            <span>RSS Reader & Zusammenfasser &copy; {{ 2024 }}</span>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

def summarize(text, max_sentences=2):
    # Einfache Zusammenfassung: Die ersten Sätze nehmen
    soup = BeautifulSoup(text, 'html.parser')
    plain_text = soup.get_text()
    sentences = plain_text.split('.')
    summary = '.'.join(sentences[:max_sentences])
    if len(sentences) > max_sentences:
        summary += '...'
    return summary

def extract_image(entry):
    # 1. media:content oder media_thumbnail
    media_content = entry.get('media_content', [])
    if media_content and isinstance(media_content, list):
        url = media_content[0].get('url')
        if url:
            return url
    media_thumbnail = entry.get('media_thumbnail', [])
    if media_thumbnail and isinstance(media_thumbnail, list):
        url = media_thumbnail[0].get('url')
        if url:
            return url
    # 2. enclosure
    enclosure = entry.get('enclosures', [])
    if enclosure and isinstance(enclosure, list):
        for enc in enclosure:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href')
    # 3. Erstes <img> im summary/description
    html = entry.get('summary', entry.get('description', ''))
    soup = BeautifulSoup(html, 'html.parser')
    img = soup.find('img')
    if img and img.get('src'):
        return img['src']
    return None

@app.route('/', methods=['GET'])
def index():
    url = request.args.get('url', '')
    entries = []
    feed_title = ''
    if url:
        try:
            feed = feedparser.parse(url)
            feed_title = feed.feed.get('title', 'Feed')
            for entry in feed.entries:
                summary = summarize(entry.get('summary', entry.get('description', '')))
                image = extract_image(entry)
                entries.append({
                    'title': entry.get('title', 'Kein Titel'),
                    'link': entry.get('link', '#'),
                    'summary': summary,
                    'image': image
                })
        except Exception as e:
            entries = []
    return render_template_string(HTML_TEMPLATE, entries=entries, url=url, feed_title=feed_title)

if __name__ == '__main__':
    app.run(debug=True) 