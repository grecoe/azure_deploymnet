# Deploy Azure Cognitive Services via Azure CLI
<sub>Dan Grecoe - A Microsoft Employee</sub>

Creating an Azure Cognitive Service in your subscription can be done in several way. This example is using an Azure Resource Manager (ARM) Template to accomplish that goal. 

When using an ARM template your resource group gains a deployment object that identifies the activity. These are not available when creating services through the Azure Portal.

Using ARM template outputs in downstream code is widely used for many different reason. 

In this code, you can create a Computer Vision or Text Analytics Cognitive Service. The outputs will the service API key and service URL. These values can then be retrieved programatically at any time. 

## Prerequisites
- Azure Subscription
- Machine with Python 3.6 or later
- Azure CLI installed (locally or in conda environment)

