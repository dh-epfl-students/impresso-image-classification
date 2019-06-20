import click
import pandas as pd
from json import load
from newspaperclassifier.evaluation.label_evaluation import get_similar_label_count, compute_label_scores
import ast


@click.command()
@click.option('--merged', help="File of merged labels", type=str)
@click.option('--similar-images', help="File of similar images (json)", type=str)
@click.option('--similar-label-count', help="File containing the count of similar labels", default=None)
@click.option('--destination', help="Destination to save the results")
@click.option('--bar', help="Show progress bar", is_flag=True)
@click.option('--min-score', help="Minimum score for similarity", default=0)
def main(merged, similar_images, similar_label_count, destination, min_score, bar):
    """Evaluate the score of each label using the REPLICA tool"""
    merged_df = pd.read_csv(merged, low_memory=False)
    
    if similar_label_count is None:
        with open(similar_images, 'r') as f:
            similar_dict = load(f)
        similar_label_count = get_similar_label_count(merged_df, similar_dict, min_score, bar)
    else:
        similar_label_count = pd.read_csv(similar_label_count, converters={'counts': ast.literal_eval})
    
    label_scores = compute_label_scores(similar_label_count)
    label_scores.columns = ['label', 'score_mean', 'score_std', 'count']
    label_scores.to_csv(destination, index=False)
