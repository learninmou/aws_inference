import json
import boto3

sess = boto3.session.Session()

client = sess.client('sagemaker-runtime',
        region_name = 'us-west-2',
        aws_access_key_id='',
        aws_secret_access_key='',
        )

request_body = {
    "model": "yi-34b-chat-v08",
    "messages": [
        {
            "role": "user",
            "content": "Hello, what is your name ?"
        }
    ],
    "stream": True,
    "max_tokens": 100,
}
payload_json = json.dumps(request_body)

print(f'request_body={request_body}')

response = client.invoke_endpoint_with_response_stream(
    EndpointName='test-endpoint-1700452460',
    Body=payload_json,
    ContentType='application/json',
)

print(f'response={response}')

event_stream = response['Body']

for event in event_stream:
    content = event['PayloadPart']['Bytes'].decode('utf-8')
    print(f'content={content}')
