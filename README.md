# RSS Reader & Zusammenfasser

Dieses Projekt ist ein einfacher RSS-Reader mit Web-Oberfläche, der RSS-Feeds abruft, zusammenfasst und im Browser anzeigt.

## Funktionen
- RSS-Feeds per URL abrufen
- Automatische Zusammenfassung der Feed-Inhalte
- Einfache, moderne Web-Oberfläche (Flask-basiert)

## Installation
1. Repository klonen:
   ```bash
   git clone <REPO-URL>
   cd rss_reader
   ```
2. Virtuelle Umgebung (optional, empfohlen):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

## Nutzung
1. Anwendung starten:
   ```bash
   python app.py
   ```
2. Im Browser öffnen: [http://localhost:5000](http://localhost:5000)
3. RSS-Feed-URL eingeben und auf "Feed laden" klicken.

## Beispiel-Feeds
- https://www.tagesschau.de/xml/rss2
- https://www.heise.de/rss/heise-atom.xml

## Veröffentlichung auf GitHub
1. Repository initialisieren (falls noch nicht geschehen):
   ```bash
   git init
   git remote add origin https://github.com/<DEIN_USERNAME>/rss_reader.git
   ```
2. Änderungen committen und pushen:
   ```bash
   git add .
   git commit -m "Initialer RSS Reader Commit"
   git push -u origin master
   ```

## Lizenz
MIT 