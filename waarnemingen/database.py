import sqlite3

def createdb():
	conn = sqlite3.connect("pissebed.db")
	c = conn.cursor()

	c.execute("create table if not exists species (id integer, name text)")
	c.execute("create unique index if not exists species_idx on species(id)")

	c.execute("create table if not exists observations (id integer, species_id integer, name text, longitude real, latitude real, precision text, date text)")
	c.execute("create unique index if not exists observations_idx on observations(id)")

	c.execute("alter table species add class text")
	c.execute("alter table species add ordo text")
	c.execute("alter table species add family text")
	c.execute("alter table species add genus text")
	c.execute("alter table species add authorship text")
	c.execute("alter table species add vernacular text")
	c.execute("alter table species add gbif_id integer")

	conn.commit()
	conn.close()

createdb()
