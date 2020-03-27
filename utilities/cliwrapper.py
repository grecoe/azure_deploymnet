import os
import json
import typing


class AzCliHelper:
    SUBSCRIPTION_SET = "az account set -s {}"
    GROUP_CREATE = "az group create -n {} -l {}"
    GROUP_DEPLOYMENT = "az group deployment create -n {} -g {} --template-file {}"
    GROUP_DEPLOYMENT_OUTPUT = "az group deployment show -g {} -n {}"
    GROUP_DEPLOYMENT_LIST = "az group deployment list -g {}"

    def __init__(self):
        pass
    
    @staticmethod
    def set_current_subscription(subscription_id : str) -> None:
        """
            Set a subscription as the default subscription for the 
            az cli so that downstream calls will affect this subscription.
        """
        if not len(subscription_id):
            raise Exception("set_current_subscription : Invalid parameters")

        actual_command = AzCliHelper.SUBSCRIPTION_SET.format(subscription_id)
        request_output = AzCliHelper._get_az_cli_output(actual_command, False)

    @staticmethod
    def create_resource_group(group_name : str, azure_region : str) -> bool:
        """
            Create an Azure Resource group in the current subscription in 
            the specified region. If the resource group already exists this
            call will succeed. 
        """
        if not len(group_name) or not len(azure_region):
            raise Exception("create_resource_group : Invalid parameters")

        return_value = False
        actual_command = AzCliHelper.GROUP_CREATE.format(group_name, azure_region)
        request_output = AzCliHelper._get_az_cli_output(actual_command)
        state = AzCliHelper._get_json_sub_object(request_output,["properties","provisioningState"])

        if state and state == "Succeeded":
            return_value = True

        return return_value

    @staticmethod
    def create_group_deployment(resource_group : str, deployment_name : str, arm_template_file : str, parameters_dictionary : dict = None) -> dict:
        """
            Create a deployment in the resource group
                resource_group  : Name of the resource group to deploy to
                deployment_name : The name associated with this deployment. It's
                                  important to note because this is the name
                                  that will be used when retrieving outputs. 
                arm_template    : File path to the Azure Resource Manager Template 
                                  (ARM) that will be used for the deployment.
                parameters_dictionary :
                                  Dictionary of parameters to pass into the template. 
                                  This parameter is optional only if your ARM template
                                  does not require parameters. If provided, the 
                                  parameters dictionary has the form
                                    {
                                        "parameter_name" : {
                                            "value" : expected_value
                                        }
                                    }

            Returns a dictionary with any outputs that were produced by the ARM
            template. If none, the dictionary will be empty. 
        """
        if not len(resource_group) or not len(deployment_name) or not len(arm_template_file):
            raise Exception("create_group_deployment : Invalid parameters")
        if not os.path.isfile(arm_template_file):
            raise Exception("create_group_deployment : Invalid template file")

        TEMP_PARAMETERS_FILE = "{}_params.json".format(deployment_name)

        # Create the base deployment request
        actual_command = AzCliHelper.GROUP_DEPLOYMENT.format(
            deployment_name,
            resource_group,
            arm_template_file)
        
        # If parameters are provided, create a file for them and append
        # to the command to issue.
        if parameters_dictionary:
            with open(TEMP_PARAMETERS_FILE, "+w") as params:
                params.write(json.dumps(parameters_dictionary, indent=4))
            
            actual_command += " --parameters @{}".format(TEMP_PARAMETERS_FILE)

        # Make the request
        request_output = AzCliHelper._get_az_cli_output(actual_command)

        # Clean up the parameters file
        if os.path.isfile(TEMP_PARAMETERS_FILE):
            os.remove(TEMP_PARAMETERS_FILE)

        # Now try and get the outputs
        outputs_dictionary = {}
        if request_output:
            outputs = AzCliHelper._get_json_sub_object(request_output, ["properties","outputs"]) 
            if outputs :
                for output_name in outputs.keys():
                    outputs_dictionary[output_name] = outputs[output_name]["value"]
            
        return outputs_dictionary

    @staticmethod
    def get_group_deployments(resource_group : str) -> list:
        """
            Get all deployments for a specific resource group
        """
        return_value = None

        actual_command = AzCliHelper.GROUP_DEPLOYMENT_LIST.format(resource_group)
        deploy_output = AzCliHelper._get_az_cli_output(actual_command)

        if deploy_output and isinstance(deploy_output, list):
            return_value = [x['name'] for x in deploy_output]

        return return_value

    @staticmethod
    def get_group_deployment_output(resource_group : str, deployment_name: str) -> dict:
        """
            Get deployment outputs for a specific deployment.
        """
        return_value = None

        actual_command = AzCliHelper.GROUP_DEPLOYMENT_OUTPUT.format(resource_group, deployment_name)
        deploy_output = AzCliHelper._get_az_cli_output(actual_command)

        if deploy_output:
            outputs = AzCliHelper._get_json_sub_object(deploy_output, ['properties', 'outputs'])
            if outputs:
                return_value = {}
                for key in outputs:
                    return_value[key] = outputs[key]['value']
 
        return return_value

    @staticmethod
    def _get_json_sub_object(json_object : json, sub_object_list : list):
        '''
            Step through a JSON object looking for a specific sub object. 

            If any of the paths in the list do not exist, return NONE...if
            you want better error handling, you should raise and Exception
            instead. 
        '''
        json_sub_obj = json_object
        for obj in sub_object_list:
            if obj in json_sub_obj.keys():
                json_sub_obj = json_sub_obj[obj]
            else:
                json_sub_obj = None
                break
        return json_sub_obj

    @staticmethod
    def _get_az_cli_output(command : str, as_json : bool = True):
        '''
            Call the azure CLI (or any command line call for that matter) and
            return the results. 

            If as_json is set, it will try to jsonify the result of the command
            line execution.
        '''
        return_value = None

        try:
            output = os.popen(command)
            return_value = output.read()

            if as_json:
                return_value = json.loads(return_value)
        except Exception as ex:
            print("Command Error : ", str(ex))

        return return_value

