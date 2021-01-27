import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required, lookup, usd, check_username_exists, register_user, is_positive_integer, allowed_file, build_index_data

import urllib.request

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROOF_FOLDER'] = 'static/proofs'

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///lostandfound.db", connect_args={'check_same_thread': False})
db = SQL("sqlite:///lostandfound.db")

# item categories
CATEGORIES = ["Pets", "Documents", "Phone", "Cash", "Debit/Credit Card", "Laptop", "Clothes", "Jewellery", "Purse", "Person", "Motorcycle", "Cycle", "Cars", "Others"]

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    # Query database
    rows = db.execute("SELECT * from posts join users on posts.posted_by = users.id WHERE posts.status <> 'deleted' ORDER BY date DESC")

    data = build_index_data(rows)
    return render_template("index.html", data = data, filter = {})


@app.route("/filter", methods=["POST"])
@login_required
def filter():
    category = request.form.get("category")
    type = request.form.get("type")
    filter = {}
    print(type)
    print(category)

    if request.form.get("category") and request.form.get("type"):
        rows = db.execute("SELECT * from posts join users on posts.posted_by = users.id WHERE posts.status <> 'deleted' \
        and category = :category and type = :type ORDER BY date DESC", category = category, type = type)
        filter["category"] = category
        filter["type"] = type
        flash("Loading " + type.upper() + " " + category.upper() + " items...")

    elif request.form.get("category"):
        rows = db.execute("SELECT * from posts join users on posts.posted_by = users.id WHERE posts.status <> 'deleted' \
        and category = :category ORDER BY date DESC", category = category)
        filter["category"] = category
        flash("Loading " + category.upper() + " items...")

    elif request.form.get("type"):
        rows = db.execute("SELECT * from posts join users on posts.posted_by = users.id WHERE posts.status <> 'deleted' \
        and type = :type ORDER BY date DESC", type = type)
        filter["type"] = type
        flash("Loading " + type.upper() + " items...")


    data = []
    data = build_index_data(rows)

    return render_template("index.html", data = data, filter = filter)


@app.route("/search", methods=["POST"])
@login_required
def search():
    search = "%{}%".format(request.form.get("search"))
    filter = {}
    filter["search"] = request.form.get("search")
    rows = db.execute("SELECT * from posts join users on posts.posted_by = users.id WHERE posts.status <> 'deleted' \
    and title LIKE :search ORDER BY date DESC", search = search)

    data = build_index_data(rows)
    flash("Searching " + request.form.get("search") + "...")
    return render_template("index.html", data = data, filter = filter)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('Must provide username.')
            return render_template("login.html")
            # return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Must provide password.')
            return render_template("login.html")
            # return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash('Invalid username and/or password.')
            return render_template("login.html")
            #return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["categories"] = sorted(CATEGORIES)

        flash('Logged in successfully.')

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
    flash('Logged out successfully.')
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # register
        username = request.form.get("username")
        pwd1 = request.form.get("password1")
        pwd2 = request.form.get("password2")
        email = request.form.get("email")
        phone = request.form.get("phone")

        # Ensure username was submitted
        if not username:
            flash('Must provide username.')
            return render_template("register.html")
            # return apology("must provide username", 403)

        # Ensure password was submitted
        elif not pwd1 or not pwd2:
            flash('Must provide password.')
            return render_template("register.html")
            # return apology("must provide password", 403)

        # Ensure two passwords match
        elif pwd1 != pwd2:
            flash('Passwords do not match.')
            return render_template("register.html")
            # return apology("Passwords do not match", 403)

        elif not is_positive_integer(phone) and len(phone) != 15:
            flash('Incorrect phone format.')
            return render_template("register.html")
            # return apology("Incorrect phone format", 403)

        elif check_username_exists(username):
            # check if username exists
            flash('Username already exists.')
            return render_template("register.html")
            # return apology("Username already exists.", 403)
        else:
            pwd_hash = generate_password_hash(pwd1, method='pbkdf2:sha256', salt_length=8)

            if register_user(username, pwd_hash, email, phone):
                flash('Registerd successfully. You can now log in.')
                return render_template("login.html")
            else:
                flash('Could not register. Please try again.')
                return render_template("register.html")
                # return apology("Could not register.", 403)

    else:
        return render_template("register.html")


