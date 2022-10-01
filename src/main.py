from distutils.command.config import config
from sre_constants import SUCCESS
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
    if hash_password(password) == hashedpassword:
        return True
    else:
        return False
def fastLogin(username, hpassword):
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
        loggedin = fastLogin(request.cookies.get("session").split("/"[0]), request.cookies.get("session").split("/")[1])
    except:
        loggedin = False
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
                resp.set_cookie('session', f"{username}/{password}")
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
                            resp.set_cookie("session", username + "/" + hash_password(password)) #TODO: Make this a session
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
@app.route('/admin')
def admin():
    if request.cookies.get("adminsession"):
        return render_template('admin.html')
    else:
        return redirect(url_for('index'))
@app.route('/<string:page_name>')
def sendfile(page_name):
    return send_from_directory('static', page_name)
if __name__ == "__main__":
    app.run(debug=True)