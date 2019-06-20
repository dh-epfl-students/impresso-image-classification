"""
Classifier Abstract Base Class
"""
from abc import ABC, abstractmethod

from newspaperclassifier.deprecated.impresso_iiif import get_image_content_from_url


class ClassifierABC(ABC):
    
    @abstractmethod
    def get_image_labels_from_bytes(self, content):
        pass
    
    def get_image_labels_local(self, filename):
        """
        Performs labelisation of local image
        Args:
            filename:

        Returns:

        """
        with open(filename, 'rb') as image:
            content = image.read()
            return self.get_image_labels_from_bytes(content)
    
    def get_image_labels_iiif(self, url):
        content = get_image_content_from_url(url)
        
        return self.get_image_labels_from_bytes(content)
