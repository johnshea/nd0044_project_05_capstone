from functools import wraps
from flask import Flask, jsonify, abort, request
import requests
from jose import jwt

AUTH0_DOMAIN = 'nd0044-project-05-capstone.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'restaurant'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    headers = request.headers
    if 'Authorization' not in headers:
        raise AuthError({
            "success": False,
            "error": 401,
            "message": "auth header not found"},
            401
        )
    else:
        auth_header = headers.get('Authorization')
        auth_info = auth_header.split()
        if len(auth_info) < 2:
            raise AuthError({
                "success": False,
                "error": 401,
                "message": "Authorization header length is not 2"},
                401
            )
        if auth_info[0].lower() != 'bearer':
            raise AuthError({
                "success": False,
                "error": 401,
                "message": "Bearer keyword not found Authorization header"},
                401
            )
        token = auth_header.split()[1]
        return token


def verify_decode_jwt(token):
    jsonurl = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = jsonurl.json()

    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception as e:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description':
                    'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            "success": False,
            "error": 400,
            "message": "Permissions key not found in JWT"},
            400
        )

    if permission not in payload['permissions']:
        raise AuthError({
            "success": False,
            "error": 403,
            "message": "Permission not found"},
            403
        )

    return True


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError as ae:
                abort(ae.status_code)

            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
