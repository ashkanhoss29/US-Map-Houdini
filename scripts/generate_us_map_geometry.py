# Copyright 2025 Ashkan Hosseini

import json, urllib.request, hou

print("Downloading US Map JSON")
URL = ("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/"
       "USA_States_Generalized_Boundaries/FeatureServer/0/query?"
       "where=1=1&outFields=STATE_NAME,STATE_ABBR&returnGeometry=true&outSR=4326&f=geojson")
with urllib.request.urlopen(URL, timeout=60) as r:
    gj = json.loads(r.read().decode("utf-8"))
    
geo = hou.pwd().geometry()
geo.clear()

def add_polygon(coordinates, attributes):
    print("Creating polygon for", attributes["STATE_NAME"])
    if len(coordinates) > 1 and coordinates[0] == coordinates[-1]:
        coordinates = coordinates[:-1]
    polygon = geo.createPolygon()
    for lon, lat in coordinates:
        point = geo.createPoint();
        point.setPosition(hou.Vector3(float(lon), float(lat), 0.0))
        polygon.addVertex(point)
    polygon.setIsClosed(True)
    for k,v in attributes.items():
        if geo.findPrimAttrib(k) is None:
            geo.addAttrib(hou.attribType.Prim, k, "")
        polygon.setAttribValue(k, v)

print("Iterating features")
features = gj.get("features", [])
for feature in features:
    geometry = feature.get("geometry", {});
    properties = feature.get("properties", {})
    attributes = {"STATE_NAME": str(properties.get("STATE_NAME","")),
                  "STATE_ABBR": str(properties.get("STATE_ABBR",""))}
    if geometry.get("type") == "Polygon":
        coordinates = geometry.get("coordinates", [])
        if coordinates: add_polygon(coordinates[0], attributes)
    elif geometry.get("type") == "MultiPolygon":
        for coordinates in geometry.get("coordinates", []):
            if coordinates: add_polygon(coordinates[0], attributes)

# print("Write US Map JSON to file")
# print(json.dumps(gj, indent=2))
# with open("C:/Users/Ashkan/Desktop/states.json","w") as f:
#     json.dump(gj, f, indent=2)