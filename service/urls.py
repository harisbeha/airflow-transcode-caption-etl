"""microservices URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from service import views
from frontend.views import get_publishable_key, create_setup_intent, pay, set_default_payment_method, webhook_received
from integrations.zoom import views as zoom_views
from integrations.youtube import views as youtube_views
import notifications.urls

urlpatterns = [
    path('', views.index, name='index'),
    path('library', views.library, name='library'),
    path('plans', views.plans, name='plans'),
    path('orders', views.orders, name='orders'),
    path('cart-preview', views.cart_preview, name='cart'),
    path('cart/remove/<order_uuid>', views.remove_item_from_cart, name='remove_item_from_cart'),
    path('payment-confirmation/<payment_id>', views.payment_confirmation, name='payment_confirmation'),
    path('pay', pay, name='pay'),
    path('stripe_webhook', views.payment_webhook_received, name='stripe_webhook'),
    path('add-card', views.add_card, name='add_card'),
    path('public-key', get_publishable_key, name='get_publishable_key'),
    path('create-setup-intent', create_setup_intent, name='create_setup_intent'),
    path('set-default/<payment_method_id>', set_default_payment_method, name='set_default_payment_method'),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('api-keys', views.api_keys, name='api_keys'),
    path('media/detail/<entry_id>', views.job_detail, name='job_detail'),
    path('media/data/vtt/<order_uuid>', views.download_vtt, name='download_vtt'),
    path('integrations', views.integrations, name='integration'),
    path('integrations/', include([
        path('zoom/', include([
            path('oauth', zoom_views.zoom_api, name='zoom_api'),
            path('is_logged', zoom_views.is_logged_zoom, name='is_logged_zoom'),
            path('deactivate', zoom_views.deactivate_zoom, name='deactivate_zoom'),
            # path('feed_type/', youtube_views.feed_type, name="feed_type"),
            path('settings', zoom_views.zoom_settings, name="zoom_settings"),
            path('import', zoom_views.zoom_import, name="zoom_import")
        ])),
        path('youtube/', include([
            path('settings/', youtube_views.youtube_settings, name="youtube_settings"),
            path('import/', youtube_views.youtube_import, name="youtube_import"),
            path('feed_type/', youtube_views.feed_type, name="feed_type"),
            path('authorize/', youtube_views.auth_youtube, name='authorize'),
            path('oauth2callback/', youtube_views.oauth2cb,
                name='oauth2callback')
        ])),
    ])),

    path('cookies', views.cookies, name='cookies'),
    path('privacy', views.privacy, name='privacy'),
    path('terms', views.terms, name='terms'),

    path('bulk-import', views.bulk_import, name='bulk-import'),
    path('order', views.order, name='order'),
    path('order-realtime', views.order_realtime, name='order_realtime'),
    path('team', views.team, name='team'),
    path('user-settings', views.user_settings, name='user_settings'),
    path("presets/", views.PresetListView.as_view(), name="orders_Preset_list"),
    path("create-preset/", views.PresetCreateView.as_view(), name="orders_Preset_create"),
    path("preset-detail/<int:pk>/", views.PresetDetailView.as_view(), name="orders_Preset_detail"),
    path("update-preset/<int:pk>/", views.PresetUpdateView.as_view(), name="orders_Preset_update"),

    path("payment/success", views.SuccessView.as_view(), name="payment_success"),
    path("payment/cancel", views.CancelView.as_view(), name="payment_cancel"),
    path("zoomverify/verifyzoom.html", views.zoom_verify, name="zoom_verify"),

    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/', include('api.urls')),
    path('portfolio/', include('frontend.urls')),
    path('internal/access/', include('access.urls')),
    path('internal/orders', include('orders.urls')),
    path('internal/workflow', include('workflow.urls')),
    path('select2/', include('django_select2.urls')),
]
