"""
Utility functions for merging the labels given by AWS and GC.

These functions do a smart merging, by first constructing the hierarchy from AWS, and then extending the GC labels
with this known hierarchy.

Future steps would be to use NLP to match labels with common meaning.
"""

import pandas as pd
from newspaperclassifier.image_utils.impresso import labels_to_dataframe
from newspaperclassifier.evaluation.tree_aggregation import build_tree


def _add_parents(df, tree):
    """
    Adds the parents of AWS labels to labels in GC that are common.
    Args:
        df (pandas.DataFrame):
        tree (dict):

    Returns:
        pandas.DataFrame
    """
    to_add = []
    for im, g in df.groupby('Image'):  # For each image
        labs = g.gc_label.unique()  # Take unique labels
        added = set()
        for i, r in g.iterrows():
            parents = tree.get(r.gc_label, [])  # Get the parents of the label in the AWS tree
            for p in parents:
                if p not in labs and p not in added:  # Add parent label if not already present
                    to_add.append(pd.Series({'Image': r.Image, 'gc_label': p, 'gc_score': r.gc_score}))
                    added.add(p)
    return pd.concat([df, pd.DataFrame(to_add)])


def _join_labels(gc, aws):
    """
    Joins the labels into one single DataFrame
    Args:
        gc (pandas.DataFrame):
        aws (pandas.DataFrame):

    Returns:
        pandas.DataFrame
    """
    joined = gc.merge(aws, how='outer', left_on=['Image', 'gc_label'], right_on=['Image', 'aws_label'])
    joined = joined.assign(label=joined.apply(lambda r: r.gc_label if pd.isnull(r.aws_label) else r.aws_label, axis=1))
    joined = joined.assign(is_common=joined.apply(lambda r: r.gc_label == r.aws_label, axis=1))
    return joined


def merge_labels(aws_dir, gc_dir):
    """
    Merges the labels found by AWS and GC, and stores them in a DataFrame
    Args:
        aws_dir (str): Directory where AWS labels are stored
        gc_dir (str): Directory where GC labels are stored

    Returns:
        pandas.DataFrame : Of merged labels
    """
    df_aws = labels_to_dataframe(aws_dir, aws=True)
    df_aws = df_aws.rename(
            columns={'Name': 'aws_label', 'Confidence': 'aws_score'}).drop(['Parents', 'Instances'], axis=1)
    
    df_gc = labels_to_dataframe(gc_dir)
    df_gc = df_gc.rename(columns={'description': 'gc_label', 'score': 'gc_score'}).drop(['mid', 'topicality'], axis=1)
    
    df_gc.gc_label = df_gc.gc_label.str.lower()
    df_aws.aws_label = df_aws.aws_label.str.lower()
    df_gc.gc_score = df_gc.gc_score * 100
    
    df_gc = df_gc.groupby(['Image', 'gc_label']).aggregate({'gc_score': 'mean'}).reset_index()
    
    aws_tree = build_tree(aws_dir)
    df_gc = _add_parents(df_gc, aws_tree)
    
    df_joined = _join_labels(df_gc, df_aws)
    
    return df_joined
