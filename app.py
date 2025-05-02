# -*- coding: utf-8 -*-

import feedparser
from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
import time
import json
import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import threading
import time as pytime

app = Flask(__name__)

# SQLite-Datenbank einrichten
engine = create_engine('sqlite:///feedsense.db', echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Feed(Base):
    __tablename__ = 'feeds'
    url = Column(String, primary_key=True)
    title = Column(String)
    last_fetch = Column(DateTime)

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    feed_url = Column(String, ForeignKey('feeds.url'))
    title = Column(String)
    link = Column(String)
    summary = Column(Text)
    image = Column(String)
    published = Column(DateTime)

Base.metadata.create_all(engine)

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
    <title>FeedSense</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="manifest" href="/static/manifest.json">
    <link rel="icon" type="image/png" sizes="192x192" href="/static/icon-192.png">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    <meta name="theme-color" content="#0d6efd">
    <style>
        body { background: #f8f9fa; }
        .container { max-width: 800px; margin-top: 40px; }
        .feed-item { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 1.5rem; margin-bottom: 1.5rem; display: flex; align-items: flex-start; gap: 1.5rem; }
        .feed-item-img { width: 120px; height: 80px; object-fit: cover; border-radius: 6px; flex-shrink: 0; background: #eee; }
        .feed-item-content { flex: 1; min-width: 0; }
        .feed-item h3 { margin-top: 0; font-size: 1.1rem; }
        .summary { color: #444; }
        .feed-title { margin-top: 1.2rem; margin-bottom: 1.2rem; font-size: 1.25rem; }
        h1 { font-size: 1.7rem; margin-bottom: 1.2rem; }
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
        /* Menü-Button fixiert ganz oben rechts */
        .menu-fix-top {
            position: fixed !important;
            top: 0;
            right: 0;
            z-index: 2000;
            margin: 12px 12px 0 0;
        }
        @media (max-width: 600px) {
            h1 { font-size: 1.2rem; }
            .feed-title { font-size: 1rem; margin-top: 0.7rem; margin-bottom: 0.7rem; }
            .feed-item h3 { font-size: 0.98rem; }
            .container { padding: 0 2px; }
            .feed-item { flex-direction: column; align-items: stretch; padding: 1rem; gap: 0.7rem; }
            .feed-item-img { width: 100%; height: 120px; margin-bottom: 0.5rem; }
            .input-group { flex-direction: column !important; gap: 0.5rem; }
            .input-group > * { width: 100% !important; font-size: 1rem; }
            .btn, .form-control, .form-select { min-height: 44px; font-size: 1.05rem; }
            .favorite-btn { min-width: 44px; }
            .footer { font-size: 0.9em; }
            .main-form-row { display: none !important; }
            /* Hintergrundbild vollflächig */
            body, html {
                height: 100%;
            }
            .start-bg {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: url('/static/FeedSense_HB.png') no-repeat center center fixed;
                background-size: cover;
                z-index: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container position-relative">
        <!-- Hamburger-Button ganz oben rechts -->
        <button class="d-block d-sm-none menu-fix-top btn btn-light border" type="button" data-bs-toggle="offcanvas" data-bs-target="#mobileMenu" aria-controls="mobileMenu" style="width:48px; height:48px;">
            <svg width="32" height="32" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect y="3" width="16" height="2" rx="1" fill="#333"/>
                <rect y="7" width="16" height="2" rx="1" fill="#333"/>
                <rect y="11" width="16" height="2" rx="1" fill="#333"/>
            </svg>
        </button>
        <h1 class="text-center mb-4">FeedSense</h1>
        <!-- Offcanvas-Menü für Mobilgeräte -->
        <div class="offcanvas offcanvas-end" tabindex="-1" id="mobileMenu" aria-labelledby="mobileMenuLabel">
          <div class="offcanvas-header">
            <h5 class="offcanvas-title" id="mobileMenuLabel">FeedSense Menü</h5>
            <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
          </div>
          <div class="offcanvas-body">
            <form method="get" class="mb-3">
              <div class="input-group">
                <input type="text" class="form-control" name="url" placeholder="Feed-Adresse" required>
                <button class="btn btn-primary" type="submit">Feed laden</button>
              </div>
            </form>
            <h6>Favoriten</h6>
            <ul class="list-group mb-3">
              {% for fav in favorites %}
                <li class="list-group-item d-flex justify-content-between align-items-center py-2 px-1">
                  <span style="word-break:break-all; font-size:0.97em;">{{ fav }}</span>
                  <span class="d-flex gap-1">
                    <a href="/?url={{ fav }}" class="btn btn-sm btn-success px-2 py-1">&#x2714;</a>
                    <button type="button" class="btn btn-sm btn-danger px-2 py-1" onclick="removeFavorite('{{ fav }}')">&#x2716;</button>
                  </span>
                </li>
              {% else %}
                <li class="list-group-item text-muted">Keine Favoriten</li>
              {% endfor %}
            </ul>
            <a href="/" class="btn btn-outline-secondary w-100">Zur Startseite</a>
          </div>
        </div>
        <form method="get" class="mb-4 main-form-row">
            <div class="input-group flex-column flex-sm-row">
                <select class="form-select mb-2 mb-sm-0" id="favoriteSelect" onchange="loadFavorite()">
                    <option value="">Favoriten auswählen...</option>
                    {% for fav in favorites %}
                        <option value="{{ fav }}" {% if url == fav %}selected{% endif %}>{{ fav }}</option>
                    {% endfor %}
                </select>
                <input type="text" class="form-control mb-2 mb-sm-0" name="url" id="urlInput" placeholder="Feed-Adresse" value="{{ url }}" required style="min-width:0;">
                <button class="btn btn-primary mb-2 mb-sm-0" type="submit">Feed laden</button>
                <button type="button" class="btn btn-outline-primary favorite-btn mb-2 mb-sm-0" onclick="toggleFavorite()">
                    {% if url in favorites %}
                        ★ Entfernen
                    {% else %}
                        ☆ Favorisieren
                    {% endif %}
                </button>
            </div>
        </form>
        {% if not entries and not url %}
            <div class="start-bg"></div>
        {% endif %}
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
            <span>FeedSense &copy; M. Koznjak 2025</span>
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

        function removeFavorite(fav) {
            fetch('/toggle_favorite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({url: fav})
            }).then(r => r.json()).then(data => { if(data.success) location.reload(); });
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
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = False
    if any(m in user_agent for m in ['iphone', 'android', 'ipad', 'mobile', 'windows phone']):
        is_mobile = True

    if url:
        session = SessionLocal()
        # 1. Einträge aus DB (nur letzte 2 Tage)
        two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        db_entries = session.query(Entry).filter(Entry.feed_url == url, Entry.published >= two_days_ago).order_by(Entry.published.desc()).all()
        entries = [
            {
                'title': e.title,
                'link': e.link,
                'summary': e.summary,
                'image': e.image
            } for e in db_entries
        ]
        # 2. Feed online laden
        try:
            feed = feedparser.parse(url)
            feed_title = feed.feed.get('title', 'Feed')
            # Feed-Titel ggf. speichern
            db_feed = session.query(Feed).filter_by(url=url).first()
            if not db_feed:
                db_feed = Feed(url=url, title=feed_title, last_fetch=datetime.datetime.utcnow())
                session.add(db_feed)
            else:
                db_feed.title = feed_title
                db_feed.last_fetch = datetime.datetime.utcnow()
            # Neue Einträge speichern
            for entry in feed.entries:
                # Publikationsdatum bestimmen
                published = None
                if 'published_parsed' in entry and entry.published_parsed:
                    published = datetime.datetime.utcfromtimestamp(time.mktime(entry.published_parsed))
                elif 'updated_parsed' in entry and entry.updated_parsed:
                    published = datetime.datetime.utcfromtimestamp(time.mktime(entry.updated_parsed))
                else:
                    published = datetime.datetime.utcnow()
                # Nur neue Einträge speichern
                exists = session.query(Entry).filter_by(feed_url=url, link=entry.get('link', '#')).first()
                if not exists and published >= two_days_ago:
                    summary = summarize(entry.get('summary', entry.get('description', '')))
                    image = extract_image(entry)
                    session.add(Entry(
                        feed_url=url,
                        title=entry.get('title', 'Kein Titel'),
                        link=entry.get('link', '#'),
                        summary=summary,
                        image=image,
                        published=published
                    ))
            # Alte Einträge löschen
            session.query(Entry).filter(Entry.feed_url == url, Entry.published < two_days_ago).delete()
            session.commit()
            # Nach dem Online-Update erneut aus DB laden
            db_entries = session.query(Entry).filter(Entry.feed_url == url, Entry.published >= two_days_ago).order_by(Entry.published.desc()).all()
            entries = [
                {
                    'title': e.title,
                    'link': e.link,
                    'summary': e.summary,
                    'image': e.image
                } for e in db_entries
            ]
        except Exception as e:
            pass
        finally:
            session.close()

    return render_template_string(HTML_TEMPLATE, 
        entries=entries, 
        url=url, 
        feed_title=feed_title,
        favorites=favorites,
        is_mobile=is_mobile
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

def background_favorites_updater():
    while True:
        session = SessionLocal()
        try:
            favorites = load_favorites()
            two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
            for url in favorites:
                try:
                    feed = feedparser.parse(url)
                    feed_title = feed.feed.get('title', 'Feed')
                    db_feed = session.query(Feed).filter_by(url=url).first()
                    if not db_feed:
                        db_feed = Feed(url=url, title=feed_title, last_fetch=datetime.datetime.utcnow())
                        session.add(db_feed)
                    else:
                        db_feed.title = feed_title
                        db_feed.last_fetch = datetime.datetime.utcnow()
                    for entry in feed.entries:
                        published = None
                        if 'published_parsed' in entry and entry.published_parsed:
                            published = datetime.datetime.utcfromtimestamp(time.mktime(entry.published_parsed))
                        elif 'updated_parsed' in entry and entry.updated_parsed:
                            published = datetime.datetime.utcfromtimestamp(time.mktime(entry.updated_parsed))
                        else:
                            published = datetime.datetime.utcnow()
                        exists = session.query(Entry).filter_by(feed_url=url, link=entry.get('link', '#')).first()
                        if not exists and published >= two_days_ago:
                            summary = summarize(entry.get('summary', entry.get('description', '')))
                            image = extract_image(entry)
                            session.add(Entry(
                                feed_url=url,
                                title=entry.get('title', 'Kein Titel'),
                                link=entry.get('link', '#'),
                                summary=summary,
                                image=image,
                                published=published
                            ))
                    session.query(Entry).filter(Entry.feed_url == url, Entry.published < two_days_ago).delete()
                    session.commit()
                except Exception as e:
                    pass
        finally:
            session.close()
        pytime.sleep(900)  # 15 Minuten

# Thread beim Starten der App starten
threading.Thread(target=background_favorites_updater, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True) 