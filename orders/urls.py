from rest_framework.routers import SimpleRouter

from orders.views import OrderItemViewSet, OutputProductViewSet


router = SimpleRouter()
router.register('order_items', OrderItemViewSet)
router.register('output_product', OutputProductViewSet)

urlpatterns = router.urls
