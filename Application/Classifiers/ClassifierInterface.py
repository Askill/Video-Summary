from abc import ABC, abstractmethod

class ClassifierInterface(ABC):
    @abstractmethod
    def tagLayer(self, layers):
        """takes filled contours of one frame, returns list (len(), same as input) 
        of lists with tags for corresponfing contours"""
        pass
