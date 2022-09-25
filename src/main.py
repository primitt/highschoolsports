from distutils.command.config import config
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import pymongo 
import os
import hashlib
import dotenv
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
    return render_template('index.html')
@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        school = request.form['school']
        data = list(schools.find({"name":school}))
        if data == []:
            return render_template('index.html', error="No data found")
        else:
            return "data found"

@app.route('/<string:page_name>')
def sendfile(page_name):
    return send_from_directory('static', page_name)
if __name__ == "__main__":
    app.run(debug=True)