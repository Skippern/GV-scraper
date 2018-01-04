# GV Scraper
GV Scraper gathers bus information from Grande Vitória, by different companies and sources, in different formats, for use with `osm2gtfs`

The scraper script downloads the timetables on PDF files, supplied on the web site of [Expresso Lorenzutti](http://www.expressolorenzutti.com.br) and [Sanremo](http://www.viacaosanremo.com.br/), and extracts the timetable from it before storing them as a JSON file.

For `Transcol` and `Seletivo`, it uses the same JSON interface, used by the [Ceturb](https://ceturb.es.gov.br) site.

For [Planeta](http://www.viacaoplaneta-es.com.br/destinos-e-horarios-viacao-planeta/), timetables are posted as tables in HTML, each variation is a separate route, using the page index as `ref` tag on the routes.

The JSON format is developed in collaboration with the developers of [osm2gtfs](https://github.com/grote/osm2gtfs) for full functionallity.

# Requirements

The script requires `pdfminer`, `requests`, `overpass`, `logging`, `json`, `workalendar` and `datetime` python moduls and runs under Python2.7

Install dependencies by running

```bash
pip install -r requirements.txt
```

- [osrm](https://github.com/ustroetz/python-osrm) need to be installed manually. If not installed, or if install not importing, fallback to `YOURS` over `requests`

# Usage

In each folder, to obtain the duration of the routes, just run `get_duration.py`. To generate a `times.json` file for `osm2gtfs`, when `durations.json` is up to date, just run `get_times.py`

# Durations

There is a separate script, `get_durations.py` that tests the route relations against `OSRM` to generate a list of durations. This script is only needed to run when significant changes have been done in the itenerary, or new routes have been added. Mark that it will not erase the duration of routes that have been discontinued.

Routing is done by selecting the route relation in question with an `overpass` query, and creates a list of waypoints that are passed to the selected routing engine.

If there are no route relation for a specific route, it returns `-1` duration, this is a signal to the scraper to test against the default value (60). Mark that routes that doesn't have a relation will not be handled by `osm2gtfs` either. Other negative values have different meanings, but for short means that no relation found or impossible to calculate route due to missing waypoints.

`get_durations.py` depends, in addition to the above mentioned, on `overpass` and [osrm](https://github.com/ustroetz/python-osrm) python modules.

As a fallback if `osrm` is not installed, or installation doesn't work, routing can be handled by a `YOURS` web interface, using `requests` calls. This is ment as a fallback, since `YOURS` must route between two nodes, so a long route must be called in a series of calls, instead of `osrm` that can take the entire waypoint list in one call.

# Calendar exceptions

For routes such as _Transcol_, I have added `feriados.py`, requiring [workalendar](https://github.com/novafloss/workalendar) python module. The `workalendar` give a system for handling holidays, and `feriados.py` use them to create different lists of holidays within a given year. This way, `exception`s can be handled in an intelligent manner. `workalendar` handles fixed holidays as well as moving holidays.

# List of services

## Urban services

- [Lorenzutti](http://www.expressolorenzutti.com.br) (Guarapari - PDF)
- [Sanremo](http://www.viacaosanremo.com.br/) (Vila Velha - PDF)
- [Seletivo](https://ceturb.es.gov.br) (Grande Vitória/Ceturb - JSON)
- [Transcol](https://ceturb.es.gov.br) (Grande Vitória/Ceturb - JSON)
- [Viação Grande Vitória](http://sistemas.vitoria.es.gov.br/redeiti/) (Vitória - HTML)

## Intercity services

- [Planeta](http://www.viacaoplaneta-es.com.br/destinos-e-horarios-viacao-planeta/) (HTML)

## Intercity services from DER-ES

- [Alvorada](http://viacaoalvorada.com/) Site not publishing times except for the airport express, and no `ref` numbers.
- [Águia Branca](https://www.aguiabranca.com.br/) Site contain no useful API, but let you buy tickets for destinations, can possibly be used to verify `ref` tags.
- [Sudeste](http://www.viacaosudeste.com.br/)

## Interstate services from ANTT

This will not be pursued, if a proper API can be found, this can be done per company, but also mapping of such routes can be challenging as some of them spans the entire territory of Brazil. It will be preferred if these companies can supply their own `GTFS` sources.

## Other services

- [EFVM]() Estrada Ferroviaria Vitoria Minas. Static `times.json` file.

## Other Sources

- [DER-ES: Quadro de Horários](https://der.es.gov.br/quadro-de-horarios) List of all intercity concessions given by DER-ES with contracted time-tables. This shows the contracts with the state, not necessary the reality. Tebles updated infrequently.
- [ANTT: Consulta Linhas que Fazem Ligação entre Duas Localidades](https://appweb.antt.gov.br/SGP/src.br.gov.antt/apresentacao/consultas/LinhasFazemSecaoDuasLocalidade.aspx) Look up companies and lines connecting two locations. Useful to look up interstate bus connections.
- [ANTT: Informações de empresas, linhas, veículos e seguro](http://www.antt.gov.br/passageiros/Pesquisar_empresas_motoristas_frota_e_seguro.html) Lists different pages to look up companies serving certain points, linking locations, or other. Useful to look up interstate bus connections.
