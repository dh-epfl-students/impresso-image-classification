import os
from json import dump

import click
import pandas as pd
import pysolr
from tqdm import tqdm


def get_similar_images(image_id, solr, nrows):
    """
    Function that returns the visually similar images of the given image
    Args:
        image_id (str): ID of the image
        solr (pysolr.solr): SOLR object
        nrows (int): Number of similar images to ask from the API

    Returns:
        list[(str, float)]: Similar images ids and the similarity score
    """
    field_name = "_vector_InceptionResNetV2_bv"
    vector = list(solr.search(f'id:{image_id}', fl=field_name))[0][field_name]
    similar = list(solr.search('{{!vectorscoring f="{:}" vector_b64="{:}"}}'.format(field_name, vector),
                               fl="*,score",
                               rows=nrows,
                               ))
    return [(x['id'], x['score']) for x in similar if x['id'] != image_id]


@click.command()
@click.option('--merged-file', type=str, help="Location of merged labels file")
@click.option('--destination', type=str, help="Destination file for saving", required=True)
@click.option('--bar', help="With progress bar", is_flag=True)
@click.option('-n', type=int, help="Number of similar images to request", default=50)
def main(merged_file, destination, bar, n):
    """Get a certain number of similar images for each image in the merged file, using Replica.
        Saves the result as json file.
    """
    df = pd.read_csv(merged_file).drop('Unnamed: 0', axis=1)
    image_ids = df.Image.unique()
    if bar:
        image_ids = tqdm(image_ids)
    
    url = f"https://{os.environ['SOLR_USER']}:{os.environ['SOLR_PASS']}@solrdev.dhlab.epfl.ch/solr/impresso_images/"
    solr = pysolr.Solr(url)
    
    result = {}
    for im in image_ids:
        similar = get_similar_images(im, solr, n)
        result[im] = similar
    
    with open(destination, 'w') as f:
        dump(result, f)
        
    print("------------End Replica------------")
