"""
Simulate cognito authorization by matching supplied token to existing OAuth subject (sub)
"""

from dataclasses import dataclass, asdict
import logging

@dataclass
class Claim:
    """
    Cognito JWT claim class
    """
    sub: str
    email: str

TOKENS: dict[str, Claim] = {
    'admin123': Claim(
        sub='11111111-1111-1111-1111-111111111111',
        email='admin@example.com'
    ),
    'user123': Claim(
        sub='22222222-2222-2222-2222-222222222222',
        email="user@example.com"
    )
}

def get_claim(headers: dict) -> Claim | None:
    """
    Given headers, decide whether a token should be used to look up an authorization claim
    or if instead claim is just passed through to the lambda.
    """

    token = headers.get('Authorization')

    if token is not None:
        token_clean = str(token).replace('Bearer ', '')
        if token_clean in TOKENS:
            logging.debug('Matched claim token to subject %s', TOKENS[token_clean].sub)
            return asdict(TOKENS[token_clean])

        logging.debug('No matching claim for token')
        return None

    # Otherwise, use subject and email to build a claim
    subject = headers.get('X-Cognito-Subject')
    email = headers.get('X-Cognito-Email')
    groups = headers.get('X-Cognito-Groups')

    if subject and email:
        return {
            'sub': subject,
            'email': email,
            'cognito:groups': groups
        }

    return None
