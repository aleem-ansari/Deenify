import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



def lookup_prayer(city):

    city = city.upper()

    import http.client

    conn = http.client.HTTPSConnection("muslimsalat.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "8742c3d2c2msh16a611bf7b7bed6p1b5ca2jsn444a58e38029",
        'X-RapidAPI-Host': "muslimsalat.p.rapidapi.com"
    }

    try:
        conn.request("GET", "/(city).json", headers=headers)

        res = conn.getresponse()
        data = res.read()

        return(data.decode("utf-8"))

    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None