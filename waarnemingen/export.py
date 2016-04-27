import sqlite3
from geojson import FeatureCollection, Feature, Point
import json
import itertools

decimals = 5

def export():

	conn = sqlite3.connect("pissebed.db")
	c = conn.cursor()
	obs = c.execute("select * from observations left join species on observations.species_id = species.id where ordo = 'Isopoda' order by name").fetchall()
	print len(obs)

	features = []

	for o in obs:

		lon = o[3]
		lat = o[4]

		if lon is not None and lat is not None:
			feature = Feature(
				geometry = Point((round(lon, decimals), round(lat, decimals))),
				properties = { "name": o[2] }
			)
			features.append(feature)

	collection = FeatureCollection(features)

	with open("data.js", "w") as outfile:
		outfile.write("var data = ")
		outfile.write(json.dumps(collection, separators=(',',':')))
		outfile.write(";")

	conn.close()

def exportnames():

	conn = sqlite3.connect("pissebed.db")
	c = conn.cursor()
	names = c.execute("select species.name from observations left join species on observations.species_id = species.id where ordo = 'Isopoda' group by species.name order by species.name").fetchall()
	print len(names)
	
	with open("names.js", "w") as outfile:
		outfile.write("var names = ")
		outfile.write(json.dumps(list(itertools.chain.from_iterable(names)), separators=(',',':')))
		outfile.write(";")

	conn.close()

export()
exportnames()