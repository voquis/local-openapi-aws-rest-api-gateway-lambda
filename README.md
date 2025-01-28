# Local AWS REST API gateway defined by OpenAPI Spec with lambda integration

Simulate a REST API gateway integrated with a single lambda via an OpenAPI spec

## Usage
### Direct

```sh
docker run \
  -p 4321:8080 \
  -p 4322:5678 \
  voquis/local-openapi-aws-rest-api-gateway-lambda
```

Gateway will be available on http://127.0.0.1:4321
