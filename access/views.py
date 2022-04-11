from access.models import AccessToken, AccountConfiguration
from access.serializers import AccountConfigurationSerializer, AccessTokenSerializer, UserSerializer
from service.custom_viewsets import CustomModelViewSet, AUTH0ModelViewSet
from service.custom_auth import Auth0Authorization, CustomAuthentication

# from django.http import Http404
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import Response, status

from service.enums import APIKeyErrorCodes


# Only to be used when passing in queryset = Model.objects.none()
# class CustomModelViewSet(ModelViewSet):
#     model = None
#     filter_key = 'id'
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object_direct(kwargs['pk'])
#         self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def get_object_direct(self, pk):
#         """
#         Uses a secondary call to ignore self.queryset
#         :param pk: whatever is used as the primary key value (or custom field)
#         :return:
#         """
#         filter_kwargs = {self.filter_key: pk}
#         obj = self.model.objects.filter(**filter_kwargs).first()
#         if not obj:
#             raise Http404
#         self.check_object_permissions(self.request, obj)
#         return obj
#
#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object_direct(kwargs['pk'])
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
#
#     def get_object(self):
#         return super(CustomModelViewSet, self).get_object()
#
#     def perform_authentication(self, request):
#         super(CustomModelViewSet, self).perform_authentication(request) and request.auth


# class AUTH0ModelViewSet(ModelViewSet):
#     scope_key = ""
#     authentication_classes = [Auth0Authorization]
#
#     def perform_destroy(self, instance):
#         """
#         Added soft delete functionality to this endpoint
#         :param instance:
#         :return:
#         """
#         if hasattr(instance, 'is_active'):
#             instance.is_active = False
#             instance.save()
#         elif hasattr(instance, 'deleted'):
#             instance.deleted = True
#             instance.save()
#         else:
#             super(AUTH0ModelViewSet, self).perform_destroy(instance)
#
#     def destroy(self, request, *args, **kwargs):
#         if "disable:{}".format(self.scope_key) not in request.auth:
#             return Response({"Message": APIKeyErrorCodes.DISABLE.value}, status=status.HTTP_401_UNAUTHORIZED)
#
#         instance = self.get_object()
#         if request.user.id != instance.organization_id:
#             return Response({"Message": "Invalid Organization ID"}, status=status.HTTP_400_BAD_REQUEST)
#
#         self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def list(self, request, *args, **kwargs):
#         if "list:{}".format(self.scope_key) not in request.auth:
#             return Response({"Message": APIKeyErrorCodes.LIST.value}, status=status.HTTP_401_UNAUTHORIZED)
#
#         self.queryset = self.queryset.filter(organization=request.user)
#         return super(AUTH0ModelViewSet, self).list(request, *args, **kwargs)
#
#     def create(self, request, *args, **kwargs):
#         if "create:{}".format(self.scope_key) not in request.auth:
#             return Response({"Message": APIKeyErrorCodes.CREATE.value}, status=status.HTTP_401_UNAUTHORIZED)
#
#         # Ensure that the organization_id in the application/json field "organization" matches the requesting org_id
#         if request.user.id != request.data['organization']:
#             return Response({"Message": "Invalid Organization ID"}, status=status.HTTP_400_BAD_REQUEST)
#
#         return super(AUTH0ModelViewSet, self).create(request, *args, **kwargs)
#
#     def retrieve(self, request, *args, **kwargs):
#         if "get:{}".format(self.scope_key) not in request.auth:
#             return Response({"Message": APIKeyErrorCodes.GET.value}, status=status.HTTP_401_UNAUTHORIZED)
#
#         instance = self.get_object()
#         if request.user.id != instance.organization_id:
#             return Response({"Message": "Invalid Organization ID"}, status=status.HTTP_400_BAD_REQUEST)
#
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
#

class AccountConfigViewSet(CustomModelViewSet):
    queryset = AccountConfiguration.objects.none()
    model = AccountConfiguration
    serializer_class = AccountConfigurationSerializer
    authentication_classes = [CustomAuthentication]


class AccessTokenViewSet(AUTH0ModelViewSet):
    filter_key = 'access_token'
    model = AccessToken
    queryset = AccessToken.objects.all()
    serializer_class = AccessTokenSerializer
    # authentication_classes = [CustomAuthentication]
    lookup_field = 'access_token'
    scope_key = 'api-keys'


def create_auth0_user(request):
    try:
        email = request.data.get("email", "")
        u = User(email=email)
        u.set_unusable_password()
        u.save()
        return Response(status=201)
    except Exception as e:
        return Response(status=400)

# class UserListView(generics.ListCreateAPIView):
#     queryset = models.CustomUser.objects.all()
#     serializer_class = serializers.UserSerializer