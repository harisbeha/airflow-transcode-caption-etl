from access.serializers import UserSerializer
from rest_framework_jwt.utils import jwt_payload_handler


def jwt_custom_payload_handler(user):
    payload = jwt_payload_handler(user)
    payload = {
        'https://hasura.io/jwt/claims': {
            'x-hasura-allowed-roles': ['editor', 'user'],
            'x-hasura-default-role': 'user',
            'x-hasura-user-id': str(user.pk),
        }
    }

    return payload

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token
    }

import jwt 

def generate_hasura_token(user, service=None):
    private_signing_key = settings.JWT_RS256_PRIVATE_KEY
    hasura_payload = construct_hasura_payload()
    payload["https://hasura.io/jwt/claims"] = hasura_payload
    payload["https://hasura.io/jwt/claims"]["x-cirrus-ss-user-id"] = user.id
    hasura_token = jwt.encode(current_payload, private_signing_key, algorithm='RS256')
    return hasura_token

def get_legacy_enterprise_id():
    return 1

def get_legacy_ss_id():
    return 1

def get_cirrus_ss_id():
    return 1

def get_cirrus_enterprise_id():
    return 1

def construct_hasura_payload(**kwargs):
    hasura_payload = {
        "x-hasura-default-role": "user",
        "x-hasura-allowed-roles": [
            "user"
        ],
    }
    return hasura_payload