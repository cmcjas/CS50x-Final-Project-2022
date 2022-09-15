import os
import re
import requests
import json

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, abort,\
    send_from_directory
from datetime import datetime
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from pathlib import Path
from helpers import apology, login_required, recipe_db, recipe_list, YT_helper, get_api_key, get_weather_results, weather_part_db

# Configure application
app = Flask(__name__)

app.config['UPLOAD_PATH1'] = ""
app.config['UPLOAD_PATH2'] = ""

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///food.db")


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
    profile = db.execute("SELECT * FROM recipe WHERE user_id = ?", session['user_id'])
    Allprofile = db.execute("SELECT * FROM recipe ")
    num = session["user_id"]
    pnamebar = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    key = db.execute("SELECT key FROM likeHISTORY WHERE user_id = ?", session['user_id'])
    # pass like preferences extracted from database into an array, so the array then can be jsonfied and pass onto the html file
    key_list = []
    for i in range(len(key)):
        key_list.insert(i, key[i]['KEY'])
       
    try:
        bf = db.execute("SELECT breakfast FROM planner WHERE user_id = ?", session['user_id'])
        lu = db.execute("SELECT lunch FROM planner WHERE user_id = ?", session['user_id'])
        din = db.execute("SELECT dinner FROM planner WHERE user_id = ?", session['user_id'])
        shop = db.execute("SELECT shopping FROM planner WHERE user_id = ?", session['user_id'])

        user_data = db.execute("SELECT * FROM weather where user_id = ?", session['user_id'])
        # access openweathermap api to extract returned weather info
        weather_data = get_weather_results(user_data[0]['local'], user_data[0]['count'], get_api_key())
        # extract individual element of the return weather info
        temp1 = "{0:.1f}".format(weather_data["main"]["temp"])
        temp2 = "{0:.1f}".format(weather_data["main"]["feels_like"])
        weather = weather_data["weather"][0]["main"]
        unix = int(weather_data["dt"])
        zone = int(weather_data["timezone"])
        local = unix + zone
        time = datetime.utcfromtimestamp(local).strftime('%Y-%m-%d %H:%M')
        t1 = datetime.utcfromtimestamp(local).strftime('%H').lstrip("0").replace(" 0", " ")

        return render_template('index.html', temp1=temp1, temp2=temp2, weather=weather, location=user_data[0]['local'], country=user_data[0]['count'], time=time, 
        t1=t1, num=num, profile=profile, bf=bf, lu=lu, din=din, shop=shop, pname=pnamebar, all=Allprofile, key=json.dumps(key_list))
    except:
         # access planner info from sql DB initally, if failed due to DB being emptied in the first place, then create an empty entry in the DB for the user
        for i in range(7):
            db.execute("INSERT INTO planner (user_id, day, breakfast, lunch, dinner, shopping) VALUES(?, ?, ?, ?, ?, ?)", session['user_id'], i+1, 
            " ", " ", " ", " ")
        bf = db.execute("SELECT breakfast FROM planner WHERE user_id = ?", session['user_id'])
        lu = db.execute("SELECT lunch FROM planner WHERE user_id = ?", session['user_id'])
        din = db.execute("SELECT dinner FROM planner WHERE user_id = ?", session['user_id'])
        shop = db.execute("SELECT shopping FROM planner WHERE user_id = ?", session['user_id'])
        return render_template("index.html", num=num, profile=profile, bf=bf, lu=lu, din=din, shop=shop, all=Allprofile, pname=pnamebar, key=json.dumps(key_list))


@app.route("/weather", methods=["POST"])
@login_required
def weather():
    loc = request.form.get('loc')
    count = request.form.get('count')
    # if api failed to find location via user's input then return error
    try:
        weather = get_weather_results(loc, count, get_api_key())
        weather_part_db(weather, loc, count, session['user_id'])
        return redirect('/')
    except:
        return apology("Location not exist! OR Invalid location/country name.", 400)


@app.route("/planner", methods=["POST"])
@login_required
def planner():
    bf = request.form.getlist('bf[]')
    lu = request.form.getlist('lu[]')
    din = request.form.getlist('din[]')
    shop = request.form.getlist('shop[]')

    for i in range(7):
        db.execute("UPDATE planner SET breakfast = ?, lunch = ?, dinner = ?, shopping = ? WHERE user_id = ? AND day = ?", bf[i], lu[i], din[i], 
        shop[i], session['user_id'], i+1)
    return redirect ("/")


