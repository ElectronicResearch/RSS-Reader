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
        .feed-item { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 1.5rem; margin-bottom: 1.5rem; }
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
                    <h3><a href="{{ entry.link }}" target="_blank">{{ entry.title }}</a></h3>
                    <div class="summary">{{ entry.summary }}</div>
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
                entries.append({
                    'title': entry.get('title', 'Kein Titel'),
                    'link': entry.get('link', '#'),
                    'summary': summary
                })
        except Exception as e:
            entries = []
    return render_template_string(HTML_TEMPLATE, entries=entries, url=url, feed_title=feed_title)

if __name__ == '__main__':
    app.run(debug=True) 