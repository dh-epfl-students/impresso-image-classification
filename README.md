# Classification of Impresso Image database

This project aims at building a pipeline that would allow the classification of the Impresso database of newspaper images.
The research and development has been done by Edoardo Tarek Hölzl and Lucas Gauchoux

## Introduction
The Impresso project is a very ambitious initiative to digitize, analyze and extract information from databases of newspapers.
As one would figure, this kind of media contains large quantities of images, ranging from crossword puzzles, to portraits,
war photos, historical events and any other kind of images from cities' day to day lives. 

After having scanned all the issues of a certain newspaper, it seems quite straightforward to treat the gathered information, 
as it could be very useful for historical research. However, to this point, images have not been explored or analyzed, and it is believed that
they could become very beneficial to historical research, if presented in the right way.

This project's aim is to first explore the huge database of images, classify them using API calls to Google Cloud Vision and AWS Rekognition,
evaluate the found labels using an additional tool, and provide a way of searching through the currently non indexed database.

The code in this project allows the classification, cleaning, evaluating and storing the results onto the Impresso S3 server.

## Research Summary

Initially, the project started as an exploration, as to assess the performance of multiple models (pre-trained), and other APIs
that work more like black boxes.

We first tried using pre-trained models, that are open source and for which we know the architecture and the number of labels:
- **OpenCV**: The trained models are very basic and only allow the identification of one entity (face, person). This option was ruled out quite early in the project
- **Faster-RCNN**:  Another pre-trained model, with 600 categories. It initially worked fine on test images (not from Impresso), but when used on scanned newspaper images,
the results were very poor. An example of that can be seen in the figure below. As we can see, there are only a few detected labels,
and this image is still considered a very good quality compared to what is present in Impresso.

![](./images/faster_rcnn_1.jpeg)

- **Mask-RCNN**: Essentially, this is an extension of Faster-RCNN, in the sense that it outputs also a mask https://news.sbb.ch/fr/article/87237/le-nouvel-abonnement-seven25-remplace-la-voie-7or the detected object.
However, this model only had 80 images, and was trained on the COCO dataset. We thought about extending the number of labels by re-training 
with OpenImage, but this would require us to perform segmentation on the images. This is the reason this model was ruled out.

- **AWS Rekognition**: This one is an API, with a deep network actinng as a black-box; we do not know the total number of labels, as it keeps increasing,
and we do not know anything about the architecture of the model. However, the performance provided was impressively good. The quality of labels given was beyond what we expected.
On the 80,000 images we classified, this API returned 2150 distinct labels, some of which aren't useful, but we believe that keeping all of them enriches more the dataset.

- **GC Vision**: This API is offered by Google, and is very similar to Rekognition, in the sense that it is also a black-box, and we do not know their model. However, its performance
is quite similar to Rekognition, and the set of labels we found had some overlap with it (3555 labels with 1013 common). Also, for a substantial amount of images,
both APIs were kind of complementary: when one of them made a mistake in the classification, the other was more accurate.

## Installation & usage

- **Dependencies**: The code depends on a few libraries that are automatically installed when installing the package. However, some keys have to be set as enviroment variables.

- **Access Keys**: The access keys for SwitchEngine need to be set in order to read and write to the S3. One needs to set `SE_ACCESS_KEY` and `SE_SECRET_KEY`.

- **AWS credentials**:  The credentials need to be stored in `~/.aws/credentials`. One needs to have `aws_access_key` and `aws_secret_access_key`

- **GC credentials**: These credentials should be downloaded from the GC console as a `JSON` file. The `GOOGLE_APPLICATION_CREDENTIALS` environment variables needs to point to this `JSON` file.

- **SOLR credentials**: To access the SOLR API, the `SOLR_PASS` env variable should be set

We recommend installing this package within an isolated environment. Installation is done using the command:

```shell
pip install .
```

After that, all the scripts should be accessible through CLI

**Usage**: There are 5 different scripts attached to this package:

- Classifying images: The script has the following signature, and classifies images stored on `s3://impresso-images/images-packed/`. The results are stored in the specified directory.
```angular2
impresso_classify --client [aws | gc] --destination <dir> -b [batch_mode]
```

- Merging the image labels: This should be done after the classification has been done on both APIs. It reads in from two specified directories (AWS and GC) and outputs on `csv` file. The signature is as follows:
```angular2
imresso_merge_labels --aws-dir <dir> --gc-dir <dir> --destination <file>
```

- Dumping the labels: To dump the labels onto an endpoint, one should use the following script. If the endpoint and bucket arguments are omitted, the script will dump on `s3://impresso-image-labels/`.

```angular2
dump_labels --merged <file> --endpoint <url> --bucket <url> --bar [show progress bar]
```

- Evaluation of labels: Before evaluating, the N similar images need to be queried from `REPLICA`. For that, one can use the following script
```angular2
impresso_replica --merged-file <file> --destination <file> -n <int> --bar [progess bar]
```

After that, the evaluation script can be run:

```angular2
evaluate_labels --merged <file> --similar-images <file> --destination <file> --min-score <int> --bar [progres bar]
```
The results will be dumped in the specified `csv` file.

## License

MIT License

Copyright (c) 2019 Edoardo Hölzl, Lucas Gauchoux

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

