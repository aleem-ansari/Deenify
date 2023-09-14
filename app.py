import os
import datetime
import requests
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup_prayer

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    id = session["user_id"]
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was re-entered
        elif not request.form.get("password"):
            return apology("must re-enter password", 400)

        # Ensure password and confirm password are same
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) != 0:
            return apology("username already exists", 400)

        #Hash the password
        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        #Add username and password to the database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/prayertimes")
@login_required
def prayertimes():

    id = session["user_id"]
    city1 = db.execute("SELECT city FROM users WHERE id = ?", id)
    country1 = db.execute("SELECT country FROM users WHERE id = ?", id)
    method1 = db.execute("SELECT method FROM users WHERE id = ?", id)

    city = city1[0]['city']
    country = country1[0]['country']
    method = method1[0]['method']

    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}"

    response = requests.get(url)

    data = (response.json())

    # Extract prayer times
    prayer_times = data['data']['timings']
    print(prayer_times)


    return render_template("prayertimes.html", prayer_times = prayer_times)




@app.route("/date", methods=["GET", "POST"])
@login_required
def date():

    if request.method == 'GET':
        date = datetime.date.today()

        # Convert the date object to a string in the format 'DD-MM-YYYY'
        date_str = date.strftime('%d-%m-%Y')
        print(date_str)

        url = f"http://api.aladhan.com/v1/gToH/{date_str}"
        response = requests.get(url)

        data = (response.json())
        print(data)

        to_day = data['data']['hijri']['day']
        to_month = data['data']['hijri']['month']['en']
        to_year = data['data']['hijri']['year']

        from_day = data['data']['gregorian']['day']
        from_month = data['data']['gregorian']['month']['en']
        from_year = data['data']['gregorian']['year']

        return render_template("date.html", to_day = to_day, to_month = to_month, to_year = to_year, from_day = from_day, from_month = from_month, from_year = from_year)

    else:

        # Get the date from the web form
        date_str = request.form.get("date")

        # Convert the date string to a datetime object
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        # Format the date as 'DD-MM-YYYY'
        formatted_date = date.strftime('%d-%m-%Y')
        print(formatted_date)

        url = f"http://api.aladhan.com/v1/gToH/{formatted_date}"
        response = requests.get(url)

        data = (response.json())
        print(data)

        to_day = data['data']['hijri']['day']
        to_month = data['data']['hijri']['month']['en']
        to_year = data['data']['hijri']['year']

        from_day = data['data']['gregorian']['day']
        from_month = data['data']['gregorian']['month']['en']
        from_year = data['data']['gregorian']['year']

        return render_template("date.html", to_day = to_day, to_month = to_month, to_year = to_year, from_day = from_day, from_month = from_month, from_year = from_year)




@app.route("/settings", methods = ['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':

        id = session["user_id"]
        city = request.form.get('city')
        country = request.form.get('country')
        method = request.form.get('method')

        if not request.form.get("city"):
            return apology("must provide city name", 400)

        if not request.form.get("country"):
            return apology("must provide country name", 400)

        if not request.form.get("method"):
            return apology("must provide method", 400)

        #Add username and password to the database
        db.execute("UPDATE users SET city = ?, country = ?, method = ? WHERE id = ?", city.lower(), country.lower(), method, id)


        # Redirect user to home page
        return render_template("settings1.html")


    else:
        return render_template("settings.html")



@app.route("/asma")
@login_required
def asma():
    number = random.randint(1, 99)

    url = f"http://api.aladhan.com/v1/asmaAlHusna/{number}"

    response = requests.get(url)

    data = (response.json())

    name = data['data'][0]['name']
    transliteration = data['data'][0]['transliteration']
    number = data['data'][0]['number']
    meaning = data['data'][0]['en']['meaning']


    return render_template("asma.html", name = name, transliteration = transliteration, number = number, meaning = meaning)


@app.route("/ayah", methods=['GET', 'POST'])
@login_required
def ayah():
    if request.method == 'POST':

        keyword = request.form.get('keyword')
        surah = request.form.get('surah')

        if not request.form.get('surah'):
            surah = 'all'
        edition = 'en.mubarakpuri'

        try:
            # Make the API call
            url = f'http://api.alquran.cloud/v1/search/{keyword}/{surah}/{edition}'

            response = requests.get(url)


            # Check if the response status code is successful (e.g., 200)
            if response.status_code == 200:
                # If the response is successful, parse the data or do whatever you need to do
                data = (response.json())
                # Process the data here
                ayah_number = data['data']['matches'][0]['number']
                surah_number = data['data']['matches'][0]['surah']['number']
                text = data['data']['matches'][0]['text']

            else:
                # If the response status code is not successful, handle the error
                print(f"API request failed with status code: {response.status_code}")

        except requests.exceptions.RequestException:
            return apology("An error has occured")

        except ValueError:
            return apology("An error has occured")

        except UnboundLocalError:
            return apology("An error has occured")

        except Exception:
            return apology("An error has occured")


        return render_template('ayah.html', ayah_number = ayah_number, surah_number = surah_number, text = text)

    else:

        keyword = 'most'
        surah = 1
        edition = 'en.mubarakpuri'

        url = f'http://api.alquran.cloud/v1/search/{keyword}/{surah}/{edition}'

        response = requests.get(url)

        data = (response.json())

        ayah_number = data['data']['matches'][0]['number']
        surah_number = data['data']['matches'][0]['surah']['number']
        text = data['data']['matches'][0]['text']

        return render_template('ayah.html', ayah_number = ayah_number, surah_number = surah_number, text = text)


@app.route("/quran", methods = ["GET", "POST"])
@login_required
def quran():

    if request.method == "POST":

        edition = 'quran-uthmani'
        page = request.form.get('page')

        if not request.form.get("page"):
            return apology("must provide a page number", 400)

        if int(page) < 1 or int(page) > 604:
            return apology("enter a valid page no.")

        url = f'http://api.alquran.cloud/v1/page/{page}/{edition}'

        response = requests.get(url)

        data = (response.json())

        ayahs = [ayah['text'] for ayah in data['data']['ayahs']]

        complete_arabic = '<br><br>'.join(ayahs)

        return render_template('quran.html', complete_arabic = complete_arabic)

    else:

        return render_template("quran.html")