@app.route("/msg", methods=["POST"])
def msg():
    name1 = db.execute("SELECT pname FROM users WHERE id = ?", session['user_id'])
    name2 = request.form.get('receiver')
    msg = request.form.get('msg')
    msgg = request.form.get('msgg')

    try:
        db.execute("UPDATE inbox SET msg2 = ? WHERE name1 = ? AND name2 = ? AND msg1 = ?", msg, name2, name1[0]['pname'], msgg)
        db.execute("UPDATE inboxtemp SET msg2 = ? WHERE name1 = ? AND name2 = ? AND msg1 = ?", msg, name2, name1[0]['pname'], msgg)
        db.execute("INSERT INTO inbox (name1, name2, msg1) VALUES(?, ?, ?)", name1[0]['pname'], name2, msg)
        db.execute("INSERT INTO inboxtemp (name1, name2, msg1) VALUES(?, ?, ?)", name1[0]['pname'], name2, msg)
    except:
        db.execute("INSERT INTO inbox (name1, name2, msg1) VALUES(?, ?, ?)", name1[0]['pname'], name2, msg)
        db.execute("INSERT INTO inboxtemp (name1, name2, msg1) VALUES(?, ?, ?)", name1[0]['pname'], name2, msg)

    return redirect(url_for('inbox'))

# remove send messages history from user
@app.route("/msgrm1", methods=["POST"])
def msgrm1():
    rmsg = request.form.get('rmsg')
    rename = request.form.get('rename')
    db.execute("DELETE FROM inbox WHERE name1 = ? AND msg1 = ?", rename, rmsg)
    return redirect(url_for('inbox'))

# remove receive messages history from user
@app.route("/msgrm2", methods=["POST"])
def msgrm2():
    rmsg = request.form.get('rmsg')
    rename = request.form.get('rename')
    db.execute("DELETE FROM inboxtemp WHERE name2 = ? AND msg1 = ?", rename, rmsg)
    return redirect(url_for('inbox'))

# update like counts for receipes
@app.route("/like", methods=["POST"])
def like():
    recipe_name = request.form['data']
    author = request.form['data2']
    key = request.form['key']
    count = db.execute("SELECT likes FROM recipe WHERE title = ? AND author = ?", recipe_name, author)
    new_count = count[0]['likes'] + 1
    db.execute("UPDATE recipe SET likes = ? WHERE title = ? AND author = ?", new_count, recipe_name, author)
    db.execute("INSERT INTO likeHistory (user_id, key) VALUES(?, ?)", session['user_id'], key)
    return


@app.route("/delike", methods=["POST"])
def delike():
    recipe_name = request.form['data']
    author = request.form['data2']
    count = db.execute("SELECT likes FROM recipe WHERE title = ? AND author = ?", recipe_name, author)
    new_count = count[0]['likes'] - 1
    key = request.form['key']
    db.execute("UPDATE recipe SET likes = ? WHERE title = ? AND author = ?", new_count, recipe_name, author)
    db.execute("DELETE FROM likeHistory WHERE user_id = ? AND key = ?", session['user_id'], key)
    return


@app.route("/inbox")
def inbox():
    pnamebar = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    name = db.execute("SELECT pname FROM users WHERE id = ?", session['user_id'])
    allname= db.execute("SELECT pname FROM users")
    inbox_data2 = db.execute("SELECT * FROM inbox WHERE name2 = ?", name[0]['pname'])
    inbox_data = db.execute("SELECT * FROM inboxtemp WHERE name1 = ?", name[0]['pname'])
    return render_template("inbox.html", inbox=inbox_data2, inbox2=inbox_data, pname=pnamebar, aname=allname)
        

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and OR or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # create unique upload folders directory for each login user
        name = str(session["user_id"])
        name1 = 'music_' + name
        name2 = 'image_' + name

        session['path1'] = 'static/upload_data/music_' + name
        session['path2'] = 'static/upload_data/image_' + name

        # update upload paths
        app.config['UPLOAD_PATH1'] = session['path1']
        app.config['UPLOAD_PATH2'] = session['path2']

        # make folder for our upload paths
        try:
            os.makedirs(os.path.join("static/upload_data", name1))
            os.makedirs(os.path.join("static/upload_data", name2))
        except:
            return redirect("/")

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

    # prompt user input for their login username, profile name for sharing purpose, password and confirmation password
    name = request.form.get("username")
    pname = request.form.get("pname")
    pass1 = request.form.get("password")
    pass2 = request.form.get("confirmation")

    # if user submit the following happens
    if request.method == "POST":

        # generate a hash for user input password, so later on we can store hash instead of raw data into our database which is more secure
        hash = generate_password_hash(pass1)

        # return error for empty password input fields
        if not name or not pass1 or not pass2:
            return apology("Input must not be emptied", 400)
        # profile name must not be the same as login username for security reasons, so when other users send you a message or search for recipe, they only see your profile name.
        if name == pname:
            return apology("profile name has to be different to your username.", 400)

        # to ensure that a user's created password is 8 letters long that contains numbers, at lease one capital & lowercase letter
        if len(pass1) < 8:
            return apology("Must be at lease 8 letters long", 400)
        elif re.search('[0-9]', pass1) is None:
            return apology("Must contatin at least a number", 400)
        elif re.search('[A-Z]', pass1) is None:
            return apology("Must contatin at least a capital letter", 400)
        elif re.search('[a-z]', pass1) is None:
            return apology("Must contatin at least a lowercase letter", 400)

        # return error if the input confirmation passord does not match the password
        if pass1 != pass2:
            return apology("Confirmation password not matched", 400)

        # if all conditions met, create a new row for a newly registered user in our database
        # username and profile name are unique, therefore, if user enters a name that already exits inside our database, error returns
        try:
            db.execute("INSERT INTO users (username, pname, hash) VALUES(?, ?, ?)", name, pname, hash)
            return redirect("/")
        except:
            return apology("Username or profile name already exists", 400)

    else:
        return render_template("register.html")


