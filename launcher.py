import logging
import uvicorn
import httpx
import boto3
import json
import time
import os
from httpx import Client, AsyncClient, URL
from fastapi import FastAPI, Request, status
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
from starlette.background import BackgroundTask
from fastapi.encoders import jsonable_encoder
from config import lazy_readconfig

logger = logging.getLogger(__name__)
app = FastAPI()

# TODO
# avoid hardcode
_VALID_AUTH = [
    'Bearer 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',
    'Bearer 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',
]
_INVALID_RESPONSE = JSONResponse(
        status_code = status.HTTP_403_FORBIDDEN,
        content=jsonable_encoder({"detail": "invalid authorization", "Error": "REQUEST FORBIDDEN"}),
    )
def _check_auth(request : Request):
    auth_value = request.headers.get('Authorization')
    if auth_value is None or auth_value not in _VALID_AUTH:
        return False
    
    # TODO : remove authorization in header
    return True

_request_index = 0
def _fetch_endpoint(target_model : str):
    if not target_model:
        return ''
    target_model = target_model.lower()
    cadidates = lazy_readconfig(os.environ['ENV_AWS_ENDPOINTS_FILE'])
    valid_endpoints = []
    for cadidate in cadidates:
        model, endpoint = cadidate.split(' ')
        if model.lower() == target_model:
            valid_endpoints.append(endpoint)

    length = len(valid_endpoints)
    if length <= 0:
        return ''

    global _request_index
    result = valid_endpoints[_request_index % length]
    # TODO : coroutine safe
    _request_index += 1
    return result

@app.on_event('startup')
def startup_service():
    logger.info('service startup')
    # init config dict
    lazy_readconfig(os.environ['ENV_AWS_ENDPOINTS_FILE'])

@app.on_event('shutdown')
def shutdown_service():
    logger.info('service shutdown')

@app.post("/v1/chat/completions")
async def create_chat_completions(request : Request):
    if not _check_auth(request):
        return _INVALID_RESPONSE

    sess = boto3.session.Session()
    client = sess.client('sagemaker-runtime',
            region_name = 'us-west-2',
            aws_access_key_id=os.environ['ENV_AWS_AK'],
            aws_secret_access_key=os.environ['ENV_AWS_SK'],
            )
    body = await request.json()
    streaming = True if body.get('stream') else False

    model = body.get('model')
    endpoint = _fetch_endpoint(model)
    if not endpoint:
        return JSONResponse(status_code = status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder({'ERROR': 'no valid endpoint for target model'}))

    payload_json = json.dumps(body)

    if streaming:
        response = client.invoke_endpoint_with_response_stream(
                EndpointName = endpoint,
                Body = payload_json,
                ContentType = 'application/json')

        async def fetch_streaming_response():
            event_stream = response['Body']
            for event in event_stream:
                content = event['PayloadPart']['Bytes'].decode('utf-8')
                yield content

        async def release_resources():
            client.close()

        return StreamingResponse(
            fetch_streaming_response(),
            media_type = "text/event-stream",
            background = BackgroundTask(release_resources),
            )
    else:
        response = client.invoke_endpoint(
                EndpointName = endpoint,
                Body = payload_json,
                ContentType = 'application/json')

        json_str = response['Body'].read().decode('utf-8')
        return JSONResponse(content = json.loads(json_str))
        
@app.get('/check_health')
def check_health():
    return 'OK'

def set_logger():
    log_dir = os.environ['ENV_LOG_DIR']
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level = logging.INFO,
        format = '[TURING]-[%(asctime)s]-[%(levelname)s]-[%(filename)s:%(lineno)d] : %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        handlers = [
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(os.path.join(log_dir, 'serving-{}.log'.format(os.getpid())),
                mode = 'a',
                maxBytes = 16 * 1024 * 1024,
                backupCount = 32)
        ]
        )
set_logger()

if __name__ == '__main__':
    uvicorn.run(
            app,
            host = '0.0.0.0',
            port = 8080,
            log_level = 'info',
            limit_concurrency = 1000,
            timeout_keep_alive = 60,
            )
