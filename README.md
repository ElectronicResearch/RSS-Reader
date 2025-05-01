# RSS Reader & Zusammenfasser

Dieses Projekt ist ein einfacher RSS-Reader mit Web-Oberfläche, der RSS-Feeds abruft, zusammenfasst und im Browser anzeigt.

## Funktionen
- RSS-Feeds per URL abrufen
- Automatische Zusammenfassung der Feed-Inhalte
- Einfache, moderne Web-Oberfläche (Flask-basiert)

## Installation und Betrieb auf einem Server (z.B. Raspberry Pi)

### Voraussetzungen
- Python 3 muss installiert sein (bei Raspberry Pi OS meist schon vorhanden)
- Git ist installiert (`sudo apt install git`)
- Optional: Virtuelle Umgebung (empfohlen)

### Schritt-für-Schritt-Anleitung

1. **Repository klonen**
   ```bash
   git clone https://github.com/ElectronicResearch/RSS-Reader.git
   cd RSS-Reader
   ```

2. **Virtuelle Umgebung erstellen und aktivieren**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Flask-App für Netzwerkzugriff starten**
   Passe die letzte Zeile in `app.py` an (falls nicht schon geschehen):
   ```python
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=True)
   ```
   Starte die App:
   ```bash
   python app.py
   ```
   Jetzt ist die App im gesamten Netzwerk unter `http://<SERVER-IP>:5000` erreichbar.

5. **Zugriff im Netzwerk**
   - Öffne im Browser eines anderen Geräts im selben Netzwerk:  
     `http://<SERVER-IP>:5000`
   - `<SERVER-IP>` ist die IP-Adresse deines Raspberry Pi oder Servers (z.B. `192.168.1.100`).

6. **(Optional) Firewall anpassen**
   ```bash
   sudo ufw allow 5000
   ```

7. **(Optional) Produktionsbetrieb mit Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
   Für den Einsatz im Internet empfiehlt sich zusätzlich ein Reverse Proxy wie nginx.

---

Damit kannst du den RSS-Reader einfach im lokalen Netzwerk oder – mit weiteren Schritten – auch im Internet bereitstellen.

## Automatischer Start beim Systemneustart (z.B. Raspberry Pi)

Um den RSS-Reader automatisch beim Hochfahren des Systems zu starten, empfiehlt sich ein systemd-Service.

### Beispiel: systemd-Service einrichten

1. **Service-Datei erstellen**
   Erstelle die Datei `/etc/systemd/system/rssreader.service` mit folgendem Inhalt (Pfad ggf. anpassen!):
   ```ini
   [Unit]
   Description=RSS Reader Flask App
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/RSS-Reader
   ExecStart=/home/pi/RSS-Reader/venv/bin/python app.py
   Restart=always
   Environment=PYTHONUNBUFFERED=1

   [Install]
   WantedBy=multi-user.target
   ```
   **Hinweis:** Passe `User` und `WorkingDirectory` ggf. an deinen Benutzernamen und Installationspfad an!

2. **Service aktivieren und starten**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable rssreader.service
   sudo systemctl start rssreader.service
   ```

3. **Status prüfen**
   ```bash
   sudo systemctl status rssreader.service
   ```

Jetzt startet der RSS-Reader automatisch bei jedem Neustart des Raspberry Pi bzw. Servers.

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

**Hinweis:**
Das Modul `requests` wird für die Anwendung benötigt und ist jetzt in der `requirements.txt` enthalten. Stelle sicher, dass du alle Abhängigkeiten mit folgendem Befehl installierst:

```bash
pip install -r requirements.txt
```

Falls du das Paket einzeln installieren möchtest:
```bash
pip install requests
```

## Fehlerbehebung (Troubleshooting)

### Fehler: ImportError: No module named feedparser

Dieser Fehler tritt auf, wenn das Modul `feedparser` nicht installiert ist.

**Lösung:**
- Stelle sicher, dass du alle Abhängigkeiten installiert hast:
  ```bash
  pip install -r requirements.txt
  ```
- Falls du eine virtuelle Umgebung verwendest, aktiviere sie vorher:
  ```bash
  source venv/bin/activate
  ```
- Alternativ kannst du das Modul einzeln installieren:
  ```bash
  pip install feedparser
  ```

Weitere Module wie `flask`, `requests` und `beautifulsoup4` werden ebenfalls benötigt und sind in der `requirements.txt` enthalten.

### Fehler: Modul weiterhin nicht gefunden

Falls trotz Installation das Modul weiterhin nicht gefunden wird, prüfe Folgendes:

1. **Virtuelle Umgebung aktivieren (falls verwendet):**
   ```bash
   source venv/bin/activate
   ```
   Danach erneut installieren:
   ```bash
   pip install -r requirements.txt
   ```

2. **Richtiges Python und pip verwenden:**
   Prüfe, ob du das Python und pip aus der venv nutzt:
   ```bash
   which python
   which pip
   ```
   Beide Pfade sollten auf die virtuelle Umgebung zeigen (z.B. `/home/pi/RSS-Reader/venv/bin/python`).

3. **Modul global installieren (wenn keine venv genutzt wird):**
   ```bash
   pip install feedparser
   # oder, falls mehrere Python-Versionen installiert sind:
   python3 -m pip install feedparser
   ```

4. **Installation überprüfen:**
   ```bash
   pip show feedparser
   ```
   Wenn keine Ausgabe erscheint, ist das Modul nicht installiert.

5. **Programm starten:**
   ```bash
   python app.py
   ```

**Neu:**
- Der Reader zeigt jetzt zu jedem Feed-Eintrag ein Vorschaubild an, sofern dieses im Feed vorhanden ist (z.B. als media:content, enclosure oder Bild im Text). 