import os
import requests
import urllib.parse
import yt_dlp
import configparser

from cs50 import SQL
from pathlib import Path
from flask import redirect, render_template, request, session, url_for
from functools import wraps
from datetime import datetime

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///food.db")

# redirect error messages to users when input is not accepted
def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# extract recipe info from sql DB 
def recipe_db(a, b, c, j, i):
    profile = db.execute("select * from recipe where id = ? and user_id = ?", j, i)
    data1 = db.execute("select * from ingredient where ing_id = ? and user_id = ?", j, i)
    data2 = db.execute("select * from equipment where equi_id = ? and user_id = ?", j, i)
    data3 = db.execute("select * from method where meth_id = ? and user_id = ?", j, i)
    data4 = db.execute("select * from nutrition where nut_id = ? and user_id = ?", j, i)
    return render_template('player.html', files=a, num=b, profile=profile, data1=data1, data2=data2, data3=data3, data4=data4, uid = c)

# insert recipe info into sql DB 
def recipe_list(t, e, f, g, a, b):
    for i in range(len(e)):
        db.execute("INSERT INTO ingredient (ing_id, ing, user_id) VALUES(?, ?, ?)", a, e[i], b)

    for j in range(len(f)):
        db.execute("INSERT INTO equipment (equi_id, equi, user_id) VALUES(?, ?, ?)", a, f[j], b)
    
    for m in range(len(g)):
         db.execute("INSERT INTO method (meth_id, meth, user_id) VALUES(?, ?, ?)", a, g[m], b)

    kcal = request.form.get('kcal')  
    fat = request.form.get('fat')  
    sat = request.form.get('sat')  
    carb = request.form.get('carb')
    sugar = request.form.get('sugar')  
    fibre = request.form.get('fibre')  
    pro = request.form.get('pro')  
    salt = request.form.get('salt')
    db.execute(t, kcal, fat, sat, carb, sugar, fibre, pro, salt, a, b)

# allows the download of utube videos and convert them into audio file via the youtube-dl module
def YT_helper(t):
    n = str(session["user_id"])
    p = 'static/upload_data/music_' + n
    text = request.form.getlist('url[]')
    ydl_opts = {
	"outtmpl": p + '/%(title)s.%(ext)s',
    "format": "bestaudio/best",
    "noplaylist": True,
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
	}

    for i in range(len(text)):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"{text[i]}"])
                info = ydl.extract_info(text[i], download=False)
                name = Path(ydl.prepare_filename(info)).stem
                db.execute("INSERT INTO music (name, user_id) VALUES(?, ?)", name, t)          
        except:
            return apology("Invalid youtube URL!", 400)
    return redirect(url_for('music'))

# openweathermap api key is stored in config file, this function access it via the configparser module
def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']

# connect to openweathermap api url to get weather info and return them in json format
def get_weather_results(loc, count, api_key):
    # api_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=metric&appid={}".format(lat, lon, api_key)
    api_url = "https://api.openweathermap.org/data/2.5/weather?q={},{}&units=metric&appid={}".format(loc, count, api_key)
    r = requests.get(api_url)
    return r.json()

# access json file info returned from the api url above
def weather_part_db(d, i, j, u):
    temp1 = "{0:.1f}".format(d["main"]["temp"])
    temp2 = "{0:.1f}".format(d["main"]["feels_like"])
    weather = d["weather"][0]["main"]
    unix = int(d["dt"])
    zone = int(d["timezone"])
    local = unix + zone
    time = datetime.utcfromtimestamp(local).strftime('%Y-%m-%d %H:%M')
    t1 = datetime.utcfromtimestamp(local).strftime('%H').lstrip("0").replace(" 0", " ")

    data = db.execute("SELECT * FROM weather WHERE user_id = ?", u)
# if weather sql DB is emptied in the first place, we create an empty entry in the DB for the user, otherwise update existing one
    if (len(data) == 0):
        db.execute("INSERT INTO weather (user_id, local, count, temp, ftemp, wea, time, hour) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
        u, i, j, temp1, temp2, weather, time, t1)
    else:
        db.execute("UPDATE weather SET local = ?, count = ?, temp = ?, ftemp = ?, wea = ?, time = ?, hour = ? WHERE user_id = ?", 
        i, j, temp1, temp2, weather, time, t1, u)

