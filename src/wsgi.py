"""
Uses Werkzeug request and response wrappers
https://werkzeug.palletsprojects.com/en/3.0.x/wrappers/

Uses openapi-python integration for Werkzeug to compare against OpenAPI spec and extract resource
path, see:
https://openapi-core.readthedocs.io/en/stable/integrations/werkzeug.html

Sends payload to lambda function in format used by AWS REST API Gateway
https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

Assumes payload structure returned by lambda matches the expected format
https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
"""

import logging
from werkzeug.wrappers import Request, Response

from openapi_core.contrib.werkzeug import WerkzeugOpenAPIRequest
from src.openapi import get_openapi, get_resource_from_path
from src.lambda_function_proxy_integration import (
    LambdaFunctionProxyIntegration,
    LambdaFunctionProxyIntegrationRequest
)
from src.cognito import get_claim
from src.cors import OPTIONS_HEADERS

@Request.application
def application(request: Request):
    """
    WSGI application handler
    """

    # Handle options requests
    if request.method.lower() == 'options':
        return Response(
            status=200,
            headers=OPTIONS_HEADERS,
        )

    # Attempt to match API key to a Cognito user
    claim = get_claim(request.headers)

    # Validate the incoming request against the OpenAPI spec
    openapi_request = WerkzeugOpenAPIRequest(request)
    schema = get_openapi()
    try:
        schema.validate_request(openapi_request)
    except Exception as exception:
        logging.warning(exception)

    # Parse the incoming request and proxy to lambda function
    integration = LambdaFunctionProxyIntegration()
    proxy_response = integration.send(
        LambdaFunctionProxyIntegrationRequest(
            resource = get_resource_from_path(request.path),
            path=request.path,
            http_method=request.method,
            headers=dict((k, v) for k, v in request.headers),
            body=request.get_data().decode('utf-8'),
            path_parameters=openapi_request.parameters.path,
            query_string_parameters=openapi_request.parameters.query,
            request_context_authorizer_claims=claim
        )
    )

    if proxy_response:
        return Response(
            status=proxy_response.status_code,
            headers=proxy_response.headers,
            response=proxy_response.body
        )

    # Fallback if proxy request failed
    logging.warning('Invalid response received from Lambda, returning 502')
    return Response(
        status=502,
        headers={
            'Access-Control-Allow-Origin': '*'
        }
    )
