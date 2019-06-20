import json
import os


def save_json(labels, output_file):
    """
    Saves the given dictionary in a json file
    Args:
        labels:
        output_file:

    Returns:

    """
    with open(output_file, 'w') as f:
        json.dump(labels, f)


def _get_split_base_name(filepath):
    """
    Given any file path, returns the name without the full path and extension
    Args:
        filepath (str):

    Returns:
        str: The name of the file without path and extension
    """
    return os.path.splitext(os.path.basename(filepath))[0]


def _get_json_path_from_id(directory, image_id):
    """
    Transforms the given image ID to the JSON label file, in the given directory
    Args:
        directory (str): Relative path to a directory where the file will be
        image_id (str): The ID of the image, as outputted by `image_id_from_url`

    Returns:
        (str): The absolute path of the json file
    """
    return os.path.abspath(os.path.join(directory, image_id + ".json"))


def get_local_labels_filepath(filepath, destination):
    """
    Transforms a local URL into a local filepath where the Labels will be stored (.JSON)
    Args:
        filepath (str): The local filepath
        destination (str): A local directory

    Returns:
        str:
    """
    base_name = _get_split_base_name(filepath)
    return _get_json_path_from_id(destination, base_name)


def list_files(directory):
    return [os.path.abspath(os.path.join(directory, i)) for i in os.listdir(directory)]
