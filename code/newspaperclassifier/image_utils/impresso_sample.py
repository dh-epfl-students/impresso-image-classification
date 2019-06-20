"""
Helper functions to sample images from the Database
"""
from newspaperclassifier.image_utils.impresso import image_date_from_uid, image_uid_to_iiif_url, labels_to_dataframe


def _create_buckets(size, years):
    """
    Assigns buckets for the given years, of a given size
    Args:
        size (int): Size of buckets in years
        years (list[int]): List of years to bucket (must be consecutive)

    Returns:
        dict: key=year, value=bucket_id
    """
    buckets = {}
    bucket_id = 1
    i = 0
    while i < len(years):
        bucket_years = years[i:i + size]
        for y in bucket_years:
            buckets[y] = bucket_id
        bucket_id += 1
        i += size
    return buckets


def _image_ids_with_years(directory):
    df = labels_to_dataframe(directory).drop('labels', axis=1)
    df['year'] = df.id.apply(lambda x: image_date_from_uid(x).year)
    return df


def sample_images(bucket_size, num_images, directory):
    """
    Samples images randomly over defined bucket sizes (years) from IIIF server
    Args:
        bucket_size (int): The period form which to sample images uniformly
        num_images (int): Number of images to sample for each bucket
        directory (str): Directory where labeled images are. Must contain .json.gz files, with

    Returns:

    """
    df = _image_ids_with_years(directory)
    
    years = sorted(df.year.unique())
    buckets = _create_buckets(bucket_size, years)
    df['bucket'] = df.apply(lambda x: buckets[x['year']], axis=1)
    
    sampled = df.groupby('bucket').apply(lambda x: x.drop('bucket', axis=1).sample(num_images)).reset_index().drop(
            'level_1', axis=1)
    image_urls = sampled['id'].apply(image_uid_to_iiif_url)
    
    return image_urls
