from distutils.command.config import config
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
#import idom
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/<string:page_name>')
def sendfile(page_name):
    return send_from_directory('static', page_name)
if __name__ == "__main__":
    app.run(debug=True)