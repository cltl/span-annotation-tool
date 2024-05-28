# login/login.py

from flask import Blueprint, render_template, request,  redirect, url_for
from scripts.save.save import check_folder
import configparser
import os

login_blueprint = Blueprint("login", __name__)

def title_and_users():
    """
    Title of the interface,
    users who can take the annotation
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "../..", "config.ini"))

    annotation_title=config.get("general", "title")
    authorized_users = config.get("general", "authorized_users").split(",")
    
    return annotation_title, authorized_users


@login_blueprint.route("/", methods=["GET", "POST"])
def welcome():
    """
    Proceed with the annotation only if 
    the email is in the list of authorized users
    """
    annotation_title, authorized_users = title_and_users()
    if request.method == "POST":
        email = request.form.get("email")

        if email in authorized_users:
            return render_template('first_page.html', email=email)
        else:
            return "You are not authorized to proceed with the annotation."
    
    return render_template("welcome.html", annotation_title=annotation_title)


        
@login_blueprint.route("/start_annotation/<email>", methods=["POST"])
def start_annotation(email):
    """
    Check if texts have been annotated    
    If not, start from the beginning
    If yes, start from the next text 
    """

    action = request.form.get("action")

    if action == "new":
        return redirect(url_for("annotation.annotate", index=0, email=email))
    
    elif action == "resume":
        annotation_title, authorized_users = title_and_users()
        user_folder = check_folder(email)
        
        # Find all saved annotation files, and start from the next text
        answer_files = [f for f in os.listdir(user_folder) if f.endswith(".json")]
    
        index_numbers = [int(f.split('-')[1].split('.')[0]) for f in answer_files]
        max_index = max(index_numbers)+ 1 if index_numbers else 0

        return redirect(url_for("annotation.annotate", index=max_index, email=email))