@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == "POST":
        type = request.form.get("type")
        category = request.form.get("category")
        title = request.form.get("title")
        desc = request.form.get("desc")
        location = request.form.get("location")
        date = request.form.get("date")
        #phone = request.form.get("phone")
        posted_by = session["user_id"]

        rows = db.execute("SELECT image_id FROM posts ORDER BY image_id DESC")
        if len(rows) == 0:
            image_id = 1
        else:
            image_id = int(rows[0]["image_id"]) + 1

        if upload_image(request, image_id, 'UPLOAD_FOLDER'):
            rows = db.execute("INSERT INTO posts (type, category, title, desc, location, date, posted_by, image_id) \
                    VALUES (:type, :category, :title, :desc, :location, :date, :posted_by, :image_id)", \
                    type = type, category = category, title = title, desc = desc, location = location, date = date, posted_by = posted_by, image_id = image_id)
            flash(" Succefully posted.")
            return index()
        else:
            return apology("Problem uploading image.", 403)

    else:
        return render_template("post.html", categories = sorted(CATEGORIES))

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/disclaimer", methods=["GET"])
def disclaimer():
    return render_template("disclaimer.html")

@app.route("/claim", methods=["GET", "POST"])
@login_required
def claim():
    if request.method == "POST":
        post_id = 0
        if request.form.get("claim-btn"):
            post_id = request.form.get("claim-btn")
        else:
            post_id = request.form.get("mark-btn")
        print(post_id)
        rows = db.execute("SELECT * from posts join users on posts.posted_by = users.id WHERE posts.post_id = :post_id and posts.status <> 'deleted' ", post_id = post_id)
        if len(rows) > 0:
            row = rows[0]

            data = []

            hash = {}
            hash["post_id"] = row["post_id"]
            hash["type"] = row["type"].upper()
            hash["category"] = row["category"].title()
            hash["title"] = row["title"]
            hash["desc"] = row["desc"]
            hash["image_id"] = row["image_id"]
            hash["location"] = row["location"]
            hash["date"] = row["date"]
            hash["status"] = row["status"].title()
            hash["claimed_by"] = row["claimed_by"]

            hash["user_id"] = row["id"]
            hash["username"] = row["username"]
            hash["email"] = row["email"]
            hash["phone"] = row["phone"]

            # data.append(hash)

            if hash["claimed_by"] != None:
                conn = db.execute("SELECT username from users where id = :claimer_id", claimer_id = hash["claimed_by"])
                hash["claimer_name"] = conn[0]["username"]

            if request.form.get("claim-btn"):
                return render_template("claim.html", item = hash, post_id = post_id)
            else:
                return render_template("mark_claimed.html", item = hash, post_id = post_id)


        else:
            return apology("Something went wrong.", 404)

    else:
        return apology("Page not found.", 404)

@app.route("/message", methods=["GET", "POST"])
@login_required
def message():
    if request.method == "POST":
        type = request.form.get("type")

        if type == "claim":
            post_id = request.form.get("claim-btn")
            sender_id = session["user_id"]
            message = request.form.get("message")

            rows = db.execute("SELECT posted_by from posts WHERE post_id = :post_id and posts.status <> 'deleted' ", post_id = post_id)
            receiver_id = rows[0]["posted_by"]

            rows = db.execute("SELECT proof_image_id FROM messages ORDER BY proof_image_id DESC")
            if len(rows) == 0:
                image_id = 1
            else:
                image_id = int(rows[0]["proof_image_id"]) + 1

            if upload_image(request, image_id, 'PROOF_FOLDER'):
                rows = db.execute("INSERT INTO messages (type, post_id, sender_id, receiver_id, message, proof_image_id) \
                        VALUES (:type, :post_id, :sender_id, :receiver_id, :message, :proof_image_id)", \
                        type = type, post_id = post_id, sender_id = sender_id, receiver_id = receiver_id, message = message, proof_image_id = image_id)

                # update status and claimed_by in posts
                db.execute("UPDATE posts SET status = :status, claimed_by = :sender_id where post_id = :post_id", post_id = post_id, sender_id = sender_id, status = "claim in progress")

                flash("Claim request sent successfully.")
                #return render_template("index.html", item = hash, post_id = post_id)
                return index()

            else:
                return apology("Problem uploading image.", 403)


        else:
            # type = chat
            sender_id = session["user_id"]
            receiver_id = request.form.get("receiver_id")
            post_id = request.form.get("post_id")
            message = request.form.get("message")
            type = "chat"

            rows = db.execute("INSERT INTO messages (type, post_id, sender_id, receiver_id, message) \
                    VALUES (:type, :post_id, :sender_id, :receiver_id, :message)", \
                    type = type, post_id = post_id, sender_id = sender_id, receiver_id = receiver_id, message = message)

            flash("Message sent successfully.")
            #return render_template("index.html", item = hash, post_id = post_id)
            return messages()
    else:
        return apology("Page not found.", 404)

