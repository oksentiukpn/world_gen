from flask import Blueprint, render_template

main = Blueprint("main", __name__)


# 404 error handler
@main.errorhandler(404)
def not_found(error):
    return '<h1 style="color: red;">404 Not Found</h1>', 404


@main.route("/")
@main.route("/home")
def home():
    return "None"
