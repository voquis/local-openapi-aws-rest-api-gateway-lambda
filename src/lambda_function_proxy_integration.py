"""
Sends payload to lambda function in format used by AWS REST API Gateway
https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

Assumes payload structure returned by lambda matches the expected format
https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
"""

from base64 import urlsafe_b64decode
from dataclasses import dataclass
import logging
import os
import requests

@dataclass
class LambdaFunctionProxyIntegrationRequest:
    """
    Represents the payload sent to a lambda function via a proxy integration request
    """
    resource: str
    path: str
    http_method: str
    headers: dict | None = None
    multi_value_headers: dict | None = None
    query_string_parameters: dict | None = None
    multi_value_query_string_parameters: dict | None = None
    body: str | None = None
    is_base64_encoded: bool = False
    path_parameters: dict | None = None
    request_context_authorizer_claims: dict | None = None


    def get_payload(self):
        """
        Returns payload to send to lambda as a dict, that will eventually be sent as a JSON string.
        """
        payload = {
            "resource": self.resource,
            "path": self.path,
            "httpMethod": self.http_method,
            "headers": self.headers,
            "multiValueHeaders": self.multi_value_headers,
            "queryStringParameters": self.query_string_parameters,
            "multiValueQueryStringParameters": self.multi_value_query_string_parameters,
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "id",
                "authorizer": {
                    "claims": self.request_context_authorizer_claims,
                    "scopes": None
                },
                "domainName": "id.execute-api.us-east-1.amazonaws.com",
                "domainPrefix": "id",
                "extendedRequestId": "request-id",
                "httpMethod": "GET",
                "identity": {
                    "accessKey": None,
                    "accountId": None,
                    "caller": None,
                    "cognitoAuthenticationProvider": None,
                    "cognitoAuthenticationType": None,
                    "cognitoIdentityId": None,
                    "cognitoIdentityPoolId": None,
                    "principalOrgId": None,
                    "sourceIp": "IP",
                    "user": None,
                    "userAgent": "user-agent",
                    "userArn": None,
                    "clientCert": {
                        "clientCertPem": "CERT_CONTENT",
                        "subjectDN": "www.example.com",
                        "issuerDN": "Example issuer",
                        "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                        "validity": {
                            "notBefore": "May 28 12:30:02 2019 GMT",
                            "notAfter": "Aug  5 09:36:04 2021 GMT"
                        }
                    }
                },
                "path": self.path,
                "protocol": "HTTP/1.1",
                "requestId": "id=",
                "requestTime": "04/Mar/2020:19:15:17 +0000",
                "requestTimeEpoch": 1583349317135,
                "resourceId": None,
                "resourcePath": self.resource,
                "stage": "$default"
            },
            "pathParameters": self.path_parameters,
            "stageVariables": None,
            "body": self.body,
            "isBase64Encoded": self.is_base64_encoded
        }

        return payload


@dataclass
class LambdaFunctionProxyIntegrationResponse:
    """
    Represents the payload received from a lambda function as a proxy integration
    """
    is_base64_encoded: bool | None = None
    status_code: int | None = None
    headers: dict | None = None
    multi_value_headers: dict | None = None
    body: str | None = None


    def from_lambda_response(self, response: dict | None):
        """
        Build dataclass from dictionary
        """
        if response is None:
            return self

        self.is_base64_encoded = response.get('isBase64Encoded')
        self.status_code = response.get('statusCode', 502)
        self.headers = response.get('headers', {
            "Access-Control-Allow-Origin": "*"
        })
        self.multi_value_headers = response.get('multiValueHeaders')
        self.body = response.get('body')

        if self.is_base64_encoded:
            self.body = urlsafe_b64decode(self.body)

        if not self.body:
            self.body = response.get('errorMessage')

        return self


class LambdaFunctionProxyIntegration:
    """
    Represents a lambda function proxy integration, used to send and receive data to and from the
    proxy-integrated lambda function.
    """
    def send(
        self,
        request: LambdaFunctionProxyIntegrationRequest
    ) -> LambdaFunctionProxyIntegrationResponse | None:
        """
        Proxies an incoming request as a POST to the REST API lambda
        """

        payload = request.get_payload()
        logging.debug('Sending payload to lambda function')
        logging.debug(payload)

        # Prepare upstream Lambda URL
        lambda_hostname = os.environ.get('LAMBDA_HOSTNAME', 'rest-api-lambda')
        lambda_port = os.environ.get('LAMBDA_PORT', 8080)
        base_url = f'http://{lambda_hostname}:{lambda_port}'

        lambda_version = os.environ.get('LAMBDA_VERSION', '2015-03-31')
        url = f'{base_url}/{lambda_version}/functions/function/invocations'
        logging.debug('Using lambda URL: %s', url)

        response = None

        try:
            response = requests.post(
                url=url,
                json=payload,
                timeout=5
            )

            logging.debug('Received %s response from lambda function', response.status_code)
            logging.debug(response.text)
        except Exception as exception:
            logging.warning(exception)

        if response:
            logging.debug('Transforming lambda response to dataclass')
            output = LambdaFunctionProxyIntegrationResponse().from_lambda_response(
                response=response.json()
            )
            logging.debug(output)
            return output

        return response
