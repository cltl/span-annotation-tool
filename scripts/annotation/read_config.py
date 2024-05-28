import configparser
import os

def read_config():
    # Read the config.ini file
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "../..", "config.ini"))

    annotation_title=config.get("general", "title")
    guidelines_file=config.get("general", "guidelines_file")


    data_file = config.get("data", "data_file")
    text_column = config.get("data", "text_column")
    text_id_column = config.get("data", "text_id_column")

    tags_short = config.get('annotations', 'TAGS_SHORT').split('-')
    tags_long = config.get('annotations', 'TAGS_LONG').split('-')
    tag_colors = config.get('annotations', 'TAG_COLORS').split('-')

    type_in_question = config.get('questions', 'type_in_question')
    trigger = config.get('questions', 'trigger')
    span_question = config.get('questions', 'span_question')

    return annotation_title, guidelines_file, data_file,\
        text_column, text_id_column,\
            tags_short, tags_long, tag_colors,\
                span_question, type_in_question, trigger