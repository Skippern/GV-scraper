#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route durations based on relations for the routes in OpenStreetMap
from common import *

import logging
import overpass
import requests
import json
import sys
import time

logger = logging.getLogger("GTFS_overpass")

def overpasser(searchString):
    logger.debug(searchString)
    api = overpass.API()
    result = False
    while result == False:
        try:
            result = api.Get(searchString, responseformat="json")
        except overpass.errors.OverpassSyntaxError as e:
            logger.debug(u"overpass.errors.OverpassSyntaxError, sleeping for 120s")
            time.sleep(120)
            continue
        except overpass.errors.UnknownOverpassError as e:
            logger.debug(u"overpass.errors.UnknownOverpassError, sleeping for 120s")
            time.sleep(120)
            continue
        except overpass.errors.TimeoutError as e:
            logger.debug(u"overpass.errors.TimeoutError, sleeping for 120s")
            time.sleep(120)
            continue
        except overpass.errors.ServerRuntimeError as e:
            logger.debug(u"overpass.errors.ServerRuntimeError, sleeping for 120s")
            time.sleep(120)
            continue
        except overpass.errors.MultipleRequestsError as e:
            logger.debug(u"overpass.errors.MultipleRequestsError, sleeping for 120s")
            time.sleep(120)
            continue
        except overpass.errors.ServerLoadError as e:
            logger.debug(u"overpass.errors.ServerLoadError, sleeping for 120s")
            time.sleep(120)
            continue
        except requests.exceptions.ConnectionError as e:
            logger.debug(u"requests.exceptions.ConnectionError, sleeping for 120s")
            time.sleep(120)
            continue
        try:
            test = json.loads(json.dumps(result))
        except TypeError as e:
            result = False
            logger.debug(u"Retrieved data was not JSON readable (TypeError), sleeping for 120s and trying again")
            time.sleep(120)
        except ValueError as e:
            result = False
            logger.debug(u"Retrieved data was not JSON readable (ValueError), sleeping for 120s and trying again")
            time.sleep(120)
    return result
