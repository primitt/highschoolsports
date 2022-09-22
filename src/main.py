from distutils.command.config import config
from flask import Flask, render_template, request, redirect, url_for, flash

from idom import component, html
from idom.backend.flask import configure
app = Flask(__name__)
@component
def index():
    return html.div(
        html.h1("Hello World!"),
    )

if __name__ == "__main__":
    configure(app, index)
    app.run(debug=True)