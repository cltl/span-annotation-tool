# save/save.py
import json
import os


def save_annotation(user_folder, index, data, annotations_list):

    # Generate the filename
    filename = f"textID-{index}.json"

    # Create an empty JSON file in the answers folder
    filepath = os.path.join(user_folder, filename)
    
    with open(filepath, "w") as file:
        # Save the annotation data here
        annotation_data = data.to_dict()
        annotation_data["Annotation"] = {i:annotations_list[i-1] for i in range(1, len(annotations_list)+1)}

        json.dump(annotation_data, file, ensure_ascii=False)
    


def check_folder(username):

    # Check if the folder for the given username exists
    answers_folder = os.path.join(os.path.dirname(__file__), "../..", "outputs")

    short_user = username.split("@")[0]
    for char in short_user:
        if not char.isalnum():
            short_user = short_user.replace(char, "_")

    user_folder = os.path.join(answers_folder, short_user )

    if not os.path.exists(user_folder):
        # Create the folder if it doesn't exist
        os.makedirs(user_folder)

    return user_folder

