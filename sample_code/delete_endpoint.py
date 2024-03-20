import sagemaker
import boto3

sagemaker_client = boto3.client('sagemaker', region_name='us-west-2')

response = sagemaker_client.delete_endpoint(EndpointName = 'inference-endpoint-yi-34b-chat-1700644332')
print(response)
