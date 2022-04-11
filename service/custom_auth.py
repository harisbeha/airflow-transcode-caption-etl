from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from jose import jwt, exceptions as jwt_exceptions

from access.models import AccessToken
from orgs.models import Organization


def strip_bearer_token(auth_token):
    """
    Strips Bearer token from the header
    :param auth_token:
    :return:
    """
    if not isinstance(auth_token, str):
        auth_token = auth_token.decode('utf-8')
    prefix = 'Bearer '
    if not auth_token.startswith(prefix):
        return None
    return auth_token[len(prefix):]


class CustomAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_header = strip_bearer_token(authentication.get_authorization_header(request))
        valid_bearer_token = settings.MICROSERVICE_API_OVERRIDE_KEY
        if auth_header != valid_bearer_token:
            raise exceptions.AuthenticationFailed("Unauthorized Request")

        return AnonymousUser, True


class CustomUserAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_header = strip_bearer_token(authentication.get_authorization_header(request))
        try:
            access_token = AccessToken.objects.get(access_token=auth_header)
        except AccessToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Unauthorized Request")

        if not access_token.is_active:
            raise exceptions.AuthenticationFailed("This Access Key has been deactivated. Contact your Account Manager")

        return access_token.member.organization, access_token.member


class Auth0Authorization(authentication.BaseAuthentication):

    @staticmethod
    def _decode_jwt_token(token):
        try:
            return jwt.decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHMS, audience=settings.JWT_AUDIENCE)
        except jwt_exceptions.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("JWT SIGNATURE EXPIRED")
        except jwt_exceptions.JWTError as e:
            if settings.DEBUG:
                raise exceptions.AuthenticationFailed(str(e))
            raise exceptions.AuthenticationFailed("INVALID JWT")

    @staticmethod
    def _fetch_organization(payload):
        org_id = payload.get('org_id')
        if not org_id:
            raise exceptions.AuthenticationFailed("Missing Org ID")
        try:
            organization = Organization.objects.get(org_id=org_id)
        except Organization.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid User Credentials")
        return organization

    @staticmethod
    def _fetch_scope(payload):
        return payload.get('scope')

    def authenticate(self, request):
        token = strip_bearer_token(authentication.get_authorization_header(request))
        if not token:
            raise exceptions.AuthenticationFailed("Unauthorized Request")
        payload = self._decode_jwt_token(token)
        return self._fetch_organization(payload), self._fetch_scope(payload)
