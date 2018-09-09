#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route
# durations based on relations for the routes in OpenStreetMap
#
import os
import sys
import io
import logging
import requests
import json
import datetime
import time

from commons import *
from overpasser import *

try:
    from unidecode import unidecode
except:
    try:
        from Unidecode import unidecode
    except:
        def unidecode(str):
            return str.encode('UTF-8')
#        pass
try:
    import osrm
except:
    pass
import overpass

routing_with_YOUR = False
#routing_with_YOUR = True
prevent_damages = True

logger = logging.getLogger("GTFS_router")

def route_osrm_py(points):
    duration = 0
    result = osrm.match(points, steps=False, overview="full")
    tmp = result[u"total_time"]
    duration = round(float(tmp)/60.0)
    return int(duration)

def route_osrm_web(points):
    duration = 0.0
    routingProfile = "car"
    routingBase = "http://router.project-osrm.org/route/v1/"+routingProfile+"/"
    waypoints = ""
    routingOptions = ""
    routeJSON = None
    for p in points:
        if len(waypoints) == 0:
            waypoints = u"{0},{1}".format(str(p[1]),str(p[0]))
        else:
            waypoints = u"{0};{1},{2}".format(waypoints,str(p[1]),str(p[0]))
    r = False
    while r == False:
        fullRoutingString = routingBase+waypoints+routingOptions
        logger.debug(fullRoutingString)
        try:
            r = requests.get(fullRoutingString, timeout=60)
        except:
            r = False
            raise
        if r.status_code == 502:
            logger.critical(u"502 Bad Gateway in route_osrm_web - returning False")
            return False
        elif r.status_code == 503:
            logger.critical(u"503 Service Unavailable in route_osrm_web - returning False")
            return False
        elif r.status_code == 504:
            logger.critical(u"504 Gateway Timeout in route_osrm_web - returning False")
            return False
        try:
            routeJSON = json.loads(r.content)
        except:
            logger.error(u"Routing object returned is not JSON")
            r = False
    for dr in routeJSON[u"routes"]:
        duration += dr[u"duration"]
    debug_to_screen(u"Duration: {0} seconds / {1} minutes".format(int(duration), int(duration / 60)))
    duration = round(duration / 60)
    return int(duration)

def route_osrm_local(points):
    duration = 0.0
    routingProfile = "car"
    routingBase = "http://127.0.0.1:5000/route/v1/"+routingProfile+"/"
    waypoints = ""
    routingOptions = ""
    routeJSON = None
    for p in points:
        if len(waypoints) == 0:
            waypoints = u"{0},{1}".format(str(p[1]), str(p[0]))
        else:
            waypoints = u"{0};{1},{2}".format(waypoints,str(p[1]), str(p[0]))
    r = False
    while r == False:
        fullRoutingString = routingBase+waypoints+routingOptions
        logger.debug(fullRoutingString)
        try:
            r = requests.get(fullRoutingString, timeout=60)
        except:
            r = False
            raise
        if r.status_code == 502:
            logger.critical(u"502 Bad Gateway in route_osrm_local - returning False")
            return False
        elif r.status_code == 503:
            logger.critical(u"503 Service Unavailable in route_osrm_local - returning False")
            return False
        elif r.status_code == 504:
            logger.critical(u"504 Gateway Timeout in route_osrm_local - returning False")
            return False
        try:
            routeJSON = json.loads(r.content)
        except:
            logger.error(u"Routing object returned is not JSON")
            r = False
    for dr in routeJSON[u"routes"]:
        duration += dr[u"duration"]
    debug_to_screen(u"Duration: {0} seconds / {1} minutes".format(int(duration), int(duration / 60)))
    duration = round(duration / 60)
    return int(duration)

def route_yours_web(points):
    if not routing_with_YOUR:
        return False
    print "YOURS: {0} waypoints".format(len(points))
    duration = 0
    routingBase = "http://www.yournavigation.org/api/1.0/gosmore.php?format=json&v=psv&fast=1"
    fromP = None
    for p in points:
        toP = p
        if fromP == None:
            fromP = toP
        else:
            r = False
            while r == False:
                sys.stdout.write(".")
                sys.stdout.flush()
                fullRoutingString = "{0}&flat={1}&flon={2}&tlat={3}&tlon={4}".format(routingBase, fromP[0], fromP[1], toP[0], toP[1])
                logger.debug(fullRoutingString)
                try:
                    r = requests.get(fullRoutingString, timeout=30)
                except ValueError:
                    r = False
                except requests.exceptions.ReadTimeout:
                    r = False
                except requests.exceptions.ConnectionError:
                    r = False
                try:
                    if len(r.content) < 50:
                        print r.content
                    getDuration = r.content
                    duration += int(getDuration[(getDuration.find("<traveltime>")+12):getDuration.find("</traveltime>")])
                except ValueError:
                    r = False
                except AttributeError:
                    r = False
        fromP = toP
    duration = round( float(duration) / 60.0 ) + round( float(len(points) * 10) / 60.0 )
    return int(duration)

