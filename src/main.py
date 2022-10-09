from distutils.command.config import config
from sre_constants import SUCCESS
from tkinter import E
from flask import Flask, make_response, render_template, request, redirect, url_for, flash, send_from_directory
import pymongo 
import os
import hashlib
import dotenv
import json
import re
import services
dotenv.load_dotenv()


def hash_password(password):
    # Hash a password for storing.
    hashedpassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashedpassword
def passwordValidate(password, hashedpassword):
    print(password, hashedpassword)
    if hashlib.sha256(password.encode('utf-8')).hexdigest() == hashedpassword:
        return True
    if password == hashedpassword:
        return True
    else:
        return False
def fastLogin(username, hpassword):
    print(username, hpassword)
    try:
        data = list(accounts.find({"username":username}))
        if data == []:
            return False
        else:
            if passwordValidate(hpassword, data[0]["password"]):
                return True
            else:
                return False
    except:
        return False
def adminFastLogin(username, hpassword):
    print(username, hpassword)
    try:
        data = list(admindb.find({"username":username}))
        if data == []:
            return False
        else:
            if passwordValidate(hpassword, data[0]["password"]):
                return True
            else:
                return False
    except:
        return False
# setup mongodb
client = pymongo.MongoClient(os.getenv("PYMONGO"))
db = client["LS"]
col = db["LS-SCORE"]
schools = db["LS-SCHOOLS"]
accounts = db["LS-ACCOUNTS"]
admindb = db["LS-ADMIN"]
#TODO: SESSIONDB = db["LS-SESSIONS"]
#import idom
app = Flask(__name__)
@app.route('/')
def index():
    try:
        log = fastLogin(request.cookies.get("session").split("/")[0], request.cookies.get("session").split("/")[1])
        if log:
            loggedin = "SESSIONTRUE"
        else:
            loggedin = "SESSIONFALSE"
    except:
        try:
            log = adminFastLogin(request.cookies.get("adminsession").split("/")[0], request.cookies.get("adminsession").split("/")[1])
            if log:
                loggedin = "ADMINTRUE"
            else:
                loggedin = "ADMINFALSE"
        except:
            loggedin = "FALSE"
    return render_template('index.html', loggedin=loggedin)
@app.route('/search', methods=['POST'])
def search():
    # TODO: Make this redirect to the school page
    # TODO: Make school profiles
    if request.method == 'POST':
        school = request.form['school']
        data = list(schools.find({"name":school}))
        if data == []:
            return render_template('index.html', error="No data found")
        else:
            return "data found"
@app.route('/regschools')
def regschools():
    data = schools.find()
    sch = []
    for school in data:
        sch.append(school['name'])
    return {"data":sch}
@app.route('/login', methods=['GET', 'POST'])
def login():
    #TODO: Check if already loggedin
    if request.method == 'POST':
        if request.cookies.get("session"):
            return redirect(url_for('index'))
        username = request.form['username']
        password = request.form['password']
        data = list(accounts.find({"username":username}))
        if data == []:
            return render_template('login.html', error="Username Not Found")
        else:
            if passwordValidate(password, data[0]['password']):
                resp = make_response(redirect(url_for('index')))
                resp.set_cookie('session', f"{username}/{hash_password(password)}")
                return resp
            else:
                return render_template('login.html', error="Invalid Password")
    else:
        if request.cookies.get("session"):
            return redirect(url_for('index'))
        return render_template('login.html')
@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.cookies.get("session"):
            return redirect(url_for('index'))
        username = request.form['username']
        password = request.form['password']
        data = list(accounts.find({"username":username}))
        if data == []:
            is_already_registered = list(accounts.find({"email":request.form['email']}))
            if is_already_registered != []:
                return render_template('register.html', error="Email already registered")
            if password == request.form['password2']:
                if len(password) > 6:
                    regex = re.compile('[A-z0-9!@#$%^&*]')
                    if regex.search(password):
                        if regex.search(username):
                            if services.services.banned_words(username=username):
                                return render_template('signup.html', error="Username contains banned words")
                            accounts.insert_one({"username":username, "password":hash_password(password), "email":request.form['email']})
                            resp = make_response(redirect(url_for('index', message="Welcome " + username, success="true")))
                            hashed = hash_password(password)
                            print(hashed)
                            resp.set_cookie("session", username + "/" + hashed) #TODO: Make this a session
                            return resp
                        else:
                            return render_template('register.html', error="Username contains invalid characters. Only letters, numbers, and !@#$%^&* are allowed")
                    else:
                        return render_template('register.html', error="Password contains illegal characters. Only A-z, 0-9, and !@#$%^&* are allowed")
                else:
                    return render_template('register.html', error="Password is too short. Password must be at least 8 characters long")
            else:
                return render_template('register.html', error="Passwords do not match")
        else:
            return render_template('register.html', error="Username is already taken")
    else:
        if request.cookies.get("session"):
            return redirect(url_for('index'))
        return render_template('register.html')
