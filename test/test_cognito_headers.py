"""
Test extracting claims from tokens
"""

from src.cognito import get_claim

def test_cognito_groups_from_expected_token():
    """
    Given an expected bearer token, verify correct claim is returned
    """

    claim = get_claim({
        'Authorization': 'Bearer user123',
        'X-Cognito-Groups': 'role:1:abc, role:2:def',
    })

    assert claim == {
        'sub': '22222222-2222-2222-2222-222222222222',
        'email': 'user@example.com',
        'cognito:groups': 'role:1:abc, role:2:def'
    }


def test_cognito_groups_from_unexpected_token():
    """
    Given an unknown bearer token, verify correct claim is returned
    """

    claim = get_claim({
        'X-Cognito-Subject': '99999999-9999-9999-9999-999922222222',
        'X-Cognito-Email': 'unknown@example.com',
        'X-Cognito-Groups': 'role:1:xyz, role:2:xyz',
    })

    assert claim == {
        'sub': '99999999-9999-9999-9999-999922222222',
        'email': 'unknown@example.com',
        'cognito:groups': 'role:1:xyz, role:2:xyz'
    }
