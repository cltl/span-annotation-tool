# annotation/annotation.py

from flask import Blueprint, render_template, redirect, url_for, request
from flask import flash
from scripts.annotation.read_config import read_config
from scripts.save.save import save_annotation, check_folder
from scripts.extensions import cache
from glob import glob
import pandas as pd
import json
import csv
import os



annotation_blueprint = Blueprint("annotation", __name__)


def set_index(user_folder, first_id):
    """
    Start annotation from the first non-annotated text
    """
    annotations = [f for f in os.listdir(user_folder) if f.endswith(".json")]
    if len(annotations) == 0:
        id_text = int(first_id)
    else:
        last_annotation = annotations[-1]
        id_text = int(last_annotation.split("-")[1].split(".")[0]) + 1

    return id_text


def load_data(data_file):
    """
    Read the input data from the tsv file
    """
    myfile = os.path.join(os.path.dirname(__file__), "../../inputs", data_file)
    df = pd.read_csv(myfile, sep="\t", quoting=csv.QUOTE_NONE)
    
    return df

def load_annotations(user_folder,index):
    """
    Load already saved annotations, if any
    """
    annotation_filepath = os.path.join(user_folder, f"textID-{index}.json")
    existing_annotations = None
    if os.path.isfile(annotation_filepath):
        with open(annotation_filepath, "r", encoding='utf-8') as f:
            annotations_data = json.load(f)
            existing_annotations = annotations_data.get("Annotation", None)

    return existing_annotations

def is_annotation_file_valid(filepath):
    """
    Check if already saved annotations are valid
    (file exists and "Annotation" field is not empty)
    """
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    if "Annotation" not in data or not data["Annotation"]:
        return False

    return True


@annotation_blueprint.route("/annotate/<int:index>/<email>", methods=["GET", "POST"])
@cache.cached()
def annotate(index, email):

    annotation_title, guidelines_file, data_file,\
        text_column, text_id_column,\
            tags_short, tags_long, tag_colors,\
                span_question, type_in_question, trigger  = read_config()
    
    df = load_data(data_file)
    user_folder = check_folder(email)
    num_texts = len(df)

    if index >= num_texts:
        # Last text in df has been annotated
        """
        Returns each text that has not been annotated yet
        """
        # Check all annotation files
        all_saved_files = glob(os.path.join(user_folder, '*.json'))
        all_valid = all(is_annotation_file_valid(f) for f in all_saved_files)

        # If so, render the "annotation_finished" template
        if len(all_saved_files)==num_texts and all_valid:
            return render_template("annotation_finished.html")
        else:
            flash('You have left some texts unannotated.')
            # Find the first invalid file and redirect to its annotation page
            for i in range(num_texts):
                file_path = os.path.join(user_folder, f"textID-{i}.json")
                if not is_annotation_file_valid(file_path):
                    return redirect(url_for("annotation.annotate", index=i, email=email))
 
    
    # Get the text at the given index from the DataFrame
    text = df.iloc[index][text_column]

    # Calculate the index for the next/back text
    next_index = index + 1
    prev_index = index -1

    existing_annotations = load_annotations(user_folder,index)

    if request.method == "POST":
        # Do stuff depending on the button chosen by the user
        action = request.form.get("action")

        if action == "next":
            """
            Go to the next text
            """
            row = df.iloc[index]
            annotations = json.loads(request.form.get("annotations"))

            if len(annotations)!=0:
                # Save the annotations
                save_annotation(user_folder, index, row, annotations)
            return redirect(url_for("annotation.annotate", index=next_index, email=email))
        
        if action == "back" and prev_index >= 0:
            return redirect(url_for("annotation.annotate", index=prev_index, email=email))

        if action == "logout":
            """
            Save the current annotation and logout
            """
            row = df.iloc[index]

            annotations = json.loads(request.form.get("annotations"))

            if len(annotations) == 0:
                return render_template("logout_empty.html")
            else:
                save_annotation(user_folder, index, row, annotations)
                return render_template("logout.html")


    if existing_annotations is None:
        existing_annotations_list = []
    else:
        existing_annotations_list = [value for key, value in existing_annotations.items()]

    tags=list(zip(tags_short, tags_long, tag_colors))

    # Render the annotation template
    return render_template("annotation.html",
                           annotation_title = annotation_title, 
                           guidelines_file = guidelines_file,
                           span_question = span_question, 
                           type_in_question = type_in_question,
                           trigger = trigger,
                           tags=list(zip(tags_short, tags_long, tag_colors)),
                           text=text, 
                           next_index=next_index, 
                           prev_index=prev_index, 
                           email=email, 
                           total_items=num_texts, 
                           current_item=index+1, 
                           existing_annotations=existing_annotations_list
                           )
