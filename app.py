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
    <title>RSS Reader & Zusammenfasser</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        input[type=text] { width: 400px; }
        .feed-item { margin-bottom: 2em; }
        .summary { color: #333; }
    </style>
</head>
<body>
    <h1>RSS Reader & Zusammenfasser</h1>
    <form method="get">
        <input type="text" name="url" placeholder="RSS Feed URL" value="{{ url }}" required>
        <button type="submit">Feed laden</button>
    </form>
    {% if entries %}
        <h2>Feed: {{ feed_title }}</h2>
        {% for entry in entries %}
            <div class="feed-item">
                <h3><a href="{{ entry.link }}" target="_blank">{{ entry.title }}</a></h3>
                <div class="summary">{{ entry.summary }}</div>
            </div>
        {% endfor %}
    {% elif url %}
        <p>Kein Feed gefunden oder ungültige URL.</p>
    {% endif %}
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