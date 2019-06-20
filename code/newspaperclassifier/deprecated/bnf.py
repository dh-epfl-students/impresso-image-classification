import os
from json import loads
from urllib.request import urlretrieve

URL = "https://gallica.bnf.fr/iiif/ark:/12148/{id}/f{page}/full/full/0/native.jpg"

id_file_name = "/Test_images_bnf_id.txt"
id_dir = os.path.abspath('../Data/ImagesID/BNFID')
data_dir = os.path.abspath('../../Data/BNF_json/IMAGES/Images-dnnDF')
dest_dir = os.path.abspath('../../Data/BNF_images')

print("Reading image information from {}, Downloading to {}".format(data_dir, dest_dir))

NUM_IMAGES = 100


def find_id(data):
    for i, x in enumerate(data):
        if type(x) == list and len(x) == 2 and x[0] == 'ID':
            return x[1]
        elif type(x) == list:
            ret = find_id(x)
            if ret is not None:
                return ret


def find_order(data):
    for i, x in enumerate(data):
        if type(x) == list and len(x) >= 2 and x[0] == 'page':
            return x[1]['ordre']
        elif type(x) == list:
            ret = find_order(x)
            if ret is not None:
                return ret


def construct_url(image_id, order):
    return URL.format(id=image_id, page=order)


id_file = open(id_dir + id_file_name)
for id_ in id_file.readlines():
    id_ = id_.strip()
    if id_.endswith('.xml'):
        f = open(os.path.join(data_dir, id_))
        lines = f.read()
        data = loads(lines)
        
        url = construct_url(find_id(data), find_order(data))
        urlretrieve(url, os.path.join(dest_dir, id_[:-4] + ".jpg"))
