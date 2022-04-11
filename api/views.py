from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from access.models import AccessToken
from access.serializers import AccessTokenSerializer
from service.custom_auth import CustomUserAuthentication
from service.custom_viewsets import AUTH0ModelViewSet, CustomAPIView
from api.utils import (
    decipher_order, create_order, update_order,
    fetch_existing_order_for_update, fetch_job_statuses,
    cancel_order, decipher_order_for_update, get_product_url,
    list_all_product_urls
)


class OrderJobAPI(CustomAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (CustomUserAuthentication,)

    @staticmethod
    def create(request):
        data = request.data.get('order_data', {})
        order_details = decipher_order(data, request.auth)
        order_data = dict(
            organization=request.user.id,
            requested_by=request.auth.id,
            turn_around_hours=data.get('turn_around_hours', 72),
            idempotency_key=data.get('idempotency_key', None),
            order_details=order_details
        )
        order_response = create_order(order_data)
        return Response(data=order_response)

    @staticmethod
    def update(request, pk):
        data = request.data.get('order_data', {})
        order_details = decipher_order_for_update(data)

        if not order_details:
            return Response({"details": "No data submitted to update order"}, status=status.HTTP_400_BAD_REQUEST)

        target_order = fetch_existing_order_for_update(pk, request.user)
        if isinstance(target_order, str):
            return Response({"details": target_order}, status=status.HTTP_400_BAD_REQUEST)

        updated_order = update_order(target_order, order_details)
        return Response(data=updated_order, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def destroy(request, pk):
        success, results = cancel_order(pk, request.user)
        if success:
            return Response({"details": results}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"details": results}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def list(request):
        success, job_info = fetch_job_statuses(request.user)
        if success:
            return Response(job_info, status=status.HTTP_200_OK)
        else:
            return Response(job_info, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def retrieve(request, pk):
        success, job_info = fetch_job_statuses(request.user, pk)
        if success:
            return Response(job_info, status=status.HTTP_200_OK)
        else:
            return Response(job_info, status=status.HTTP_400_BAD_REQUEST)


class DownloadOutputProductAPI(CustomAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (CustomUserAuthentication,)

    @staticmethod
    def retrieve(request, pk):
        product_name = request.GET.get('product')
        success, results = get_product_url(pk, request.user, product_name)
        if success:
            return Response(results, status=status.HTTP_200_OK)
        else:
            return Response(results, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def list(request):
        results = list_all_product_urls(request.user)
        return Response(results)


class AccessTokenUserViewSet(AUTH0ModelViewSet):
    queryset = AccessToken.objects.all()
    serializer_class = AccessTokenSerializer
    lookup_field = 'access_token'
    scope_key = 'api-keys'
