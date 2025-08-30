# Copyright 2025 Ashkan Hosseini

import json, urllib.request, urllib.parse, hou

BASE = ("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/"
        "USA_Counties_Generalized_Boundaries/FeatureServer/0/query")

geo = hou.pwd().geometry()
geo.clear()

for n in ("NAME","STATE_NAME","STATE_ABBR","FIPS","COUNTY_FIPS"):
    if not geo.findPrimAttrib(n):
        geo.addAttrib(hou.attribType.Prim, n, "")

if not geo.findGlobalAttrib("num_features"):
    geo.addAttrib(hou.attribType.Global, "num_features", 0)
if not geo.findGlobalAttrib("status"):
    geo.addAttrib(hou.attribType.Global, "status", "")

def fetch_page(offset):
    params = {
        "where": "1=1",
        "outFields": "NAME,STATE_NAME,STATE_ABBR,FIPS,COUNTY_FIPS",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": 2000
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def add_coordinates(coordinates, attributes):
    if len(coordinates) > 1 and coordinates[0] == coordinates[-1]:
        coordinates = coordinates[:-1]
    polygon = geo.createPolygon()
    for lon, lat in coordinates:
        point = geo.createPoint();
        point.setPosition(hou.Vector3(float(lon), float(lat), 0.0))
        polygon.addVertex(point)
    polygon.setIsClosed(True)
    for k,v in attributes.items():
        polygon.setAttribValue(k, v if isinstance(v, str) else str(v or ""))

total = 0
offset = 0
while True:
    gj = fetch_page(offset)
    features = gj.get("features", [])
    if not features:
        break
    total += len(features)
    for f in features:
        geometry = f.get("geometry", {});
        properties = f.get("properties", {})
        attrs = {
            "NAME": properties.get("NAME",""),
            "STATE_NAME": properties.get("STATE_NAME",""),
            "STATE_ABBR": properties.get("STATE_ABBR",""),
            "FIPS": properties.get("FIPS",""),
            "COUNTY_FIPS": properties.get("COUNTY_FIPS",""),
        }
        if geometry.get("type") == "Polygon":
            coordinates = geometry.get("coordinates", [])
            if coordinates: add_coordinates(coordinates[0], attrs)
        elif geometry.get("type") == "MultiPolygon":
            for coordinates in geometry.get("coordinates", []):
                if coordinates: add_coordinates(coordinates[0], attrs)
    if len(features) < 2000:
        break
    offset += 2000

geo.setGlobalAttribValue("num_features", total)
geo.setGlobalAttribValue("status", "Built {} county features".format(total))
print("Built", total, "county features")
