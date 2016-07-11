import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_github import GitHub

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