@app.route("/history")
@login_required
def history():
    # Query database
    rows = db.execute("SELECT * FROM (SELECT * from posts join users on posts.posted_by = users.id ORDER BY date DESC) WHERE id = :user_id", user_id = session["user_id"])

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

        hash["user_id"] = int(row["id"]) # id of poster/ current user
        hash["username"] = row["username"]
        hash["email"] = row["email"]
        hash["phone"] = row["phone"]

        if hash["claimed_by"] != None:
            conn = db.execute("SELECT username from users where id = :claimer_id", claimer_id = hash["claimed_by"])
            hash["claimer_name"] = conn[0]["username"]

        data.append(hash)

    rows = db.execute("SELECT * FROM (SELECT * from posts join users on posts.claimed_by = users.id  WHERE posts.status <> 'deleted' ORDER BY date DESC) WHERE id = :user_id", user_id = session["user_id"])

    claim_data = []

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
        hash["posted_by"] = row["posted_by"] # id of poster

        # information of the user that made the post

        hash["user_id"] = int(row["id"]) # id of poster
        hash["username"] = row["username"]
        hash["email"] = row["email"]
        hash["phone"] = row["phone"]

        if hash["posted_by"] != None:
            conn = db.execute("SELECT username from users where id = :poster_id", poster_id = hash["posted_by"])
            hash["poster_name"] = conn[0]["username"]

        claim_data.append(hash)

    return render_template("history.html", data = data, claim_data = claim_data)


@app.route("/mark_claimed", methods=["GET", "POST"])
@login_required
def mark_claim():
    if request.method == "POST":
        post_id = 0
        if request.form.get("claim-btn"):
            post_id = request.form.get("claim-btn")
        else:
            post_id = request.form.get("mark-btn")

        # update status as claimed
        db.execute("UPDATE posts SET status = :status WHERE post_id = :post_id", post_id = post_id, status = "claimed")

        flash("Item marked as CLAIMED successfully.")
        return index()

    else:
        return apology("Page not found.", 404)

@app.route("/messages", methods=["GET"])
@login_required
def messages():
    # Query database
    rows = db.execute("SELECT * FROM (SELECT * from messages  WHERE sender_id = :user_id OR receiver_id = :user_id ORDER BY post_id DESC) ORDER BY date DESC", user_id = session["user_id"])

    data = []

    for row in rows:
        if row["status"] != "deleted":
            hash = {}
            hash["message_id"] = row["message_id"]
            hash["sender_id"] = row["sender_id"]
            hash["receiver_id"] = row["receiver_id"]
            hash["message"] = row["message"]
            hash["post_id"] = row["post_id"]
            hash["proof_image_id"] = row["proof_image_id"]
            hash["type"] = row["type"]
            hash["date"] = row["date"]

            conn = db.execute("SELECT username from users where id = :sender_id", sender_id = hash["sender_id"])
            hash["sender_name"] = conn[0]["username"]

            conn = db.execute("SELECT username from users where id = :receiver_id", receiver_id = hash["receiver_id"])
            hash["receiver_name"] = conn[0]["username"]

            conn = db.execute("SELECT title, type, status from posts where post_id = :post_id and posts.status <> 'deleted' ", post_id = hash["post_id"])
            hash["post_title"] = conn[0]["title"].title()
            hash["post_type"] = conn[0]["type"].upper()
            hash["post_status"] = conn[0]["status"].upper()

            data.append(hash)

    return render_template("messages.html", data = data)


