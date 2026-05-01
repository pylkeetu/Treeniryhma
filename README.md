# Työvuorojärjestelmä
Alkuperäiset tavoitteet: 
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan työvuoroja.
- Käyttäjä pystyy lisäämään tietoja työvuoroon.
- Käyttäjä näkee sovellukseen lisätyt työvuorot ja niiden tiedot
- Käyttäjä pystyy etsimään työvuoroja hakusanalla (teemoittain).
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät ilmoitukset koskien työvuoroja.
- Käyttäjä pystyy valitsemaan työvuorolle yhden tai useamman luokittelun (esim. mikä työ on kyseessä, teema, kohderyhmä).
- Käyttäjä pystyy kommentoimaan työvuoroja

Tämänhetkinen tilanne:
- Struktuuri pidetty samana, mutta idea muutettu, jotta työ vastaisi enemmän vaatimuksia. Valmennuskäyttöön suunniteltu työvuorojärjestelmä muuttui treeni-alustaksi nimeltä treeniryhmä.
- Sovellukseen pystyy lisäämään treenejä, joihin muilla käyttäjillä on mahdollisuus osallistua.
- Harjoituksia pystyy myös kommentoimaan eli antamaan palautetta, tai kysymään kysymyksiä ennen tai jälkeen harjoituksen.
- Käyttäjillä on myös oma sivu, jossa näkyy tilastoja: Lisätyt treenit, osallistujien keskiarvo, sekä muiden treeneihin osallistumiset.
- Sovelluksen ulkoasu viimeistelty css-avulla
- Kaikki perusvaatimukset täyttyvät

Asennusohjeet:
- Kloonaa repositorio: git clone https://github.com/pylkeetu/Tyovuorojarjestelma.git
- Siirry projektikansioon: cd Tyovuorojarjestelma
- Luo virtuaaliympäristö: python -m venv venv
- Aktivoi virtuaaliympäristö: venv\Scripts\activate (Windows)
- Aktivoi virtuaaliympäristö: source venv/bin/activate (Mac/Linux)
- Asenna riippuvuudet: pip install -r requirements.txt

Tietokannan luominen:

Powershell:
- Get-Content schema.sql | sqlite3 database.db

CMD:
- sqlite3 database.db < schema.sql

Sovelluksen käynnistäminen:

- flask run

- Sovellus käynnistyy osoitteeseen: http://127.0.0.1:5000/
