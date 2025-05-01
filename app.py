# -*- coding: utf-8 -*-

import feedparser
from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
import time
import json
import os

app = Flask(__name__)

# Laden der Favoriten
def load_favorites():
    try:
        with open('favorites.json', 'r') as f:
            return json.load(f)['favorites']
    except:
        return []

# Speichern der Favoriten
def save_favorites(favorites):
    with open('favorites.json', 'w') as f:
        json.dump({'favorites': favorites}, f)

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
        .feed-item { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 1.5rem; margin-bottom: 1.5rem; display: flex; align-items: flex-start; gap: 1.5rem; }
        .feed-item-img { width: 120px; height: 80px; object-fit: cover; border-radius: 6px; flex-shrink: 0; background: #eee; }
        .feed-item-content { flex: 1; min-width: 0; }
        .feed-item h3 { margin-top: 0; }
        .summary { color: #444; }
        .feed-title { margin-top: 2rem; margin-bottom: 2rem; }
        .footer { text-align: center; color: #888; margin-top: 3rem; font-size: 0.95em; }
        #scrollTopBtn {
            display: none;
            position: fixed;
            bottom: 40px;
            right: 40px;
            z-index: 99;
            border: none;
            outline: none;
            background-color: #0d6efd;
            color: white;
            cursor: pointer;
            padding: 12px 18px;
            border-radius: 50%;
            font-size: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        #scrollTopBtn:hover {
            background-color: #0b5ed7;
        }
        .favorite-btn {
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">RSS Reader & Zusammenfasser</h1>
        <form method="get" class="mb-4">
            <div class="input-group">
                <select class="form-select" id="favoriteSelect" onchange="loadFavorite()">
                    <option value="">Favoriten auswählen...</option>
                    {% for fav in favorites %}
                        <option value="{{ fav }}" {% if url == fav %}selected{% endif %}>{{ fav }}</option>
                    {% endfor %}
                </select>
                <input type="text" class="form-control" name="url" id="urlInput" placeholder="RSS Feed URL" value="{{ url }}" required>
                <button class="btn btn-primary" type="submit">Feed laden</button>
                <button type="button" class="btn btn-outline-primary favorite-btn" onclick="toggleFavorite()">
                    {% if url in favorites %}
                        ★ Entfernen
                    {% else %}
                        ☆ Favorisieren
                    {% endif %}
                </button>
            </div>
        </form>
        {% if entries %}
            <h2 class="feed-title text-center">Feed: {{ feed_title }}</h2>
            {% for entry in entries %}
                <div class="feed-item">
                    <img src="{{ entry.image }}" class="feed-item-img" alt="Vorschaubild">
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
    <button onclick="scrollToTop()" id="scrollTopBtn" title="Nach oben">&#8679;</button>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Scroll-to-Top Button
        const scrollBtn = document.getElementById('scrollTopBtn');
        window.onscroll = function() {
            if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
                scrollBtn.style.display = 'block';
            } else {
                scrollBtn.style.display = 'none';
            }
        };
        function scrollToTop() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }

        function loadFavorite() {
            const select = document.getElementById('favoriteSelect');
            const urlInput = document.getElementById('urlInput');
            if (select.value) {
                urlInput.value = select.value;
                document.querySelector('form').submit();
            }
        }

        function toggleFavorite() {
            const url = document.getElementById('urlInput').value;
            if (!url) return;

            fetch('/toggle_favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({url: url})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        }
    </script>
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
    # 3. image Feld direkt
    if 'image' in entry and isinstance(entry['image'], dict):
        url = entry['image'].get('href') or entry['image'].get('url')
        if url:
            return url
    # 4. Erstes <img> im summary/description
    html = entry.get('summary', entry.get('description', ''))
    soup = BeautifulSoup(html, 'html.parser')
    img = soup.find('img')
    if img and img.get('src'):
        return img['src']
    # 5. OpenGraph/Twitter-Card von verlinkter Seite
    link = entry.get('link')
    if link:
        try:
            resp = requests.get(link, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                page = BeautifulSoup(resp.text, 'html.parser')
                # OpenGraph
                og = page.find('meta', property='og:image')
                if og and og.get('content'):
                    return og['content']
                # Twitter Card
                tw = page.find('meta', attrs={'name': 'twitter:image'})
                if tw and tw.get('content'):
                    return tw['content']
        except Exception as e:
            print(f"DEBUG: Fehler beim Parsen von {link}: {e}")
            pass
    # 6. Fallback: Platzhalterbild
    return 'https://via.placeholder.com/120x80?text=Kein+Bild'

@app.route('/', methods=['GET'])
def index():
    url = request.args.get('url', '')
    entries = []
    feed_title = ''
    favorites = load_favorites()
    
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
    
    return render_template_string(HTML_TEMPLATE, 
        entries=entries, 
        url=url, 
        feed_title=feed_title,
        favorites=favorites
    )

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    favorites = load_favorites()
    if url in favorites:
        favorites.remove(url)
    else:
        favorites.append(url)
    
    save_favorites(favorites)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True) 