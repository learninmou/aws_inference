import sagemaker
import boto3

sagemaker_client = boto3.client('sagemaker')

response = sagemaker_client.delete_endpoint(EndpointName = 'inference-endpoint-yi-34b-chat-1700644332')
print(response)
