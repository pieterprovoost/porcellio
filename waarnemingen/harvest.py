import mechanize
import sys
import re
import random
import time
from  more_itertools import unique_everseen
import pickle
import traceback
import sqlite3
import itertools

br = mechanize.Browser()
br.set_handle_robots(False)
mindelay = 1
maxdelay = 1
maxpages = 2

def extractobs(content):
	content = content.replace("\n", "").replace("\r", "")
	names = re.findall("<em>(.+?)</em>", content)
	dates = re.findall("<th>Datum</th>\s*<td>(.+?)</td>", content)
	precisions = re.findall("<th>precisie</th>\s*<td>(.+?)</td>", content)
	coordinates = re.findall("<th>GPS</th>\s*<td>(.+?)</td>", content)
	routes = re.findall("daddr=([0-9]+\.[0-9]+,[0-9]+\.[0-9]+)", content)

	lat = None
	lon = None
	if len(routes) > 0:
		parts = routes[0].split(",")
		lat = float(parts[0].strip())
		lon = float(parts[1].strip())

	return (
		names[0].strip() if len(names) > 0 else None,
		lon,
		lat,
		precisions[0].strip() if len(precisions) > 0 else None,
		dates[0].strip() if len(dates) > 0 else None
	)

def extractids(content):
	content = content.replace("\n", "").replace("\r", "")
	links = re.findall("</td><td><a class=\"z[0-9]\" href=\"\/soort\/view\/([0-9]+)\"><span class=\"z[0-9]\">(.+?)</span></a>", content)
	return links

def extractobsids(content):
	links = re.findall("\/waarneming\/view\/([0-9]+)", content)
	return links

def harvestspeciesids():
	
	baseurl = "http://waarnemingen.be/soortenlijst.php?g=13&f=0&q=&z=0&p=0&sort_lat=0&sound=0&hidden=0&type=S&all_lang=0&page=%s"
	conn = sqlite3.connect("pissebed.db")
	c = conn.cursor()

	page = 1
	previous = []

	while True:
		try:
			url = baseurl % (page)
			res = br.open(url).read()
			ids = extractids(res)
			print "Page " + str(page) + ": found " + str(len(ids)) + " ids"
			
			current = list(itertools.chain.from_iterable(ids))
			if cmp(previous, current) == 0:
				break
			previous = current

			for id in ids:
				print id
				c.execute("insert or replace into species (id, name) values (?, ?)", (id[0], id[1]))
				conn.commit()

		except Exception, e:
			print "Error: " + str(e)

		page = page + 1
		time.sleep(random.randint(mindelay, maxdelay))

	conn.close()

def harvestobsids():

	baseurl = "http://waarnemingen.be/soort/view/%s?from=1900-01-01&to=2100-01-01&rows=100&page=%s"
	conn = sqlite3.connect("pissebed.db")
	c = conn.cursor()

	ids = c.execute("select id from species")
	ids = list(itertools.chain.from_iterable(ids))

	for id in ids:

		page = 1
		previous = []

		while True:
			try:
				url = baseurl % (id, page)
				res = br.open(url).read()
				obsids = list(unique_everseen(extractobsids(res)))
				print "Species " + str(id) + ", page " + str(page) + ": found " + str(len(obsids)) + " observations"

				if cmp(previous, obsids) == 0:
					break
				previous = obsids

				for obsid in obsids:
					records = c.execute("select * from observations where id = ?", (obsid,)).fetchall()
					if len(records) == 0:
						print "New observation: %s" % obsid
						c.execute("insert into observations (id, species_id) values (?, ?)", (obsid, id))
						conn.commit()
					else:
						print "Observation %s already exists" % obsid

			except Exception, e:
				print "Error: " + str(e)

			page = page + 1
			if page > maxpages:
				break
			time.sleep(random.randint(mindelay, maxdelay))

	conn.close()

def harvestobs():

	baseurl = "http://waarnemingen.be/waarneming/view/%s"
	conn = sqlite3.connect("pissebed.db")
	c = conn.cursor()

	obs = c.execute("select id, species_id from observations where name is null").fetchall()

	for ob in obs:
		id = ob[0]
		spid = ob[1]

		try:
			url = baseurl % (id)
			res = br.open(url).read()
			o = extractobs(res)
			species = (id, spid) + o
			print species
			c.execute("insert or replace into observations values (?, ?, ?, ?, ?, ?, ?)", species)
			conn.commit()

		except Exception, e:
			traceback.print_exc()

		time.sleep(random.randint(mindelay, maxdelay))

	conn.close()

#harvestspeciesids()
harvestobsids()
harvestobs()


