from django.urls import path, include
from rest_framework.routers import SimpleRouter
from access.views import AccessTokenViewSet, AccountConfigViewSet, create_auth0_user

router = SimpleRouter()
router.register('account_config', AccountConfigViewSet)
router.register('access', AccessTokenViewSet)

urlpatterns = [
    path('create-auth0-user/', create_auth0_user),
]
urlpatterns += router.urls
