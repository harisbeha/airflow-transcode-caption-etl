from django.http import Http404
from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import Response, status, APIView
import uuid

from service.custom_auth import Auth0Authorization
from service.enums import APIKeyErrorCodes


def generic_view_exception_handling(exception_object):
    # TODO: edit this line below with the code to fetch the sentry log ID
    sentry_code = uuid.uuid4()
    if settings.DEBUG:
        res = Response(data={"details": str(exception_object)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        error_message = "Error has been logged {} contact support with this ID".format(sentry_code)
        res = Response(
            data={"Error": error_message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return res


# Only to be used when passing in queryset = Model.objects.none()
class CustomModelViewSet(ModelViewSet):
    model = None
    filter_key = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object_direct(kwargs['pk'])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object_direct(self, pk):
        """
        Uses a secondary call to ignore self.queryset
        :param pk: whatever is used as the primary key value (or custom field)
        :return:
        """
        filter_kwargs = {self.filter_key: pk}
        obj = self.model.objects.filter(**filter_kwargs).first()
        if not obj:
            raise Http404
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object_direct(kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        return super(CustomModelViewSet, self).get_object()

    def perform_authentication(self, request):
        super(CustomModelViewSet, self).perform_authentication(request) and request.auth


class AUTH0ModelViewSet(ModelViewSet):
    scope_key = ""
    filter_key_name = "member__organization_id"
    authentication_classes = [Auth0Authorization]

    def perform_destroy(self, instance):
        """
        Added soft delete functionality to this endpoint
        :param instance:
        :return:
        """
        if hasattr(instance, 'is_active'):
            instance.is_active = False
            instance.save()
        elif hasattr(instance, 'deleted'):
            instance.deleted = True
            instance.save()
        else:
            super(AUTH0ModelViewSet, self).perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        if "disable:{}".format(self.scope_key) not in request.auth:
            return Response({"Message": APIKeyErrorCodes.DISABLE.value}, status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        if instance.member_id not in request.user.org_users.all().values_list('id', flat=True):
            return Response({"Message": "Invalid Organization ID"}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        if "list:{}".format(self.scope_key) not in request.auth:
            return Response({"Message": APIKeyErrorCodes.LIST.value}, status=status.HTTP_401_UNAUTHORIZED)
        filter_kwargs = {self.filter_key_name: request.user.id}
        self.queryset = self.queryset.filter(**filter_kwargs)
        return super(AUTH0ModelViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if "create:{}".format(self.scope_key) not in request.auth:
            return Response({"Message": APIKeyErrorCodes.CREATE.value}, status=status.HTTP_401_UNAUTHORIZED)

        if request.data.get('member') not in request.user.org_users.all().values_list('id', flat=True):
            return Response({"Message": "Can only create tokens for members in the same organization"}, status=status.HTTP_403_FORBIDDEN)

        return super(AUTH0ModelViewSet, self).create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if "get:{}".format(self.scope_key) not in request.auth:
            return Response({"Message": APIKeyErrorCodes.GET.value}, status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        if request.user.id != instance.organization_id:
            return Response({"Message": "Invalid Organization ID"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CustomAPIView(APIView):

    def get(self, request, **kwargs):
        try:
            if kwargs.get('pk'):
                return self.retrieve(request, kwargs['pk'])
            else:
                return self.list(request)
        except Exception as e:
            return generic_view_exception_handling(e)

    def post(self, request, **kwargs):
        try:
            if kwargs.get('pk'):
                return self.update(request, kwargs['pk'])
            else:
                return self.create(request)
        except Exception as e:
            return generic_view_exception_handling(e)

    def patch(self, request, **kwargs):
        primary_key_index = kwargs.get('pk')
        if not primary_key_index:
            return Response({"details": "Missing ID"}, status=status.HTTP_400_BAD_REQUEST)
        return self.update(request, primary_key_index)

    def delete(self, request, **kwargs):
        primary_key_index = kwargs.get('pk')
        if not primary_key_index:
            return Response({"details": "Missing ID"}, status=status.HTTP_400_BAD_REQUEST)
        return self.destroy(request, primary_key_index)

    def put(self, request, **kwargs):
        return self.post(request, **kwargs)

    @staticmethod
    def create(request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @staticmethod
    def update(request, pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @staticmethod
    def destroy(request, pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @staticmethod
    def list(request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @staticmethod
    def retrieve(request, pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
