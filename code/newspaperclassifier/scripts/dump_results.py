import os

import click
import pandas as pd
from dask.diagnostics import ProgressBar
from tqdm import tqdm
import json

from newspaperclassifier.image_utils.impresso import DUMP_BUCKET, SOURCE_ENDPOINT, get_images_data_from_s3


def _tuplize(it):
    return [tuple(x) for x in it]


def prepare_data(merged_labels, bar=False):
    grouped = merged_labels.groupby('Image')
    result = {}
    if bar:
        grouped = tqdm(grouped)
    
    for im, g in grouped:
        m = g.assign(mean=g.apply(lambda r: (r.gc_score + r.aws_score) / 2.0, axis=1))
        common = _tuplize(m[m.is_common][['label', 'mean']].values)
        gc_labels = _tuplize(m[~m.gc_label.isna()][['gc_label', 'gc_score']].values)
        aws_labels = _tuplize(m[~m.aws_label.isna()][['aws_label', 'aws_score']].values)
        result[im] = {'gc_labels': gc_labels, 'aws_labels': aws_labels, 'common_labels': common}
    
    return result


def add_fields(js, results):
    image_id = js['id']
    labels = results.get(image_id, {})
    for k, v in labels.items():
        js[k] = v
    return js


@click.command()
@click.option('--merged', type=str, help="File where merged labels is stored")
@click.option('--endpoint', type=str, help="Endpoint of bucket to store results to", default=SOURCE_ENDPOINT)
@click.option('--bucket', type=str, help="Destination bucket", default=DUMP_BUCKET)
@click.option('--bar', help="Show progress bar", is_flag=True)
def main(merged, endpoint, bucket, bar):
    dask_storage_options = {
        'client_kwargs': {'endpoint_url': endpoint},
        'key': os.environ['SE_ACCESS_KEY'], 'secret': os.environ['SE_SECRET_KEY']
        }
    
    merged_df = pd.read_csv(merged, low_memory=False)
    to_dump = prepare_data(merged_df, bar)
    
    source_data = get_images_data_from_s3()
    
    result = source_data.map(lambda js: json.dumps(add_fields(js, to_dump)))
    if bar:
        with ProgressBar():
            result.to_textfiles(bucket, storage_options=dask_storage_options)
    else:
        result.to_textfiles(bucket, storage_options=dask_storage_options)
    
    print("---------- Dump of labels done ----------")
