from newspaperclassifier.evaluation.merging import merge_labels
import click


@click.command()
@click.option('--aws-dir', type=str, help="Directory where AWS labels are stored")
@click.option('--gc-dir', type=str, help="Directory where GC labels are stored")
@click.option('--destination', type=str, help="Destination file")
def main(aws_dir, gc_dir, destination):
    """Merge stored labels"""
    merged = merge_labels(aws_dir, gc_dir)
    
    merged.to_csv(destination, index=False)
