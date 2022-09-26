from distutils.command.config import config
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import pymongo 
import os
import hashlib
import dotenv
import json
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
        username = request.form['username']
        password = request.form['password']
        data = list(accounts.find({"username":username}))
        if data == []:
            return render_template('login.html', error="Username Not Found")
        else:
            if passwordValidate(password, data[0]['password']):
                return "Login Successful"
            else:
                return render_template('login.html', error="Invalid Password")
    else:
        return render_template('login.html')
@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #TODO: Check if username is taken
        #TODO: Check is email is valid
        #TODO: Check if already registered for both email and username
        #TODO: Check if already loggedin
        username = request.form['username']
        password = request.form['password']
        data = list(accounts.find({"username":username}))
        if data == []:
            accounts.insert_one({"username":username, "password":hash_password(password)})
            return "Account Created"
        else:
            return render_template('register.html', error="Username Already Exists")
    else:
        return render_template('register.html')
# TODO: Make school sign up page
# TODO: Make user register page functional
# TODO: Make "verified" email a thing
# TODO: Make a system to add score and such

# TODO: Make admin panel
@app.route('/<string:page_name>')
def sendfile(page_name):
    return send_from_directory('static', page_name)
if __name__ == "__main__":
    app.run(debug=True)