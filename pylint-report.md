# Pylint-raportti

Pylint antaa seuraavan raportin `app.py` ja `database.py` tiedostoista:

```
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

Olen poistanut käytöstä kaksi varoitusta `pylintrc` tiedostolla: `missing-docstring`, `redefined-outer-name`.

## missing-docstring

Tämä varoitus ei ole hyödyllinen muualla kuin oikeissa ohjelmistokehitystilanteissa.

## redefined-outer-name

Tämä varoittaa [nimien varjostamisesta](https://en.wikipedia.org/wiki/Variable_shadowing), joka on ohjelmointikätevyyden kannalta mainio ominaisuus missä tahansa kielessä. Mielestäni varoitus on turha.
