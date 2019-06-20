"""
Script to perform classification on either classifiers
"""

import os
from json import dumps

import click
from dask.diagnostics import ProgressBar

from newspaperclassifier.classifiers import AwsClassifier, GCClassifier
from newspaperclassifier.image_utils.impresso import get_images_from_s3
from newspaperclassifier.utils import get_local_labels_filepath, list_files, save_json

classifiers = {'aws': AwsClassifier, 'gc': GCClassifier}


def single_label_local(classifier, filepath, destination):
    """
    Labels one image stored locally
    Args:
        classifier (ClassifierABC):
        filepath (str): Path of image to label
        destination (str): Directory where to store labels
    """
    classifier = classifier()
    output = get_local_labels_filepath(filepath, destination)
    labels = classifier.get_image_labels_local(filepath)
    save_json(labels, output)


def single_label_s3(classifier, image_data):
    """
    Classifies a single image, given the image data
    Args:
        classifier (ClassifierABC):
        image_data (dict): With keys=['id', 'content']

    Returns:
        dict: With key=['id', 'labels']
    """
    labels = classifier.get_image_labels_from_bytes(image_data['content'])
    new_data = {'id': image_data['id'], 'labels': labels}
    return new_data


def batch_label_local(classifier, directory, destination):
    """
    Labels a batch of images stored locally, in a directory
    Args:
        classifier (ClassifierABC):
        directory (str): Directory where images are stored
        destination (str): Directory where to store labels

    Returns:

    """
    files = list_files(directory)
    for f in files:
        single_label_local(classifier, f, destination)


def _label_partition(partition, classifier):
    """
    Labels a partition of a Dask bag (needs to be done sequentially)
    Args:
        partition (list[dict]): The list of images in this partition
        classifier (ClassifierABC):

    Returns:
        list[dict]: The input images, labeled
    """
    classifier = classifier()
    return [dumps(single_label_s3(classifier, x)) for x in partition]


def batch_label_s3(classifier, destination, bar=False):
    """
    Given a classifier and destination folder, performs parallel labelization of all images stored on the S3
    Args:
        classifier (ClassifierABC): Some classifier
        destination (str): Destination folder to store labels
        bar (bool): Whether to show progress bar
    """
    image_data = get_images_from_s3()
    if bar:
        with ProgressBar():
            
            image_data = image_data.repartition(1).map_partitions(lambda part: _label_partition(part, classifier))
            image_data.to_textfiles(f"{destination}/*.json.gz")
    else:
        
        image_data = image_data.map_partitions(lambda part: _label_partition(part, classifier))
        image_data.to_textfiles(f"{destination}/*.json.gz")


@click.command()
@click.option('--client', type=click.Choice(['aws', 'gc']), help='Which client to use (GC or AWS)', required=True)
@click.option('--destination', help='Destination folder to store results', required=True)
@click.option('-b', is_flag=True, help='Batch mode')
@click.option('-l', is_flag=True, help='Local mode - Use images stored locally')
@click.option('--directory', help='Directory where images to be classified are stored (local+batch mode)', type=str)
@click.option('--image', help='Path of image to classify (local+single mode)')
@click.option('--bar', help="Show progress bar (remote+batch mode)", is_flag=True)
def main(client, destination, b, l, directory, image, bar):
    """Classify images stored locally or on Impresso S3 server, using AWS or GoogleCloud Vision"""
    classifier = classifiers[client]
    destination = os.path.abspath(destination)
    
    if b:  # Batch mode
        if l:
            batch_label_local(classifier, directory, destination)
        else:
            batch_label_s3(classifier, destination, bar=bar)
    else:  # Single mode
        if l:
            single_label_local(classifier, image, destination)
        else:
            print("No single mode for remote server")
    
    print("------------End classification------------")

