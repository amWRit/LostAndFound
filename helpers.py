import os
import requests
import urllib.parse
from cs50 import SQL

from flask import redirect, render_template, request, session
from functools import wraps

#db = SQL("sqlite:///lostandfound.db", connect_args={'check_same_thread': False})
db = SQL("sqlite:///lostandfound.db")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

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

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def check_username_exists(name):
    # Query database for username
    # db = SQL("sqlite:///finance.db")
    rows = db.execute("SELECT * FROM users WHERE username = :username", username = name)

    # Ensure username exists and password is correct
    if len(rows) == 1:
        return True
    else:
        return False

def register_user(name, pwd_hash, email, phone):


    # insert user name and password hash into db
    rows = db.execute("INSERT INTO users (username, hash, email, phone) VALUES (:username, :hash, :email, :phone)", username = name, hash = pwd_hash, email = email, phone = phone)

    if rows == None:
        return False
    else:
        return True


# https://note.nkmk.me/en/python-check-int-float/
# https://stackoverflow.com/questions/26198131/check-if-input-is-positive-integer

def is_positive_integer(n):
    try:
        val = int(n)
        if val < 0:
            return False
    except ValueError:
        return False
    else:
        return True

# Reference: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def build_index_data(rows):
    data = []

    for row in rows:
        hash = {}
        hash["post_id"] = row["post_id"]
        hash["type"] = row["type"].upper()
        hash["category"] = row["category"].upper()
        hash["title"] = row["title"].title()
        hash["desc"] = row["desc"]
        hash["image_id"] = row["image_id"]
        hash["location"] = row["location"]
        hash["date"] = row["date"]
        hash["status"] = row["status"].title()
        hash["claimed_by"] = row["claimed_by"] # id of claimer

        # information of the user that made the post

        hash["user_id"] = int(row["id"]) # id of poster
        hash["username"] = row["username"]
        hash["email"] = row["email"]
        hash["phone"] = row["phone"]

        if hash["claimed_by"] != None:
            conn = db.execute("SELECT username from users where id = :claimer_id", claimer_id = hash["claimed_by"])
            hash["claimer_name"] = conn[0]["username"]

        data.append(hash)

    return data
