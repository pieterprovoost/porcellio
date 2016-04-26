import sqlite3
from geojson import FeatureCollection, Feature, Point
import json

def export():

	conn = sqlite3.connect("pissebed.db")
	c = conn.cursor()
	obs = c.execute("select * from observations left join species on observations.species_id = species.id where ordo = 'Isopoda' limit 1000").fetchall()
	print len(obs)

	features = []

	for o in obs:

		lon = o[3]
		lat = o[4]

		if lon is not None and lat is not None:
			feature = Feature(
				geometry = Point((lon, lat)),
				properties = { "name": o[2] }
			)
			features.append(feature)

	collection = FeatureCollection(features)

	with open("data.js", "w") as outfile:
		outfile.write("var data = ")
		json.dump(collection, outfile)
		outfile.write(";")

	conn.close()

export()