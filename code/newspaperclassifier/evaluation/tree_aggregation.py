from json import loads

import dask.bag as db


def _parse(im):
    """
    Helper function for building the tree
    Args:
        im (dict): Dictionary representing the labels of images (id, labels)

    Returns:
        dict
    """
    js = loads(im)
    return {x['Name']: {y['Name'] for y in x['Parents']} for x in js['labels']}


def build_tree(json_dir):  # This function should be reviewed, but is not necessary for this project
    """
    Builds the tree, where each key is the label, and the values the set of parents
    Args:
        json_dir (str): Directory where jsons are stored

    Returns:
        dict: keys are labels, values are parents
    """
    bag = db.read_text(json_dir + "*")
    bag = bag.map(_parse).compute()
    
    name_parents = {}
    for im in bag:
        for k, v in im.items():
            if k not in name_parents:
                name_parents[k] = v
            else:
                name_parents[k] = v.union(name_parents[k])
    
    return name_parents


def inverse_tree(sorted_data):
    inversed_data = {}
    for l, p in sorted_data:
        p = list(p)
        if len(p) == 0:
            inversed_data[l] = {}
        if len(p):
            inversed_data[p[0]][l] = {}
        else:
            dict_ = inversed_data
            for i in range(len(p)):
                for j in range(len(p)):
                    if p[j] in dict_.keys():
                        dict_ = dict_[p[j]]
                        break
            dict_[l] = {}
    return inversed_data


def sort_tree(data):
    return sorted(data.items(), key=lambda x: len(x[1]))
