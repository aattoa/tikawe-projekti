# tikawe projekti

## Kuvaus

Yksinkertainen viestipalvelu, joka sallii vapaan viestinnän eri kanavilla.

Käyttäjä pystyy:

- Luomaan tilin ja kirjautumaan sisään.
- Etsimään ja luomaan kanavia.
- Julkaisemaan viestejä, kunhan on kirjautut sisään.
- Poistamaan omia viestejään.
- Muokkaamaan omia viestejään.
- Lisäämään tykkäyksiä muiden käyttäjien viesteihin.
- Tarkastelemaan halutun käyttäjän viestejä ja tilastoja.
- Luokittelemaan omat viestinsä.
- Hakemaan viestejä luokittelun perusteella.

Sovellus estää CSRF-hyökkäykset kurssimateriaalin mukaisesti.

## Testaaminen

Luo tietokanta komennolla: `sqlite3 database.db < schema.sql`

Käynnistä paikallinen flask palvelin: `flask run`

Avaa viestipalvelu selaimessa: [http://localhost:5000](http://localhost:5000)

## Mahdolliset tulevat parannukset
- Varmista että yksi käyttäjä ei tykkää viestistä enemmän kuin kerran.
- Salli tilin poisto
