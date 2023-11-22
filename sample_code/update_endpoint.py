import sagemaker
import boto3

sagemaker_client = boto3.client('sagemaker')

response = sagemaker_client.update_endpoint(
        EndpointName = 'inference-endpoint-yi-34b-chat-1700549343',
        EndpointConfigName = 'inference-endpoint-config-yi-34b-chat-1700644332',
        )
print(response)

