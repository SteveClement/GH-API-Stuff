#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# all the imports
import os
import json
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import urllib.request

import flask_github

from time import time, sleep

import requests

import hashlib

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config['GITHUB_CLIENT_ID'] = 'XXX'
app.config['GITHUB_CLIENT_SECRET'] = 'YYY'

github = GitHub(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'emoji.db'),
    SECRET_KEY='d3v3l0pm3nt k3y',
    USERNAME='admin',
    PASSWORD='a55w0rd',
    APIURL='https://api.github.com/emojis'
))
app.config.from_envvar('EMOJI_SETTINGS', silent=True)

def checkEmoji(name, dataHash):
    db =  get_db()
    query = 'SELECT hash FROM entries WHERE name={} ORDER BY lastCrawl'.format(name)
    print(query)
    hashes = db.execute('SELECT hash FROM entries WHERE name=\"{}\" ORDER BY lastCrawl'.format(name))
    hasHash = hashes.fetchone()
    print(hasHash)
    sleep(9)
    if hasHash:
        print("{} has a hash: {}".format(name, hasHash[0]))
        if dataHash == hasHash[0]:
            print("Already in db, skipping: {}".format(name))
            return False
        else:
            return True
    else:
        return False

def update_db():
    with app.app_context():
        try:
            print("trying")
            r = requests.get(app.config['APIURL'])
            response = urllib.request.urlopen(app.config['APIURL'])
        except requests.exceptions.RequestException as e:
            print("I am error, Probably no netz: {}".format(e))
            return False
        data = response.read()
        dataHash = hashlib.sha256(data).hexdigest()
        text = data.decode('utf-8')
        json_acceptable_string = text.replace("'", "\"")
        emoList = json.loads(json_acceptable_string)
        now = time()
        db = get_db()
        counter = 0
        total = len(dict.keys(emoList))
        for name in dict.keys(emoList):
            imgURL = emoList[name]
            counter += 1
            print("Processing: {} - {} of {}".format(name, counter, total))
            response = urllib.request.urlopen(imgURL)
            data = response.read()
            dataHash = hashlib.sha256(data).hexdigest()
            if not checkEmoji(name, dataHash):
                print("Adding {} to db".format(name))
                db.execute('INSERT INTO entries (name, lastCrawl, imgURL, hash) VALUES (?, ?, ?, ?)',
                             [name, now, imgURL, dataHash])
                db.commit()
        return True

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def check_db():
    with app.app_context():
        db = get_db()
        try:
            cur = db.execute('SELECT * FROM entries LIMIT 1')
            if cur.fetchone():
                print("Got an entry, thus not empty")
                return True
        except:
            print("Probably empty, initdb")
            return False

def init_db():
    """Initializes the database."""
    with app.app_context():
        if not check_db():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
        else:
            print("Skipping initdb")

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT name, imgURL, hash FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    init_db()
    if update_db():
        print("Update suceeded, launching service")
        app.run(debug=True)
    else:
        print("Update failed, launching service")
        app.run(debug=True)
