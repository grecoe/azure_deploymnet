from utilities.cliwrapper import AzCliHelper
from utilities.deployment import CognitiveService, CognitiveServiceDeployment

'''
    Global fields you must change to be succesful. Provide your 
    own subscription ID, resource group name and an azure region
    such as 'eastus'. 
'''
SUBSCRIPTION_ID = 'YOUR_SUBSCRIPTION_ID'
RESOURCE_GROUP = 'YOUR_RESOURCE_GROUP_NAME'
RESOURCE_GROUP_REGION = 'eastus'

'''
    Provide specific information, mainly for COG_SERVICES_DEPLOY_TYPE
    to change between TextAnalytics and ComputerVision
'''
DEPLOY_COG_SERVICE = True
COG_SERVICES_DEPLOY_TYPE = CognitiveService.ComputerVision
COG_SERVICES_TEMPLATE_FILE = './arm_templates/cog-services-template.json'
COG_SERVICE_DEPLOYMENT_NAME = "comp_vis_deployment"
COG_SERVICE_NAME = "test_comp_vis"


'''
    Program Code:

    1. Set the current subscription
    2. Create/verify the resource group
    3. If DEPLOY_COMPUTER_VISION is
        True : Deploy the service to the specified resource group.
        False: Retrieve the outputs from an existing deployment

        In either case, the deployment outputs are dumped to the 
        console. 
'''
print("Set current subscription....")
AzCliHelper.set_current_subscription(SUBSCRIPTION_ID)

rg_created = AzCliHelper.create_resource_group(RESOURCE_GROUP, RESOURCE_GROUP_REGION)
print("Create resource group : ", RESOURCE_GROUP, '=', rg_created)

'''
    Deploy Computer Vision or just get the outputs
'''
deployment_outputs = None
if DEPLOY_COG_SERVICE:
    print("Deploying Cognitive Service...")
    deployment_details = CognitiveServiceDeployment(
            COG_SERVICES_DEPLOY_TYPE,
            COG_SERVICE_NAME,
            RESOURCE_GROUP_REGION
        )

    deployment_outputs = AzCliHelper.create_group_deployment(
                            RESOURCE_GROUP,
                            COG_SERVICE_DEPLOYMENT_NAME,
                            COG_SERVICES_TEMPLATE_FILE,
                            deployment_details.parameters
                         )

    print("Deployment Outputs:")
    print(deployment_outputs)
else:
    print("Get Cognitive Service Deployment Outputs")
    deployment_outputs = AzCliHelper.get_group_deployment_output(
                            RESOURCE_GROUP,
                            COG_SERVICE_DEPLOYMENT_NAME
                         )
    print("Deployment Outputs:")
    print(deployment_outputs)
