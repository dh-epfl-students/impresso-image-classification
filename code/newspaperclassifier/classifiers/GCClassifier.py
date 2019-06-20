"""
Classifier that uses the Google Cloud Vision API
"""
import json
from time import sleep

from google.api_core.exceptions import ResourceExhausted
from google.cloud import vision
from google.protobuf.json_format import MessageToJson

from newspaperclassifier.classifiers import ClassifierABC


class GCClassifier(ClassifierABC):
    
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
    
    def get_image_labels_from_bytes(self, content, retries=5):
        """
        Performs label detection via GCVision API for a byte array
        Args:
            content (bytes): The content of the image
            retries (int): Number of allowed retries in case of failure

        Returns:
            list[dict]: The labels, with their confidence and instances if applicable
        """
        
        num_tries = 1
        retry = True
        response = None
        
        while num_tries <= retries and retry:
            try:
                response = self.client.label_detection({'content': content})
                response = json.loads(MessageToJson(response))
                retry = False
            except ResourceExhausted as e:
                sleep(num_tries)
                num_tries += 1
        
        if response and 'labelAnnotations' in response:
            test = response['labelAnnotations']
            return test
        else:
            return []
