# Vector map MP  ( plain text) to OSM  (XML) format convertor
# modified by Bedouin
# modified by simon@mungewell.org
# modified by Karl Newman (User:SiliconFiend) to preserve routing topology and parse RouteParam 
# license: GPL V2 or later

# Source MP file should be named as "short.mp"
# Destination.file: will be "out.osm"

import xml.etree.ElementTree as ET

# "Source" key value place here:
attribution = 'gps-club.kz'

# SOURCE FILE:
file_mp = open('short.mp')

# flags and global variable
poi = False
polyline = False
polygon = False
roadid = ''
rNodeToOsmId = {} # map routing node ids to OSM node ids
rnodes = {}

# debug/stats counters
poi_counter = 0
polyline_counter = 0
polygon_counter = 0

osm = ET.Element('osm', version='0.5', generator='Gena' )
osm.text = '\n  '
osm.tail = '\n'
source = ET.Element('tag', k='source',v=attribution)
source.tail = '\n    '
nodeid = -1

# Define the mapping from Garmin type codes to OSM tags
# Note that single items in parentheses need a trailing comma

poitagmap = {
# Cities
(0x0001,): {'place': 'city'},
(0x0002,): {'place': 'city'},
(0x0003,): {'place': 'city'},
(0x0004,): {'place': 'city'},
(0x0005,): {'place': 'city'},
(0x0006,): {'place': 'city'},
(0x0007,): {'place': 'city'},
(0x0008,): {'place': 'city'},
(0x0009,): {'place': 'town'},
(0x000a,): {'place': 'town'},
(0x000b,): {'place': 'village'},
(0x000c,): {'place': 'hamlet'},
(0x000d,): {'place': 'locality'},
(0x000e,): {'place': 'locality'},
(0x000f,): {'place': 'locality'},
(0x0010,): {'place': 'locality'},
(0x0100,): {'place': 'city'},
(0x0200,): {'place': 'city'},
(0x0300,): {'place': 'city'},
(0x0500,): {'place': 'town'},
(0x0600,): {'place': 'town'},
(0x0700,): {'place': 'town'},
(0x0800,): {'place': 'town'},
(0x0900,): {'place': 'town'},
(0x0a00,): {'place': 'town'},
(0x0b00,): {'place': 'suburb'},
(0x0c00,): {'place': 'hamlet'},
(0x0d00,): {'place': 'hamlet'},
(0x0e00,): {'place': 'village'},
(0x0f00,): {'place': 'hamlet'},
(0x1000,): {'place': 'hamlet'},
(0x1100,): {'place': 'hamlet'},
(0x1612,): {'highway': 'gate'},
(0x1616,): {'highway': 'gate'},
# Wrecks/Obstruction
(0x1c00,): {'highway': 'other'},
(0x1c01,): {'highway': 'wreck'},
(0x1c02,): {'highway': 'wreck'},
(0x1c03,): {'highway': 'wreck'},
(0x1c04,): {'highway': 'wreck'},
(0x1c05,): {'highway': 'obstruction'},
(0x1c06,): {'highway': 'obstruction'},
(0x1c07,): {'highway': 'obstruction'},
(0x1c08,): {'highway': 'obstruction'},
(0x1c09,): {'highway': 'obstruction'},
(0x1c0a,): {'highway': 'obstruction'},
(0x1c0b,): {'highway': 'obstruction'},

(0x1e00,): {'place': 'region'},
(0x1f00,): {'place': 'country'},
(0x2900,): {'service': 'other'},
# Food/Drink
(0x2a00,): {'amenity': 'restaurant'},
(0x2a01,): {'amenity': 'restaurant'},
(0x2a02,): {'amenity': 'restaurant'},
(0x2a03,): {'amenity': 'fast_food'},
(0x2a04,): {'amenity': 'fast_food'},
(0x2a05,): {'amenity': 'fast_food'},
(0x2a06,): {'amenity': 'fast_food'},
(0x2a07,): {'amenity': 'fast_food'},
(0x2a08,): {'amenity': 'fast_food'},
(0x2a09,): {'amenity': 'fast_food'},
(0x2a0a,): {'amenity': 'fast_food'},
(0x2a0b,): {'amenity': 'fast_food'},
(0x2a0c,): {'amenity': 'fast_food'},
(0x2a0d,): {'amenity': 'fast_food'},
(0x2a0e,): {'amenity': 'cafe'},
# Accomodation
(0x2b00,): {'tourism': 'hotel'},
(0x2b01,): {'tourism': 'motel'},
(0x2b02,): {'tourism': 'guest_house'},
(0x2b03,): {'tourism': 'caravan_site'},
(0x2b04,): {'tourism': 'guest_house'},
# Attractions
(0x2c00,): {'tourism': 'attraction'},
(0x2c01,): {'tourism': 'theme_park'},
(0x2c02,): {'tourism': 'museum'},
(0x2c03,): {'amenity': 'library'},
(0x2c04,): {'tourism': 'viewpoint'},
(0x2c05,): {'amenity': 'school'},
(0x2c06,): {'leisure': 'park'},
(0x2c07,): {'amenity': 'zoo'},
(0x2c08,): {'leisure': 'sports_centre'},
(0x2c09,): {'amenity': 'public_building'},
(0x2c0a,): {'amenity': 'pub'},
(0x2c0b,): {'amenity': 'place_of_worship'},
(0x2c0c,): {'amenity': 'geiser'},
(0x2c0d,): {'amenity': 'place_of_worship'},
(0x2c0e,): {'amenity': 'place_of_worship'},
(0x2c0f,): {'amenity': 'place_of_worship'},
# Entertainment
(0x2d00,): {'amenity': 'other'},
(0x2d01,): {'amenity': 'theatre'},
(0x2d02,): {'amenity': 'nightclub'},
(0x2d03,): {'amenity': 'cinema'},
(0x2d04,): {'amenity': 'casino'},
(0x2d05,): {'amenity': 'golf_course'},
(0x2d06,): {'amenity': 'sports_center'},
(0x2d07,): {'amenity': 'bowling'},
(0x2d08,): {'leisure': 'sports_centre'},
(0x2d09,): {'leisure': 'sports_centre'},
(0x2d0a,): {'leisure': 'sports_centre'},
(0x2d0b,): {'leisure': 'sports_centre'},
# Shops
(0x2e00,): {'shop': 'convenience'},
(0x2e01,): {'shop': 'convenience'},
(0x2e02,): {'shop': 'supermarket'},
(0x2e03,): {'shop': 'supermarket'},
(0x2e04,): {'shop': 'supermarket'},
(0x2e05,): {'amenity': 'pharmacy'},
(0x2e06,): {'shop': 'convenience'},
(0x2e07,): {'shop': 'convenience'},
(0x2e08,): {'shop': 'convenience'},
(0x2e09,): {'shop': 'convenience'},
(0x2e0a,): {'shop': 'convenience'},
(0x2e0b,): {'shop': 'convenience'},
# Transport Services
(0x2f00,): {'shop': 'dry_cleaning'},
(0x2f01,): {'amenity': 'fuel'},
(0x2f02,): {'amenity': 'car_rental'},
(0x2f03,): {'shop': 'car_repair'},
(0x2f04,): {'aeroway': 'aerodrome'},
(0x2f05,): {'amenity': 'post_office'},
(0x2f06,): {'amenity': 'bank'},
(0x2f07,): {'shop': 'car'},
(0x2f08,): {'amenity': 'bus_station'},
(0x2f09,): {'shop': 'marina_repair'},
(0x2f0b,): {'amenity': 'parking'},
(0x2f0c,): {'tourism': 'picnic_site'},
(0x2f0d,): {'shop': 'car'},
(0x2f0e,): {'amenity': 'car_wash'},
(0x2f10,): {'services': 'other'},
(0x2f11,): {'amenity': 'business_services'},
(0x2f12,): {'amenity': 'phone'},
(0x2f13,): {'services': 'repair'},
(0x2f14,): {'services': 'social'},
(0x2f17,): {'highway': 'bus_stop'},
# Government
(0x3000,): {'amenity': 'townhall'},
(0x3001,): {'amenity': 'police'},
(0x3002,): {'amenity': 'hospital'},
(0x3004,): {'amenity': 'courthouse'},
(0x3007,): {'amenity': 'public_building'},
(0x3008,): {'amenity': 'fire_station'},
(0x4100,): {'leisure': 'fishing'},
(0x4300,): {'amenity': 'ferry_terminal'},
(0x4400,): {'amenity': 'fuel'},
(0x4500,): {'amenity': 'restaurant'},
(0x4600,): {'amenity': 'pub'},
(0x4700,): {'leisure': 'slipway'},
(0x4800,): {'tourism': 'campsite'},
(0x4900,): {'leisure': 'park'},
(0x4a00,): {'tourism': 'picnic_site'},
(0x4b00,): {'amenity': 'hospital'},
(0x4c00,): {'tourism': 'information'},
(0x4d00,): {'amenity': 'parking'},
(0x4e00,): {'amenity': 'toilets'},
(0x4f00,): {'shop': 'beauty'},
(0x4f07,): {'traffic': 'no_transit_sign'},
(0x5000,): {'amenity': 'drinking_water'},
(0x5100,): {'amenity': 'telephone'},
(0x5200,): {'tourism': 'viewpoint'},
(0x5400,): {'sport': 'swimming'},
(0x5800,): {'noexit': 'yes'},
(0x5902,): {'aeroway': 'aerodrome'},
(0x5904,): {'aeroway': 'helipad'},
(0x5904,): {'aeroway': 'helipad'},
(0x5905,): {'aeroway': 'aerodrome'},
(0x5a00,): {'distance_marker': 'yes'},
(0x6200,): {'peak': 'yes'},
(0x6300,): {'man_made': 'survey_point'},
# Man Made
(0x6400,): {'highway': 'gate'},
(0x6401,): {'bridge': 'yes'},
(0x6402,): {'building': 'yes'},
(0x6403,): {'amenity': 'grave_yard'},
(0x6404,): {'amenity': 'place_of_worship'},
(0x6405,): {'amenity': 'public_building'},
(0x6406,): {'highway': 'crossing'},
(0x6407,): {'waterway': 'dam'},
(0x6408,): {'amenity': 'hospital'},
(0x6409,): {'waterway': 'dam'},
(0x640a,): {'place': 'locality'},
(0x640b,): {'military': 'barraks'},
(0x640c,): {'man_made': 'mineshaft'},
(0x640d,): {'man_made': 'pumping_rig'},
(0x640e,): {'leisure': 'park'},
(0x640f,): {'amenity': 'post_office'},
(0x6410,): {'amenity': 'school'},
(0x6411,): {'man_made': 'tower'},
(0x6412,): {'highway': 'trailhead'},
(0x6413,): {'tunnel': 'yes'},
(0x6414,): {'natural': 'spring'},
(0x6415,): {'place': 'locality'},
(0x6416,): {'place': 'locality'},
# HydroGraphics
(0x6501,): {'waterway': 'stream'},
(0x6502,): {'natural': 'island'},
(0x6503,): {'natural': 'water'},
(0x6504,): {'natural': 'water'},
(0x6505,): {'waterway': 'canal'},
(0x6506,): {'waterway': 'canal'},
(0x6507,): {'natural': 'water'},
(0x6508,): {'waterway': 'waterfall'},
(0x6509,): {'natural': 'gayser'},
(0x650a,): {'natural': 'glacier'},
(0x650b,): {'natural': 'water'},
(0x650c,): {'natural': 'island'},
(0x650d,): {'natural': 'water'},
(0x650e,): {'waterway': 'rapid'},
(0x650f,): {'landuse': 'reservoir'},
(0x6511,): {'natural': 'spring'},
# Land features
(0x6600,): {'natural': 'other'},
(0x6601,): {'natural': 'bench'},
(0x6602,): {'place': 'locality'},
(0x6603,): {'natural': 'basin'},
(0x6604,): {'natural': 'beach'},
(0x6605,): {'natural': 'bench'},
(0x6606,): {'natural': 'cape'},
(0x6607,): {'natural': 'cliff'},
(0x6608,): {'natural': 'crater'},
(0x6609,): {'natural': 'flat'},
(0x660a,): {'natural': 'wood'},
(0x660b,): {'natural': 'gap'},
(0x660c,): {'natural': 'gut'},
(0x660d,): {'natural': 'isthmus'},
(0x660e,): {'natural': 'lava'},
(0x660f,): {'natural': 'pillar'},
(0x6610,): {'natural': 'plain'},
(0x6611,): {'natural': 'range'},
(0x6612,): {'natural': 'reserve'},
(0x6613,): {'natural': 'ridge'},
(0x6614,): {'natural': 'rock'},
(0x6615,): {'natural': 'slope'},
(0x6616,): {'natural': 'peak'},
(0x6617,): {'natural': 'valley'},
(0x6618,): {'natural': 'wood'},


(0xf001,): {'amenity': 'bus_station'},
(0xf001,): {'highway': 'bus_stop'},
(0xf002,): {'highway': 'bus_stop'},
(0xf003,): {'highway': 'bus_stop'},
(0xf004,): {'highway': 'bus_stop'},
(0xf006,): {'railway': 'halt'},
(0xf007,): {'railway': 'station'},
(0xf201,): {'highway': 'traffic_signals'}
}
# POLYLINES
polylinetagmap = {
# some road
(0x0000,): {'highway': 'road'},
# major highway
(0x0001,): {'highway': 'trunk'},
# principal 
(0x0002,): {'highway': 'primary'},
# Other hw
(0x0003,): {'highway': 'secondary'},
# arterial
(0x0004,): {'highway': 'secondary'},
# collector road
(0x0005,): {'highway': 'tertiary'},
# residantial
(0x0006,): {'highway': 'residential'},
# alley/private
(0x0007,): {'highway': 'service'},
# hw ramp low speed
(0x0008,): {'highway': 'primary_link'},
(0x0009,): {'highway': 'trunk_link'},
# unpaved
(0x000a,): {'highway': 'track'},
# major hw connector
(0x000b,): {'highway': 'secondary'},
# roundabout
(0x000c,): {'junction': 'roundabout'},

(0x000d,): {'highway': 'road'},
(0x000e,): {'highway': 'road'},
(0x000f,): {'highway': 'road'},
(0x0010,): {'highway': 'road'},
(0x0011,): {'railway': 'platform'},
(0x0012,): {'highway': 'service'},
(0x0013,): {'highway': 'steps'},
# RAILROAD
(0x0014,): {'railway': 'rail'},
# walkway
(0x0016,): {'highway': 'footway'},
(0x0018,): {'waterway': 'stream'},
(0x001a,): {'route': 'ferry'},
(0x001b,): {'route': 'ferry'},

# boundary state/province
(0x001c,): {'boundary': 'administrative'},
# county
(0x001d,): {'boundary': 'administrative'},
# international boundary
(0x001e,): {'boundary': 'administrative'},

(0x001f,): {'waterway': 'river'},
(0x0026,): {'waterway': 'stream'},
(0x0027,): {'aeroway': 'runway'},
(0x0028,): {'man_made': 'pipeline'},
(0x0029,): {'power': 'line'},
(0x003f,): {'railway': 'subway'},
(0x0042,): {'highway': 'unsurfaced'},
(0x0044,): {'waterway': 'drain'},
(0x0045,): {'boundary': 'administrative'},
(0x0048,): {'highway': 'pedestrian'},
(0x0049,): {'highway': 'living_street'}
}
# POLYGONES
polygontagmap = {
(0x0001,): {'landuse': 'residential'},
(0x0002,): {'landuse': 'residential'},
(0x0003,): {'landuse': 'residential'},
(0x0004,): {'landuse': 'millitary'},
(0x0005,): {'amenity': 'parking'},
(0x0006,): {'amenity': 'parking'},
(0x0007,): {'landuse': 'aerodrome'},
(0x0008,): {'landuse': 'retail'},
(0x000a,): {'amenity': 'school'},
(0x000b,): {'building': 'hospital'},
(0x000c,): {'landuse': 'industrial'},
(0x000d,): {'natural': 'wood'},
(0x0013,): {'building': 'yes'},
(0x0014,): {'natural': 'wood'},
(0x0015,): {'natural': 'wood'},
(0x0016,): {'leisure': 'park'},
(0x0017,): {'leisure': 'park'},
(0x0018,): {'sport': 'golf'},
(0x001a,): {'landuse': 'cemetery'},
(0x001e,): {'natural': 'wood'},
(0x001f,): {'natural': 'wood'},
(0x0020,): {'natural': 'wood'},
(0x0028,): {'natural': 'coastline'},
(0x003b,): {'waterway': 'riverbank'},
(0x003c,): {'waterway': 'riverbank'},
(0x0040,): {'waterway': 'riverbank'},
(0x0041,): {'waterway': 'riverbank'},
(0x0045,): {'waterway': 'riverbank'},
(0x0047,): {'waterway': 'riverbank'},
(0x0048,): {'waterway': 'riverbank'},
(0x0049,): {'waterway': 'riverbank'},
(0x004c,): {'waterway': 'intermittent'},
(0x004e,): {'leisure': 'garden'},
(0x004f,): {'natural': 'scrub'},
(0x0050,): {'landuse': 'forest'},
(0x0051,): {'natural': 'marsh'},
(0x0052,): {'landuse': 'forest'},
(0x0053,): {'natural': 'beach'},
(0x006c,): {'building': 'yes'},
(0x006d,): {'building': 'yes'},
(0x006e,): {'building': 'terminal'},
(0x006f,): {'amenity': 'public_building'},
(0x006f,): {'amenity': 'public_building'},
(0x0081,): {'landuse': 'forest'},
(0x0082,): {'landuse': 'forest'},
(0x0083,): {'landuse': 'forest'},
(0x0084,): {'landuse': 'forest'},
(0x0085,): {'landuse': 'forest'},
(0x0086,): {'leisure': 'garden'},
(0x0087,): {'leisure': 'garden'},
(0x0088,): {'leisure': 'garden'},
(0x008b,): {'natural': 'marsh'},
(0x008f,): {'landuse': 'forest'},
(0x0090,): {'landuse': 'forest'},
(0x0091,): {'landuse': 'forest'},
(0x0096,): {'natural': 'marsh'},
(0x0098,): {'natural': 'wood'},
(0x2d0a,): {'leisure': 'sports_centre'},
(0x3002,): {'amenity': 'hospital'},
(0x6402,): {'building': 'yes'},
(0x6408,): {'building': 'clinic'}
}

