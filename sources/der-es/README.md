# DER-ES sources

The information in the `JSON` files in this folder are manually derived from `PDF` files provided at the [DER-ES: Quadra de Horarios](https://der.es.gov.br/quadro-de-horarios) page. Each `JSON` corresponds an individual `PDF` file.

The format is a basic dictionary, containing the information a scraper would need to build a `OSM2GTFS` schedule.

These files are manually maintained, and are meant to allow creating inter-urban GTFS files where web sites does not provide scrapable information, or operators doesn't supply any useful API or other sources. Where schedules are maintained by operator, this should be used instead of these files.

# Fields

- `operator` The operator company
- `operator:ref` Company reference with DER-ES
- `updated` Date when consession data was updated with DER-ES

## `routes`

- `###/#` Route reference with DER-ES (not necessary operators `ref` key, can be mapped as `ref:der-es`)
- `name` A name for the route
- `ref` Operator's `ref`, the one that should be used in the relation if known
- `from` Where the route goes from, same as the relation `from` tag
- `to` Where the route goes to, same as the relation `to` tag
- `via` Optional, any via points in the route, same as the relation `via` tag, as single string or array of strings
- `services` ISO date codes for when the route services
- `times` Array of start times for the `from` location
- `note` Any notes related to the route
- `start_date` and `end_date` for routes that have limits, i.e. routes that will expire, or routes with different times in high season and off-season.
