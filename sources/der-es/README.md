# DER-ES sources

The information in the `JSON` files in this folder are manually derived from `PDF` files provided at the [DER-ES: Quadra de Horarios](https://der.es.gov.br/quadro-de-horarios) page. Each `JSON` corresponds an individual `PDF` file.

The format is a basic dictionary, containing the information a scraper would need to build a `OSM2GTFS` schedule.

These files are manually maintained, and are meant to allow creating inter-urban GTFS files where web sites does not provide scrapable information, or operators doesn't supply any useful API or other sources. Where schedules are maintained by operator, this should be used instead of these files.
