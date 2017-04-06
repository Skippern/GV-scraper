# PDF-scraper-Lorenzutti
PDF Scraper to extract time tables for Expresso Lorenzutti, for use with osm2gtfs

The scraper script downloads the timetables on PDF files, supplied on the web site of [Expresso Lorenzutti](http://www.expressolorenzutti.com.br) and extracts the timetable from it before storing them as a JSON file.

The script requires `pdfminer`, `requests`, `logging`, `json`, and `datetime` python moduls and runs under Python2.7

The JSON format is developed in collaboration with the developers of [osm2gtfs](https://github.com/grote/osm2gtfs) for full functionallity.

# Requirements

Install dependencies by running

`pip install -r requirements.txt`

# Durations

There is a separate script, `get_durations.py` that tests the route relations against `OSRM` to generate a list of durations. This script is only needed to run when significant changes have been done in the itenerary, or new routes have been added. Mark that it will not erase the duration of routes that have been discontinued.

If there are no route relation for a specific route, it returns `-1` duration, this is a signal to the scraper to test against the default value (60). Mark that routes that doesn't have a relation will not be handled by `osm2gtfs` either.

`get_durations.py` depends, in addition to the above mentioned, on `overpass` and [osrm](https://github.com/ustroetz/python-osrm) python modules. Currently, `osrm` needs to be installed manually