def get_duration(ref, origin, destination, bbox):
    duration = 0
    points = []
    # Overpass get relation
    if unicode(ref).encode('ascii', 'replace').find(u"?") > 0:
        searchString = u"relation[\"type\"=\"route\"][\"route\"=\"bus\"][\"ref\"~\"{0}\"][\"from\"~\"{1}\"][\"to\"~\"{2}\"]({3},{4},{5},{6});out body;>;".format(unicode(ref), unicode(origin), unicode(destination), bbox["s"], bbox["w"], bbox["n"], bbox["e"]).encode('ascii', 'replace').replace(u"?", u".")
    else:
        searchString = u"relation[\"type\"=\"route\"][\"route\"=\"bus\"][\"ref\"=\"{0}\"][\"from\"~\"{1}\"][\"to\"~\"{2}\"]({3},{4},{5},{6});out body;>;".format(unicode(ref), unicode(origin), unicode(destination), bbox["s"], bbox["w"], bbox["n"], bbox["e"]).encode('ascii', 'replace').replace(u"?", u".")
    result = overpasser(searchString)
    nodeList = []
    # Make points list
    if len(result["elements"]) < 1:
        logger.error(u"No relation found: \"%s\" from %s to %s", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        debug_to_screen(u"    Investigate route \"{0}\" from {1} to {2}. Relation not found".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination))) )
        duration = -5
        return duration
    for elm in result[u"elements"]:
        if elm[u"type"] == u"relation":
            if elm[u"members"][0][u"role"] != u"stop" and elm[u"members"][0][u"role"] != u"stop_entry_only":
                logger.error(u"Route \"%s\" from %s to %s doesn't begin with a stop", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
                debug_to_screen(u"    Investigate route \"{0}\" from {1} to {2}. Route doesn't begin with a stop".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination))) )
                return -3
            if elm[u"members"][-1][u"role"] != u"stop" and elm[u"members"][-2][u"role"] != u"stop" and elm[u"members"][-1][u"role"] != u"stop_exit_only" and elm[u"members"][-2][u"role"] != u"stop_exit_only":
                logger.error(u"Route \"%s\" from %s to %s doesn't end with a stop", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)) )
                debug_to_screen(u"    Investigate route \"{0}\" from {1} to {2}. Route doesn't end with a stop".format( unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination))) )
                return -4
            for m in elm[u"members"]:
                if m[u"role"] == u"stop" and m[u"type"] == u"node":
                    nodeList.append(m["ref"])
                elif m[u"role"] == u"stop_entry_only" and m[u"type"] == u"node":
                    nodeList.append(m["ref"])
                elif m[u"role"] == u"stop_exit_only" and m[u"type"] == u"node":
                    nodeList.append(m[u"ref"])
    for testNode in nodeList:
        for elm in result[u"elements"]:
            if elm[u"type"] == u"node" and elm[u"id"] == testNode:
                points.append( ( elm[u"lat"], elm[u"lon"] ) )
    if len(points) == 0:
        logger.error(u"Relation have no defined stops: \"%s\" from %s to %s", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        debug_to_screen(u"    Investigate route \"{0}\" from {1} to {2}. Relation have no stops mapped".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination))) )
        duration = -1
        return duration
    elif len(points) == 1:
        logger.error(u"Relation have only one defined stop: \"%s\" from %s to %s", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        debug_to_screen(u"    Investigate route \"{0}\" from {1} to {2}. Relation have only one defined stop".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination))) )
        duration = -2
        return duration
    elif len(points) == 2 and points[0] == points[1]:
        logger.error(u"Relation \"%s\" start and end with same node without additional nodes", unidecode(unicode(ref)))
        debug_to_screen(u"    Investigate route \"{0}\", starting and ending with same node without additional nodes".format(unidecode(unicode(ref))))
        duration = -6
        return duration
    # Get Route
    passes = 0
    while duration < 1:
        if passes > 10:
            print u"WARNING: Exiting after {0} passes".format(passes)
            break
        try:
            duration = route_osrm_py(points)
        except:
            logger.warning(u"Routing with OSRM Python wrapper failed")
        if duration < 1:
            try:
                duration = route_osrm_local(points)
            except:
                logger.warning(u"Routing with OSRM local API failed")
        if duration < 1:
            try:
                duration = route_osrm_web(points)
            except:
                logger.warning(u"Routing with OSRM Web API failed")
        if duration < 1:
            try:
                duration = route_yours_web(points)
            except:
                logger.warning(u"Routing with YOUR Web API failed")
        passes = passes + 1
        sys.stdout.write("{0} ".format(passes))
        sys.stdout.flush()
        if duration < 1:
            time.sleep(3)
        # Return
    logger.info(u"Route \"%s\" from %s to %s calculated with duration %s minutes", ref, origin, destination, duration)
#    duration = duration + 1
    if duration == 0.0 and prevent_damages:
        print u"WARNING: No working routing API encountered, to avoid damages to duration file, exiting script with this warning!"
        logger.critical(u"No working routing API encountered, to avoid damages to duration file, exiting script with warning!")
        sys.exit(1)
#        return None
    return duration

