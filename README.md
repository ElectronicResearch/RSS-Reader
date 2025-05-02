# FeedSense

Dieses Projekt ist ein moderner RSS-Reader mit Web-Oberfläche, der RSS-Feeds abruft und im Browser anzeigt.

## Funktionen
- RSS-Feeds per URL abrufen
- Automatische Zusammenfassung der Feed-Inhalte
- Einfache, moderne Web-Oberfläche (Flask-basiert)

## Favoritenfunktion

Du kannst beliebig viele RSS-Quellen als Favoriten speichern und bequem zwischen ihnen wechseln:

- Über das Dropdown-Menü (Desktop) oder das Menü (Smartphone) kannst du gespeicherte Favoriten direkt auswählen und laden.
- Mit dem Stern-Button neben dem URL-Feld kannst du die aktuelle Feed-URL als Favorit speichern oder wieder entfernen.
- Die Favoriten werden dauerhaft in der Datei `favorites.json` gespeichert.
- Die Favoritenfunktion benötigt keine zusätzlichen Python-Module.

**Hinweis:**
Die Anzahl der gespeicherten Favoriten ist nicht begrenzt. Auf schwächeren Systemen (z.B. Raspberry Pi) empfiehlt es sich jedoch, die Zahl der Favoriten moderat zu halten, da alle Favoriten-Feeds regelmäßig im Hintergrund aktualisiert werden. Viele parallele Feeds können die Systemleistung beeinflussen.

**Tipp:** Die Favoriten sind sofort nach dem Hinzufügen/Entfernen im Dropdown-Menü verfügbar.

## Mobile Optimierung

- Das Layout passt sich automatisch an Smartphones und Tablets an (responsive Design).
- Buttons und Eingabefelder sind auf Touch-Bedienung optimiert.
- Die Darstellung ist kompakter und moderner auf kleinen Bildschirmen.
- Ein Floating-Button zum schnellen Scrollen erscheint auf Mobilgeräten.
- Die App erkennt mobile Geräte automatisch (User-Agent) und kann das Verhalten weiter anpassen.

**Tipp:** Die App kann als Web-App zum Home-Bildschirm hinzugefügt werden und zeigt dann ein schönes RSS-Icon.

## Neue Features (2025)

- **Menü-Button:** Immer ganz oben rechts fixiert, auch auf Smartphones.
- **Startbild:** Das Hintergrundbild wird auf der Startseite vollflächig und responsiv angezeigt.
- **Favoriten-Feeds:** Werden alle 15 Minuten automatisch im Hintergrund aktualisiert und in der SQLite-Datenbank gespeichert. Dadurch sind die Feeds beim Öffnen sofort aktuell und das Laden geht blitzschnell.

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

&copy; M. Koznjak 2025

## Feed-Caching mit SQLite

FeedSense nutzt eine lokale SQLite-Datenbank, um RSS-Feeds und deren Einträge effizient zwischenzuspeichern:

- Beim Laden eines Feeds werden zuerst die letzten 2 Tage aus der Datenbank angezeigt.
- Neue Einträge werden automatisch ergänzt, alte (älter als 2 Tage) werden gelöscht.
- Das sorgt für deutlich schnellere Ladezeiten, weniger Datenverbrauch und eine bessere Nutzererfahrung – auch bei großen Feeds.
- Die Datenbankdatei heißt `feedsense.db` und wird automatisch im Projektverzeichnis angelegt.