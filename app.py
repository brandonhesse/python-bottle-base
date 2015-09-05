import bottle # For bottle
from bottle.ext import sqlite # For a database (where your "data" will be stored for requests)

import functools
import json # JSON for Javascript Transmissions
from standardjson import StandardJSONEncoder # An improved JSON class converter for items like datetime.datetime

import datetime, time
from random import uniform

bottle.debug(True)
root = bottle.Bottle() # Build a bottle application container.

# Improve the JSON output utilizing a modified dumps and reinstalling the JSONPlugin
improvedDumps = functools.partial(json.dumps, cls=StandardJSONEncoder, sort_keys=True)
improvedDumps.__doc__ = 'Covert to a JSON string utilizing the improvements of standardjson'
root.uninstall(bottle.JSONPlugin)
root.install(bottle.JSONPlugin(improvedDumps))

# Add SQLite database power
# This will inject into any route below that has "db" as a parameter
# a SQLite database instance automatically
plugin = sqlite.Plugin(dbfile='data.sqlite3')
root.install(plugin)

# Bind template to a jinja2 Template
template = bottle.jinja2_template

# Route definitions via annotations
# Index is default entry point
@root.get('/')
def index():
	return template('index')

# Generate a set of random points for testing
@root.get('/api/point/rand')
def api_point_rand():
	# Build a list of dictionaries (to make JS objects, tuples produce arrays)
	points = [{ 'id': None, 'x':uniform(1,10), 'y':uniform(1,10) } for i in range(20)]
	return { 'lastRetrieved': datetime.datetime.now(), 'data': points }

# Create the database
@root.get('/db/create')
def db_create(db):
	error = None
	try:
		c = db.execute("""
			CREATE TABLE points (
				`id` integer not null primary key, 
				`x` real not null default 0.0,
				`y` real not null default 0.0
			)
		""")
		db.commit()
	except sqlite.sqlite3.Error as er: # Handle create error
		error = er.args[0]
	
	return template('create', error=error)

# Assign multiple routes to a single endpoint
@root.get('/api/point/points')
@root.get('/api/point/points/<row_id:int>')
def api_point_get(db, row_id=None):
	if not row_id: # If a user does not provide a row_id, get all
		c = db.execute('SELECT id, x, y FROM points')
		print("Got multiple points")
		rows = c.fetchall()
		data = [{ 'id': row[0], 'x':row[1], 'y':row[2]} for row in rows]
	else: # Get a specific point
		c = db.execute('SELECT * FROM points WHERE id = ?', (row_id, )) #escapes the id safely
		print("Got a single points")
		row = c.fetchone()
		data = { 'id': row[0], 'x':row[1], 'y':row[2] } 
	return { 'lastRetrieved': datetime.datetime.now(), 'data': data }

# Make and store new points via JSON
@root.post('/api/point/new')
def db_insert_point(db):
	error = None
	# Comes in as POST request with application/json as sending type
	x = bottle.request.json.get('x')
	y = bottle.request.json.get('y')
	# Insert data. First item is a timestamp in UNIX time as the id
	# Not good for concurrent users
	p = (time.mktime(datetime.datetime.now().timetuple()), x, y, )
	try:
		c = db.execute('INSERT INTO `points` (id, x, y) VALUES (?,?,?)', p)
		db.commit()
	except sqlite.sqlite3.Error as er: #Handle insert errors
		error = er.args[0]
		return bottle.Response({ 'err': error }, 400)
	else:
		row_id = c.lastrowid
		return { 'id': row_id }


root.run(host='0.0.0.0', port=8000, reloader=True)