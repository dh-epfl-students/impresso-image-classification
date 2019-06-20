import gzip
import json
import os
from base64 import standard_b64decode
from datetime import date

import pandas as pd
import requests
from dask import bag as db

from newspaperclassifier.utils import list_files

SOURCE_BUCKET = 's3://impresso-images/images-packed/*.jsonl.gz'
DUMP_BUCKET = 's3://impresso-image-labels/'
SOURCE_ENDPOINT = 'https://os.zhdk.cloud.switch.ch'

IIIF_MAPPING_URL = "https://impresso-project.ch/api/images/"

IIIF_SUFFIX = 'full/0/default.png'
IIIF_PREFIX = 'https://impresso-project.ch/api/proxy/iiif'


def get_images_data_from_s3(endpoint=SOURCE_ENDPOINT, bucket=SOURCE_BUCKET):
    dask_storage_options = {
        'client_kwargs': {'endpoint_url': endpoint},
        'key': os.environ['SE_ACCESS_KEY'], 'secret': os.environ['SE_SECRET_KEY']
        }
    image_data = db.read_text(
            bucket,
            storage_options=dask_storage_options
            ).map(json.loads)
    return image_data


def get_images_from_s3():
    """
    Fetches the images that are stored on the S3 Bucket
    The credentials must be stored in an env variable (SE_ACCESS_KEY and SE_SECRET_KEY)

    Returns:
        dask.bag: Each element has two fields ('id', and 'content')

    """
    image_data = get_images_data_from_s3()
    return image_data.map(lambda p: {'id': p['id'], 'content': standard_b64decode(p['bytes_b64'])})


def image_uid_to_iiif_url(image_id):
    """
    Transforms an image id to the url of the page on IIIF
    Args:
        image_id (str):

    Returns:
        str: The IIIF url of the image
    """
    url = os.path.join(IIIF_MAPPING_URL, image_id)  # Fetch image info
    r = requests.get(url)
    content = json.loads(r.content)
    
    if 'regions' in content:
        regions = content['regions'][0]
    else:
        return None
    page = regions['pageUid']
    coords = ','.join([str(i) for i in regions['coords']])
    return os.path.join(IIIF_PREFIX, page, coords, IIIF_SUFFIX)


def labels_to_dataframe(directory, aws=False):
    """
    Parses the labels as a pandas DataFrame for analysis
    Args:
        directory (str): Directory where files JSON files are stored (labels)
        aws (bool): Whether the labels are from AWS or not (Adds instances)

    Returns:
        pandas.DataFrame
    """
    files = list_files(directory)
    data = []
    for file in files:
        with gzip.open(file, "r") as f:
            for line in f.readlines():
                js = json.loads(line)
                image = js["id"]
                j = js["labels"]
                for d in j:
                    if aws:
                        d['Instances'] = len(d['Instances'])
                    d['Image'] = image
                data += j
    return pd.DataFrame(data)


def image_date_from_uid(image_id):
    """
    Returns the date of an image given it's UID
    Args:
        image_id (str): ID of image

    Returns:

    """
    split = image_id.split('-')
    return date(int(split[1]), int(split[2]), int(split[3]))