@app.route('/player', methods=["GET", "POST"])
@login_required
def music():
    music = db.execute("SELECT * FROM music WHERE user_id = ?", session["user_id"])
    num = session["user_id"]

    if request.method == "POST":
        title = request.form.get("name")
        session["recipe"] = title
        # this is the userid for the account that our user searches for via the sharing feature
        uid = request.form.get("uid")
        session["uid"] = uid
        data = db.execute("SELECT id FROM recipe WHERE title = ? AND user_id = ?", title, uid)
        id = data[0]['id']
        return recipe_db(music, num, uid, id, uid)
    else:
        data = db.execute("SELECT id FROM recipe WHERE title = ? AND user_id = ?", session["recipe"], session["uid"])
        id = data[0]['id']
        return recipe_db(music, num, session["uid"], id, session["uid"])

# function for processing upload mp3 files from users, and insert its relevant info into sql DB
@app.route('/mp3', methods=['POST'])
@login_required
def upload_files1():
    uploaded_file = request.files.getlist('file[]')
    for i in range(len(uploaded_file)):
        filename = secure_filename(uploaded_file[i].filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            file_name = os.path.splitext(filename)[0]
            uploaded_file[i].save(os.path.join(app.config['UPLOAD_PATH1'], filename))
            db.execute("INSERT INTO music (name, user_id) VALUES(?, ?)", file_name, session["user_id"]);
    return redirect(url_for('music'))
    
# delete audio files
@app.route("/delete1", methods=["POST"])
@login_required
def delete1():
    # get abs url for the mp3 file from html input value
    data1 = request.form['data1']
    data2 = request.form['data2']
    os.remove(data2)
    db.execute("DELETE FROM music WHERE name = ? AND user_id = ?", data1, session["user_id"])
    db.execute("INSERT INTO temp (id, user_id, name) SELECT id, user_id, name FROM music")
    db.execute("DELETE FROM music")
    db.execute("INSERT INTO MUSIC (user_id, name) SELECT user_id, name FROM temp ORDER BY id ASC")
    db.execute("DELETE FROM temp")
    return

# move up audio playlist via DB manipulation
@app.route("/asc", methods=["POST"])
@login_required
def asc():
    name = request.form['name']
    data = db.execute("SELECT * FROM music WHERE name = ?", name)
    ID = data[0]['id']
    try:
        db.execute("INSERT INTO temp (id, user_id, name) SELECT id, user_id, name FROM music WHERE id = ? - 1 AND \
        user_id = ?", ID, session["user_id"])
        db.execute("UPDATE music SET name = (SELECT name FROM music WHERE id = ?) WHERE id = ? - 1 \
        AND user_id = ?", ID, ID, session["user_id"])
        db.execute("UPDATE music SET name = (SELECT name FROM temp) WHERE id = ? \
        AND user_id = ?", ID, session["user_id"])
        db.execute("DELETE FROM temp")  
    except:
        return redirect(url_for('music'))

# move down audio playlist via DB manipulation
@app.route("/dec", methods=["POST"])
@login_required
def dec():
    name = request.form['name']
    data = db.execute("SELECT * FROM music WHERE name = ?", name)
    ID = data[0]['id']
    try:
        db.execute("INSERT INTO temp (id, user_id, name) SELECT id, user_id, name FROM music WHERE id = ? + 1 AND \
        user_id = ?", ID, session["user_id"])
        db.execute("UPDATE music SET name = (SELECT name FROM music WHERE id = ?) WHERE id = ? + 1 \
        AND user_id = ?", ID, ID, session["user_id"])
        db.execute("UPDATE music SET name = (SELECT name FROM temp) WHERE id = ? \
        AND user_id = ?", ID, session["user_id"])
        db.execute("DELETE FROM temp")
    except:
        return redirect(url_for('music'))

# see helper function for more detail
@app.route("/YT", methods=["POST"])
@login_required
def YT():
    return YT_helper(session["user_id"])


@app.route("/create")
@login_required
def recipe():
    pnamebar = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    return render_template('create.html', pname=pnamebar)

# function for the recipe creation page
@app.route("/create", methods=['POST'])
@login_required
def ADD():
    title = request.form.get('name')
    image = request.files.get('img_file')
    intro = request.form.get('intro')
    tip = request.form.get('tip')
    typ = request.form.get('type')
    pri = request.form.get('share')
    aut = db.execute("SELECT pname FROM users WHERE id = ?", session['user_id'])

    # here we use the helper function for inserting recipe info into sql DB
    text = "INSERT INTO nutrition (kcal, fat, sat, carb, sugar, fibre, pro ,salt, nut_id, user_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_PATH2'], filename))
    file_name = os.path.splitext(filename)[0]

    ing = request.form.getlist('ing[]')
    equi = request.form.getlist('equi[]')
    meth = request.form.getlist('meth[]')

    # prevent user creating another recipe with the same name
    user_recipe_name = db.execute("SELECT title FROM recipe WHERE user_id = ?", session['user_id'])
    for i in range(len(user_recipe_name)):
        if title == user_recipe_name[i]['title']:
            return apology("recipe name already exist!", 400)

    db.execute("INSERT INTO recipe (title, author, intro, img, tip, type, privacy, likes, user_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", 
    title, aut[0]['pname'], intro, file_name, tip, typ, pri, '0', session["user_id"])

    id = db.execute("SELECT id FROM recipe WHERE title = ? and user_id = ?", title, session["user_id"])
    recipe_list(text, ing, equi, meth, id[0]["id"], session["user_id"])
    return redirect(url_for('index'))

# function for deleting recipe related info such as pictures and DB
@app.route("/delete2", methods=["POST"])
@login_required
def delete2():
    data1 = request.form['data1']
    data2 = request.form['data2']
    id = db.execute("SELECT id FROM recipe WHERE title = ? and user_id = ?", data1, session["user_id"])
    os.remove(data2)

    db.execute("DELETE FROM ingredient WHERE ing_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    db.execute("DELETE FROM equipment WHERE equi_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    db.execute("DELETE FROM method WHERE meth_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    db.execute("DELETE FROM nutrition WHERE nut_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    db.execute("DELETE FROM recipe WHERE title = ? AND user_id = ?", data1, session["user_id"])
    return 

# function for displaying exiting info on the recipe editing page
@app.route("/edit", methods=["POST"])
@login_required
def edit():
    # extract info from DB for existing recipes and send them to html page, so user can see existing info and decide what to change/edit
    title = request.form.get('title')
    data1 = db.execute("SELECT * FROM recipe WHERE title = ? AND user_id = ?", title, session["user_id"])
    id = db.execute("SELECT id FROM recipe WHERE title = ? and user_id = ?", title, session["user_id"])
    pname = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    data2 = db.execute("SELECT * FROM ingredient WHERE ing_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    data3 = db.execute("SELECT * FROM equipment WHERE equi_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    data4 = db.execute("SELECT * FROM method WHERE meth_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    data5 = db.execute("SELECT * FROM nutrition WHERE nut_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    return render_template("edit.html", data1=data1, data2=data2, data3=data3, data4=data4, data5=data5, pname=pname)

# function for editing the recipe
@app.route("/update", methods=['POST'])
@login_required
def update():
    title = request.form.get('title')
    intro = request.form.get('intro')
    tip = request.form.get('tip')
    pri = request.form.get('share')
    typ = request.form.get('type')

    ing = request.form.getlist('ing[]')
    equi = request.form.getlist('equi[]')
    meth = request.form.getlist('meth[]')

    # here we use the helper function for inserting recipe info into sql DB
    text = "UPDATE nutrition SET kcal = ?, fat = ?, sat = ?, carb = ?, sugar = ?, fibre = ?, pro = ?, salt = ? WHERE nut_id = ? AND user_id = ?"

    # entries are removed before inserting a new one for the editing functionality, however, update set command for sql DB is also viable here
    db.execute("UPDATE recipe SET intro = ?, tip = ?, privacy = ?, type = ? WHERE title = ? AND user_id = ?", intro, tip, pri, typ, title, session["user_id"])
    id = db.execute("SELECT id FROM recipe WHERE title = ? and user_id = ?", title, session["user_id"])
    db.execute("delete from ingredient WHERE ing_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    db.execute("delete from equipment WHERE equi_id = ? AND user_id = ?", id[0]["id"], session["user_id"])
    db.execute("delete from method WHERE meth_id = ? AND user_id = ?", id[0]["id"], session["user_id"])

    recipe_list(text, ing, equi, meth, id[0]["id"], session["user_id"])
    return redirect(url_for('index'))

# ensure flask app is only openned once at a time
if __name__ == '__main__':
    app.run()


    










    




    




    


    

        
				






