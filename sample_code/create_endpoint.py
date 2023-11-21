import time
import sys
import datetime
import sagemaker
import boto3

timestr = '{}'.format(int(time.time()))
print(f'timestr={timestr}')

sess = sagemaker.Session()
sagemaker_client = boto3.client('sagemaker')

model_name = f'inference-model-yi-34b-chat-{timestr}'
instance_type = 'ml.p4de.24xlarge'
#instance_type = 'ml.p4d.24xlarge'
#instance_type = 'ml.c5.large'

create_model_response = sagemaker_client.create_model(
    ModelName = model_name,
    ExecutionRoleArn = 'arn:aws:iam::601449239237:role/SageMakerExecutionRole',
    PrimaryContainer = {
        "Image": "601449239237.dkr.ecr.us-west-2.amazonaws.com/turing_serving_infra:entrypoint_0.0.4",
        "ModelDataSource": {
            "S3DataSource": {
                "S3Uri": f's3://turing-infer-files/models/yi-34b-sft-v08/',
                "S3DataType": "S3Prefix",
                "CompressionType": "None",
            },
        },
        "Environment": {
            "TP_SIZE": "2",
            "DP_SIZE": "4",
            "TURING_MODEL_NAME": "Yi-34B-Chat",
        }
    },
    VpcConfig= {
        'SecurityGroupIds': [
            'sg-0bc193e288856ba30',
        ],
        'Subnets': [
            'subnet-06bff51a2e6356317',
            'subnet-052f96a5d824a3b5b',
        ]
    },
)

create_endpoint_response = sagemaker_client.create_endpoint_config(
    EndpointConfigName = f'inference-endpoint-config-yi-34b-chat-{timestr}',
    ProductionVariants = [{
        'VariantName': 'all',
        'ModelName': model_name,
        'InstanceType': instance_type,
        'InitialInstanceCount': 1,
    }]
)

endpoint_name = f'inference-endpoint-yi-34b-chat-{timestr}'
sagemaker_client.create_endpoint(
    EndpointName = endpoint_name,
    EndpointConfigName = f'inference-endpoint-config-yi-34b-chat-{timestr}',
)