@app.route("/message_form", methods=["GET", "POST"])
@login_required
def message_form():
    if request.method == "POST":
        receiver_id = request.form.get("receiver-id")
        post_id = request.form.get("post_id")

        # Query database
        hash = {}

        conn = db.execute("SELECT username from users where id = :sender_id", sender_id = session["user_id"])
        hash["sender_name"] = conn[0]["username"]

        conn = db.execute("SELECT username from users where id = :receiver_id", receiver_id = receiver_id)
        hash["receiver_name"] = conn[0]["username"]
        hash["receiver_id"] = receiver_id

        conn = db.execute("SELECT * from posts where post_id = :post_id and posts.status <> 'deleted' ", post_id = post_id)
        hash["post_title"] = conn[0]["title"].title()
        hash["post_type"] = conn[0]["type"].upper()
        hash["post_status"] = conn[0]["status"].upper()
        hash["date"] = conn[0]["date"]
        hash["post_id"] = post_id

        hash["message_type"] = "chat"


        return render_template("message_form.html", item = hash)

    else:
        return apology("Page not found.", 404)


@app.route("/delete_post", methods=["POST"])
@login_required
def delete_post():
    post_id = request.form.get("delete-btn")
    print(post_id)

    db.execute("UPDATE posts SET status = :status WHERE post_id = :post_id", post_id = post_id, status = "deleted")
    db.execute("UPDATE messages SET status = :status WHERE post_id = :post_id", post_id = post_id, status = "deleted")

    flash("Post deleted successfully.")
    return history()

@app.route("/deny_claim", methods=["POST"])
@login_required
def deny_claim():
    post_id = request.form.get("deny-btn")
    print(post_id)

    db.execute("UPDATE posts SET status = :status, claimed_by = NULL WHERE post_id = :post_id", post_id = post_id, status = "unclaimed")
    db.execute("UPDATE messages SET status = :status WHERE post_id = :post_id", post_id = post_id, status = "deleted")

    flash("Claim cancelled successfully.")
    return history()

@app.route("/post_detail", methods=["POST"])
@login_required
def post_detail():
    if request.method == "POST":
        post_id = request.form.get("post_id")
        rows = db.execute("SELECT * from posts join users on posts.posted_by = users.id WHERE posts.post_id = :post_id and posts.status <> 'deleted' ", post_id = post_id)
        if len(rows) > 0:
            row = rows[0]

            hash = {}
            hash["post_id"] = row["post_id"]
            hash["type"] = row["type"].upper()
            hash["category"] = row["category"].title()
            hash["title"] = row["title"]
            hash["desc"] = row["desc"]
            hash["image_id"] = row["image_id"]
            hash["location"] = row["location"]
            hash["date"] = row["date"]
            hash["status"] = row["status"].title()
            hash["claimed_by"] = row["claimed_by"]

            hash["user_id"] = row["id"]
            hash["username"] = row["username"]
            hash["email"] = row["email"]
            hash["phone"] = row["phone"]

            if hash["claimed_by"] != None:
                conn = db.execute("SELECT username from users where id = :claimer_id", claimer_id = hash["claimed_by"])
                hash["claimer_name"] = conn[0]["username"]

            return render_template("post_details.html", item = hash, post_id = post_id)


        else:
            return apology("Something went wrong.", 404)

    else:
        return apology("Page not found.", 404)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# Reference: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/

def upload_image(request, image_id, type):
	if 'file' not in request.files:
		flash('No file part')
		# return redirect(request.url)
		return False
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		# return redirect(request.url)
		return False
	if file and allowed_file(file.filename):
		filename = secure_filename(str(image_id) + '.jpg')
		file.save(os.path.join(app.config[type], filename))
		#file.save(filename)
		#print('upload_image filename: ' + filename)
		#flash('Image successfully uploaded.')
		# return render_template('index.html')
		return True
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return False
		# return redirect(request.url)