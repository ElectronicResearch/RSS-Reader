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