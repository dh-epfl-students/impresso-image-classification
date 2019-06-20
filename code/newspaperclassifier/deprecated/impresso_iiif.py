import json
import os

import requests
from dask import bag as db
from impresso_commons.path import parse_canonical_filename

SOURCE_BUCKET = 's3://impresso-public/canonical-with-images/*.jsonl.bz2'
SOURCE_ENDPOINT = 'https://os.zhdk.cloud.switch.ch'
IMPRESSO_USER = 'guest'

"""
-----------------------------DEPRECATED-----------------------------
These methods are the old way of fetching images, which were store on the IIIF server
 """


def _is_image(item):
    """Filter function to keep only images."""
    return item['m']['tp'] == 'image'


def _get_iiif_url_local(page_id, box):
    """ Returns impresso iiif url given a page id and a box
    :param page_id: impresso page id, e.g. EXP-1930-06-10-a-p0001
    :type page_id: str
    :param box: iiif box (x, y, w, h)
    :type box: str (4 coordinate values blank separated)
    :return: iiif url of the box
    :rtype: str
    """
    base = "http://dhlabsrv17.epfl.ch/iiif_impresso"
    suffix = "full/0/default.jpg"
    return os.path.join(
            base, page_id,
            ','.join([str(c) for c in box]),
            suffix
            )


def _expand_page_id(image):
    """
    Expands the page number (where an image is found) to the page canonical id.
    """
    image_id = image['m']['id']
    
    # parse the content item ID into its components
    newspaper, date, edition, ci_type, ci_n, _ = parse_canonical_filename(image_id)
    
    # images should not span more than one page, so it's safe to do this
    page = image['m']['pp'][0]
    
    # fill in a canonical ID pattern
    page_id = f"{newspaper}-{'-'.join(date)}-{edition}-p{str(page).zfill(4)}"
    image['m']['pp'] = page_id
    return image


def _image2link(image):
    """
    Transforms an image into its iiif link.
    """
    page_id = image['m']['pp']
    box = image['c']
    return _get_iiif_url_local(page_id, box)


def _get_image_dicts_from_s3(bucket_url, endpoint):
    bag = db.read_text(bucket_url,
                       storage_options={
                               'client_kwargs': {'endpoint_url': endpoint},
                               'anon': True
                               }).map(json.loads)
    bag = bag.pluck('i').flatten().persist()
    images = bag.filter(_is_image).persist()
    return images


def get_image_urls_from_s3(bucket_url=SOURCE_BUCKET, endpoint=SOURCE_ENDPOINT):
    """
    Reads JSON files from Impresso S3, and returns the list of urls corresponding to all the images
    Args:
        bucket_url (str): URL of the bucket to read from
        endpoint (str): The endpoint of the bucket to read from

    Returns:
        list[str]: The list of image urls in IIIF server
    """
    images = _get_image_dicts_from_s3(bucket_url, endpoint)
    image_urls = images.map(_expand_page_id).map(_image2link).compute()
    return image_urls


def get_image_content_from_url(url):
    """
    Gets the image from the given url, using the credentials
    Args:
        url (str):

    Returns:
        bytes: The content of the image
    """
    password = os.environ['IMPRESSO_PASSWORD']
    r = requests.get(url, auth=(IMPRESSO_USER, password))
    return r.content
