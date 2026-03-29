# Työvuorojärjestelmä
Alkuperäiset tavoitteet: 
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan työvuoroja.
- Käyttäjä pystyy lisäämään tietoja työvuoroon.
- Käyttäjä näkee sovellukseen lisätyt ilmoitukset.
- Käyttäjä pystyy etsimään työvuoroja hakusanalla.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät ilmoitukset koskien työvuoroja.
- Käyttäjä pystyy valitsemaan työvuorolle yhden tai useamman luokittelun (esim. mikä työ on kyseessä, teema, kohderyhmä).
- Käyttäjä pystyy kommentoimaan työvuoroja
Lisättyjä tavotteita:
- Käyttäjä pystyy valitsemaan vapaana olevia työvuoroja

Tämänhetkinen tilanne:
- Käyttäjä pystyy rekisteröitymään
- Käyttäjä pystyy kirjautumaan
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan työvuoron

Asennusohjeet:
- Kloonaa repositorio: git clone https://github.com/pylkeetu/Tyovuorojarjestelma.git
- Siirry projektikansioon: cd Tyovuorojarjestelma
- Luo virtuaaliympäristö: python -m venv venv
- Aktivoi virtuaaliympäristö: venv\Scripts\activate
- Asenna riippuvuudet: pip install -r requirements.txt

Tietokannan luominen:

Powershell:
- Get-Content schema.sql | sqlite3 database.db

CMD:
- sqlite3 database.db < schema.sql

Sovelluksen käynnistäminen:

- python app.py

- flask run

- Sovellus käynnistyy osoitteeseen: http://127.0.0.1:5000/
