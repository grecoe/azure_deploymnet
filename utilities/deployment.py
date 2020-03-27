import typing
from enum import Enum


class CognitiveService(Enum):
     ComputerVision = 'ComputerVision'
     TextAnalytics = 'TextAnalytics'

class CognitiveServiceDeployment:
    def __init__(self, cognitive_service : CognitiveService, service_name : str, azure_region : str, sku : str = 'S1'):
        self.parameters = {}
        self.add_parameter('name', service_name)
        self.add_parameter('location', azure_region)
        self.add_parameter('svcKind', cognitive_service.value)
        self.add_parameter('sku', sku)

    def add_parameter(self, name : str, value : object):
        self.parameters[name] = { "value" : value}
