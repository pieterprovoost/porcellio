import sqlite3
import requests

def gbif():

	baseurl = "http://api.gbif.org/v1/species?name=%s"

	conn = sqlite3.connect("pissebed.db")
	c = conn.cursor()
	names = c.execute("select distinct(name) from species where gbif_id is null").fetchall()
	
	for n in names:

		name = n[0]
		url = baseurl % name
		r = requests.get(url)
		content = r.json()
		results = content["results"]

		if len(results) > 0:
			print name
			r = results[0]
			c.execute("update species set class=?, ordo=?, family=?, genus=?, authorship=?, vernacular=?, gbif_id=? where name = ?",
				(
					r["class"] if "class" in r else None,
					r["order"] if "order" in r else None,
					r["family"] if "family" in r else None,
					r["genus"] if "genus" in r else None,
					r["authorship"] if "authorship" in r else None,
					r["vernacularName"] if "vernacularName" in r else None,
					r["key"] if "key" in r else None,
					name
				)
			)
			conn.commit()

	conn.close()

gbif()