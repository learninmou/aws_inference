import time
import sys
import datetime
import sagemaker
import boto3

timestr = '{}'.format(int(time.time()))
print(f'timestr={timestr}')

# 模型名称
TURING_MODEL_NAME = 'yi-vl-plus'
# TURING_MODEL_NAME = 'yi-34b-chat-200k-v01'

# 模型文件地址
MODEL_S3_URI = f's3://turing-infer-files/models/llava-34b_vary_0304_new_stage3-chat/'
# MODEL_S3_URI = f's3://turing-infer-files/models/Yi-34B-Chat-0205/'
# MODEL_S3_URI = f's3://turing-infer-files/models/Yi-34B-200K-v01-202403131800/'

# endpoint镜像地址
ENDPOINT_IMAGE_URI = f'601449239237.dkr.ecr.us-west-2.amazonaws.com/y-vl-inference:entrypoint_v0'

# 资源规格
INSTANCE_TYPE = 'ml.p4de.24xlarge'  # 8xA100(80GB)
# INSTANCE_TYPE = 'ml.p4d.24xlarge'
# INSTANCE_TYPE = 'ml.c5.large'

# 环境变量
TURING_TP_SIZE = 8
TURING_DP_SIZE = 1


ENDPOINT_MODEL_NAME = f'inference-model-{TURING_MODEL_NAME}-{timestr}'
ENDPOINT_CONFIG_NAME = f'inference-endpoint-config-{TURING_MODEL_NAME}-{timestr}'
ENDPOINT_NAME = f'inference-endpoint-{TURING_MODEL_NAME}-{timestr}'

sagemaker_client = boto3.client('sagemaker', region_name='us-west-2')

create_model_response = sagemaker_client.create_model(
    ModelName=ENDPOINT_MODEL_NAME,
    ExecutionRoleArn='arn:aws:iam::601449239237:role/SageMakerExecutionRole',
    PrimaryContainer={
        "Image": ENDPOINT_IMAGE_URI,
        "ModelDataSource": {
            "S3DataSource": {
                "S3Uri": MODEL_S3_URI,
                "S3DataType": "S3Prefix",
                "CompressionType": "None",
            },
        },
        "Environment": {
            "TURING_TP_SIZE": TURING_TP_SIZE,
            "TURING_DP_SIZE": TURING_DP_SIZE,
            "TURING_MODEL_NAME": TURING_MODEL_NAME,
        }
    },
    VpcConfig={
        'SecurityGroupIds': [
            'sg-0bc193e288856ba30',
        ],
        'Subnets': [
            'subnet-06bff51a2e6356317',
            'subnet-052f96a5d824a3b5b',
            'subnet-0b353894acd384fcd',
        ]
    },
)

create_endpoint_response = sagemaker_client.create_endpoint_config(
    EndpointConfigName=ENDPOINT_CONFIG_NAME,
    ProductionVariants=[{
        'VariantName': 'all',
        'ModelName': ENDPOINT_MODEL_NAME,
        'InstanceType': INSTANCE_TYPE,
        'InitialInstanceCount': 1,
        'ModelDataDownloadTimeoutInSeconds': 2400,
        'ContainerStartupHealthCheckTimeoutInSeconds': 800,
        'RoutingConfig': {
            'RoutingStrategy': 'LEAST_OUTSTANDING_REQUESTS',
        }
    }]
)

sagemaker_client.create_endpoint(
    EndpointName=ENDPOINT_NAME,
    EndpointConfigName=ENDPOINT_CONFIG_NAME,
)
