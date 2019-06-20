import numpy as np
import pandas as pd
from tqdm import tqdm


def get_similar_label_count(merged_df, similar_dict, min_score=0, bar=False):
    """
    
    Args:
        merged_df (pandas.DataFrame): DataFrame of merged labels
        similar_dict (dict): Dictionary of similar images with scores
        min_score (float): Minimum score of similarity for an image to be considered
        bar (bool): Show progress bar


    """
    df_labels = pd.DataFrame(merged_df.groupby('Image')['label'].apply(list))  # List of labels for each image
    
    result = []
    iterable = df_labels.iterrows()
    if bar:
        iterable = tqdm(iterable)
    
    for im, labels in iterable:
        labs = set(labels.label)
        similar_ims = [x[0] for x in similar_dict[im] if x[1] > min_score]  # Get only image names
        
        similar_labels = df_labels[df_labels.index.isin(similar_ims)].label.values
        num_similar = len(similar_labels)
        
        if num_similar > 0:
            flattened = np.concatenate(similar_labels)
            lb, cnts = np.unique(flattened, return_counts=True)  # Returns labels, counts
            res = dict([(l, int(c)) for l, c in zip(lb, cnts) if l in labs])
            
            result.append({'Image': im, 'counts': res, 'num_similar': num_similar})
    return pd.DataFrame(result)


def compute_label_scores(label_counts):
    label_ratios = label_counts.assign(
            ratios=label_counts.apply(lambda r: {k: v / r.num_similar for k, v in r.counts.items()}, axis=1))
    
    label_ratios = pd.DataFrame([y for x in label_ratios.ratios.apply(lambda x: list(x.items())).values for y in x],
                                columns=['label', 'score'])
    
    label_scores = label_ratios.groupby('label').agg({'score': ['mean', 'std', 'count']}).reset_index()
    
    return label_scores
