# GV Scraper
GV Scraper gathers bus information from Grande Vitória, by different companies and sources, in different formats, for use with `osm2gtfs`

The scraper script downloads the timetables on PDF files, supplied on the web site of [Expresso Lorenzutti](http://www.expressolorenzutti.com.br) and [Sanremo](http://www.viacaosanremo.com.br/), and extracts the timetable from it before storing them as a JSON file.

For `Transcol` and `Seletivo`, it uses the same JSON interface, used by the [Ceturb](https://ceturb.es.gov.br) site.

The JSON format is developed in collaboration with the developers of [osm2gtfs](https://github.com/grote/osm2gtfs) for full functionallity.

# Requirements

The script requires `pdfminer`, `requests`, `overpass`, `logging`, `json`, `workalendar` and `datetime` python moduls and runs under Python2.7

Install dependencies by running

`pip install -r requirements.txt`

# Durations

There is a separate script, `get_durations.py` that tests the route relations against `OSRM` to generate a list of durations. This script is only needed to run when significant changes have been done in the itenerary, or new routes have been added. Mark that it will not erase the duration of routes that have been discontinued.

Routing is done by selecting the route relation in question with an `overpass` query, and creates a list of waypoints that are passed to the selected routing engine.

If there are no route relation for a specific route, it returns `-1` duration, this is a signal to the scraper to test against the default value (60). Mark that routes that doesn't have a relation will not be handled by `osm2gtfs` either.

`get_durations.py` depends, in addition to the above mentioned, on `overpass` and [osrm](https://github.com/ustroetz/python-osrm) python modules. Currently, `osrm` needs to be installed manually.

As a fallback if `osrm` is not installed, or installation doesn't work, routing can be handled by a `YOURS` web interface, using `requests` calls. This is ment as a fallback, since `YOURS` must route between two nodes, so a long route must be called in a series of calls, instead of `osrm` that can take the entire waypoint list in one call.

# Calendar exceptions

For routes such as _Transcol_, I have added `feriados.py`, requiring [workalendar](https://github.com/novafloss/workalendar) python module. The `workalendar` give a system for handling holidays, and `feriados.py` use them to create different lists of holidays within a given year. This way, `exception`s can be handled in an intelligent manner. `workalendar` handles fixed holidays as well as moving holidays.

# List of services

## Urban services

- Lorenzutti (Guarapari - PDF)
- Sanremo (Vila Velha - PDF)
- Transcol (Grande Vitória/Ceturb - JSON)
- Seletivo (Grande Vitória/Ceturb - JSON)
- Viação Grande Vitória (Vitória - ?)

## Intercity services

- Alvorada (Manual scraping for now)
- Planeta (Manual scraping for now)

