"""
Classifier that uses the Amazon Rekognition API
"""
import logging
from time import sleep

import boto3
from botocore.exceptions import ClientError

from newspaperclassifier.classifiers import ClassifierABC

FILE_LIMIT = 5242880  # AWS limits to 5MB images
THROUGHPUT_EXCEPTION = "ProvisionedThroughputExceededException"


class AwsClassifier(ClassifierABC):
    
    def __init__(self):
        self.client = boto3.client('rekognition')
    
    def get_image_labels_from_bytes(self, content, retries=5):
        """
        Performs label detection via Rekognition API for a byte array (less than 5MB)
        Args:
            content (bytes): The content of the image
            retries (int): Number of retries in case of Throughput limit

        Returns:
            list[dict]
        """
        if len(content) > FILE_LIMIT:
            logging.warning("Image exceeds file size limit of 5MB")
            return []
        
        num_tries = 1
        retry = True
        
        response = None
        while (num_tries <= retries) and retry:
            try:
                response = self.client.detect_labels(Image={'Bytes': content})
                retry = False
            except ClientError as e:
                if e.response['Error']['Code'] != THROUGHPUT_EXCEPTION:
                    print(f"Got error{e}")
                sleep(num_tries)
                num_tries += 1
        
        if num_tries >= retries and response is None:
            print(f"Could not get labels after {num_tries} retries")
        
        if response and 'Labels' in response:
            return response['Labels']
        else:
            return []