for line in file_mp:
    
    # Marker for start of sections
    # NODE:
    if line.startswith(('[POI]','[RGN10]','[RGN20]')):
        node = ET.Element('node', visible='true', id=str(nodeid))
        nodeid -= 1
        #node.append(source)
        poi = True
        elementtagmap = poitagmap
        poi_counter += 1

    # WAY:
    if line.startswith(('[POLYLINE]','[RGN40]')):
        node = ET.Element('way', visible='true', id=str(nodeid))
        nodeid -= 1
        node.append(source)
        polyline = True
        elementtagmap = polylinetagmap
        rnodes = {} # Track routing nodes for current polyline
        polyline_counter += 1

    # POLYGONE:
    if line.startswith(('[POLYGON]','[RGN80]')):
        node = ET.Element('way', visible='true', id=str(nodeid))
        nodeid -= 1
        node.append(source)
        polygon = True
        elementtagmap = polygontagmap
        polygon_counter += 1

    # parsing data
    if poi or polyline or polygon:
        
        if line.startswith('Label'):
            label = line.split('=')[1].strip()
            # Now strip out control codes such as ~[0x2f]
            codestart = label.find('~[')
            if codestart != -1:
                codeend = label.find(']',codestart)
                if codeend != -1:
                    label = label[0:codestart] + ' ' + label[codeend+1:]
            tag = ET.Element('tag', k='name',v=unicode(label.strip().title(),'cp1251')) # convert to title case
            tag.tail = '\n    '
            node.append(tag)

        if line.startswith('Type'):
            typecode = line.split('=')[1].strip()
            #tag = ET.Element('tag', k='garmin_type',v=typecode)
            #tag.tail = '\n    '
            #node.append(tag)
            typecode = int(typecode, 16) 
            for codes, taglist in elementtagmap.iteritems():
                if typecode in codes:
                    for key, value in taglist.iteritems():
                        tag = ET.Element('tag', k=key, v=value)
                        tag.tail = '\n    '
                        node.append(tag)

        #if line.startswith('RoadID'):
            #roadid = line.split('=')[1].strip()
            #tag = ET.Element('tag', k='catmp-RoadID',v=roadid)
            #tag.tail = '\n    '
            #node.append(tag)

        # RouteParam: speed, class,  attrib1, attrib2,
        #    emergency, goods, motorcar, psv, taxi, foot, bicycle, hgv
        if line.startswith('RouteParam'):
            rparams = line.split('=')[1].split(',')
            # speedval has speeds in km/h corresponding to RouteParam speed value index
            speedval = [8, 20, 40, 56, 72, 93, 108, 128]
            speed = ET.Element('tag', k='maxspeed', v=str(speedval[int(rparams[0])]))
            speed.tail = '\n    '
            #node.append(speed)
            rclass = ET.Element('tag', k='garmin_road_class', v=str(rparams[1]))
            rclass.tail = '\n    '
            #node.append(rclass)
            for att, attval in zip(('oneway', 'toll'), rparams[2:3]):
                if int(attval):
                    attrib = ET.Element('tag', k=att, v='true')
                    attrib.tail = '\n    '
                    node.append(attrib)
            # Note: taxi is not an approved access key
            vehicles = ['emergency', 'goods', 'motorcar', 'psv', 'taxi', 'foot', 'bicycle', 'hgv']
            for veh, res in zip(vehicles, rparams[4:]):
                vehtag = ET.Element('tag', k=veh, v=('yes', 'no')[int(res)]) 
                vehtag.tail = '\n    '
                #node.append(vehtag)

        # Get nodes from all zoom levels (ie. Data0, Data1, etc)
        # TODO: Only grab the lowest-numbered data line (highest-resolution) and ignore the rest
        if line.startswith('Data'):
            if poi:
                coords = line.split('=')[1].strip()
                coords = coords.split(',')
                node.set('lat',str(float(coords[0][1:])))
                node.set('lon',str(float(coords[1][:-1])))
            if polyline or polygon:
                # Just grab the line and parse it later when the [END] element is encountered
                coords = line.split('=')[1].strip() + ','
                # TODO: parse out "holes" in a polygon by reading multiple Data0 lines and
                # constructing a multipolygon relation

        if line.startswith('Nod'):
            if polyline:
                # Store the point index and routing node id for later use
                nod = line.split('=')[1].strip().split(',', 2)
                rnodes[nod[0]] = nod[1]

        if line.startswith('[END]'):
            if polyline or polygon:
                # Have to write out nodes as they are parsed
                nodidx = 0
                nodIds = []
                reused = False
                while coords != '':
                    coords = coords.split(',', 2)
                    if str(nodidx) in rnodes:
                        if rnodes[str(nodidx)] in rNodeToOsmId:
                            curId = rNodeToOsmId[str(rnodes[str(nodidx)])]
                            reused = True
                        else:
                            curId = nodeid
                            nodeid -= 1
                            rNodeToOsmId[str(rnodes[str(nodidx)])] = curId
                    else:
                        curId = nodeid
                        nodeid -= 1
                    nodIds.append(curId)
                    # Don't write another node element if we reused an existing one
                    if not reused:
                        nodes = ET.Element('node', visible='true', id=str(curId), lat=str(float(coords[0][1:])), lon=str(float(coords[1][:-1])))
                        nodes.text = '\n    '
                        nodes.tail = '\n  '
                        osm.append(nodes)
                    coords = coords[2]
                    reused = False
                    nodidx += 1
                nodidx = 0
                for ndid in nodIds:
                    nd = ET.Element('nd', ref=str(ndid))
                    nd.tail = '\n    '
                    node.append(nd)
            if polygon:
                nd = ET.Element('nd', ref=str(nodIds[0]))
                nd.tail = '\n    '
                node.append(nd)

            poi = False 
            polyline = False 
            polygon = False 
            roadid = ''
            rnodes = {} # Clear out routing nodes to prepare for next entity

            node.text = '\n    '
            node.tail = '\n  '
            
            osm.append(node)

# writing to file
f = open('out.osm', 'w')
f.write(ET.tostring(osm).encode('utf-8'))

# dump some stats
print '======'
print 'Totals'
print '======'
print 'POI', poi_counter
print 'POLYLINE', polyline_counter
print 'POLYGON', polygon_counter
print 'Last nodeid', nodeid