@app.route('/api/checkusername', methods=['GET'])
def checkusername():
    if request.method == 'GET':
        username = request.args.get('username')
        data = list(accounts.find({"username":username}))
        if data == []:
            return {"status":"available"}
        else:
            return {"status":"taken"}

# TODO: Make school sign up page
@app.route('/admin/login', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data = list(admindb.find({"username":username}))
        if data == []:
            return render_template('adminlogin.html', error="Username Not Found")
        else:
            if passwordValidate(password, data[0]['password']):
                resp = make_response(redirect(url_for('admin')))
                resp.set_cookie("adminsession", username + "/" + hash_password(password)) #TODO: Make this a session
                return resp
            else:
                return render_template('adminlogin.html', error="Invalid Password")
    else:
        return render_template('adminlogin.html')

# TODO: Make "verified" email a thing
# TODO: Make a system to add score and such
# TODO: Make admin panel
@app.route('/admin/creategame', methods=['GET', 'POST'])
def creategame():
    if request.method == "POST":
        if request.cookies.get("adminsession"):
            if adminFastLogin(request.cookies.get("adminsession").split("/")[0], request.cookies.get("adminsession").split("/")[1]):
                gamename = request.form['name']
                date = request.form['date']
                time = request.form['time']
                location = request.form['location']
                opponent = request.form['opponent']
                sport = request.form['sport']
                if gamename == "":
                    return render_template('creategame.html', error="Game name cannot be blank")
                if date == "":
                    return render_template('creategame.html', error="Date cannot be blank")
                if time == "":
                    return render_template('creategame.html', error="Time cannot be blank")
                if location == "":
                    return render_template('creategame.html', error="Location cannot be blank")
                if opponent == "":
                    return render_template('creategame.html', error="Opponent cannot be blank")
                if sport == "":
                    return render_template('creategame.html', error="Sport cannot be blank")
                # get schools from admindb
                admin = list(admindb.find({"username":request.cookies.get("adminsession").split("/")[0]}))
                if admin == []:
                    return redirect(url_for('adminlogin'))
                else:
                    school = list(schools.find({"id":int(admin[0]['schools'][0])}))[0]["teamname"] # FIXME: This needs to be automatic school finder in the future!, PLEASE ADVISE
                    col.insert_one({"gamename":gamename, "date":date, "time":time, "home":school, "location":location, "opponent":opponent, "sport":sport, "score":{"home":0, "away":0}})
                    return redirect(url_for('admin'))
    else:
        if request.cookies.get("adminsession"):
            if adminFastLogin(request.cookies.get("adminsession").split("/")[0], request.cookies.get("adminsession").split("/")[1]):
                return render_template('creategame.html')
            else:
                return redirect(url_for('adminlogin'))
        else:
            return redirect(url_for('adminlogin'))
@app.route('/admin')
def admin():
    if request.cookies.get("adminsession"):
        if adminFastLogin(request.cookies.get("adminsession").split("/")[0], request.cookies.get("adminsession").split("/")[1]):
            # get all games
            games = list(col.find())
            if games == []:
                return render_template('admin.html', games="none")
            return render_template('admin.html', games=games)
        else:
            return redirect(url_for('adminlogin'))
    else:
        return redirect(url_for('adminlogin'))
@app.route('/admin/gameid/<int:id>')
def gameid(id):
    if request.cookies.get("adminsession"):
        if adminFastLogin(request.cookies.get("adminsession").split("/")[0], request.cookies.get("adminsession").split("/")[1]):
            # get game
            game = list(col.find({"gameid":id}))
            if game == []:
                return redirect(url_for('admin'))
            return render_template('edit.html', game=game[0])
        else:
            return redirect(url_for('adminlogin'))
    else:
        return redirect(url_for('adminlogin'))
@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('session', '', expires=0)
    return resp
@app.route('/admin/logout')
def adminlogout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('adminsession', '', expires=0)
    return resp
@app.route('/<string:page_name>')
def sendfile(page_name):
    return send_from_directory('static', page_name)
if __name__ == "__main__":
    app.run(debug=True)