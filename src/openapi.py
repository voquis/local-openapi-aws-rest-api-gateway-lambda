"""
Load openapi spec from disk and use it to find matching routes
"""

import logging
import os
import re
import yaml
from openapi_core import OpenAPI

def get_openapi():
    """
    Retrieve OpenAPI Spec from path on disk
    """
    openapi_file_path = os.environ.get('OPENAPI_FILE_PATH', '/openapi/openapi.yaml')
    logging.debug('Loading OpenAPI file from %s', openapi_file_path)

    openapi_dict = {}

    with open(openapi_file_path, 'r', encoding='utf-8') as openapi_file:
        openapi_dict = yaml.safe_load(openapi_file)

    base_url = os.environ.get('OPENAPI_BASE_URL')

    # Inject base URL to allow validation to succeed
    if base_url:
        servers = openapi_dict['servers']
        server_exists = False
        for server in servers:
            if server['url'] == base_url:
                server_exists = True
                break

        if not server_exists:
            logging.debug('Injecting base url into OpenAPI servers: %s', base_url)
            openapi_dict['servers'].append({
                'url': base_url,
                'description': 'Local REST API Gateway Base URL'
            })

    openapi = OpenAPI.from_dict(openapi_dict)
    return openapi


def get_resource_from_path(path: str):
    """
    Given a requested URL, attempts to find the matching resource route from OpenAPI spec
    """

    openapi_paths = list(get_openapi().spec['paths'].keys())
    openapi_paths.sort(key=len, reverse=True)
    regexes = [re.sub(r'{.*?}', r'.*?', openapi_path) for openapi_path in openapi_paths]
    logging.debug('Searching for path %s in OpenAPI spec', path)
    for regex in regexes:
        logging.debug('Checking for a match against %s', regex)

        # If there's an exact match, i.e. no substitution, return immediately
        if regex == path:
            logging.debug('Exact match found, returning')
            return path

        logging.debug('No exact match found, checking regex match for %s', regex)
        index = 0
        for regex in regexes:
            logging.debug('Checking regex %s', regex)
            if re.fullmatch(re.compile(regex), path):
                logging.debug('Matched regex %s for path %s', regex, path)
                return openapi_paths[index]
            index += 1

    logging.debug('No matches found against OpenAPI spec, using path %s', path)
    return path
