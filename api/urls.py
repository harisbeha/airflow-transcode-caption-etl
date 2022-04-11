from django.urls import path

from rest_framework.routers import SimpleRouter
from api.views import OrderJobAPI, DownloadOutputProductAPI, AccessTokenUserViewSet

LIST_METHODS = ['get']
CREATE_METHODS = ['post', 'put']
UPDATE_METHODS = ['post', 'patch']
DELETE_METHODS = ['delete']

router = SimpleRouter()
router.register('access', AccessTokenUserViewSet)

urlpatterns = [
    path('order/', OrderJobAPI.as_view(http_method_names=LIST_METHODS+CREATE_METHODS), name='order'),
    path("order_job/", OrderJobAPI.as_view(http_method_names=CREATE_METHODS), name='order_job'),
    path("order/info/<slug:pk>", OrderJobAPI.as_view(http_method_names=LIST_METHODS), name='order_info'),
    path('order/update/<slug:pk>', OrderJobAPI.as_view(http_method_names=UPDATE_METHODS), name='update_order'),
    path('order/delete/<slug:pk>', OrderJobAPI.as_view(http_method_names=DELETE_METHODS), name='delete_order'),
  
    path('output/', DownloadOutputProductAPI.as_view(http_method_names=LIST_METHODS), name='list_output_products'),
    path('output/<slug:pk>', DownloadOutputProductAPI.as_view(http_method_names=LIST_METHODS), name='get_output_product'),
] + router.urls
