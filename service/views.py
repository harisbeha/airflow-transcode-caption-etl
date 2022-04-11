from django import forms
from django.http import HttpResponse, JsonResponse
from django.shortcuts import HttpResponseRedirect, render
from django.template import loader
from django.views import generic
from google.auth import jwt
import django_filters

from access.models import AccessToken
from orders.models import Cart, OrderItem, Preset
from orders.enums import OrderStatus
from orders.forms import PresetForm, OrderItemForm
from library.models import Entry
import django_tables2 as tables
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from django_select2 import forms as s2forms
from django.views.decorators.csrf import csrf_exempt
import analytics
import json
import stripe

from google.cloud import pubsub_v1
from google.cloud import storage


# class EntryTable(tables.Table):
#     id = tables.CheckBoxColumn(accessor='pk', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
#     created = tables.DateTimeColumn(accessor='created', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
#     name = tables.Column(accessor='name', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
#     status = tables.Column(accessor='order_status', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
#     media_length = tables.Column(accessor='media_length', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
#     actions = tables.Column(attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})

    # class Meta:
    #     model = Entry
    #     template_name = "django_tables2/tailwind.html"
    #     fields = ('id', 'name', 'created', 'media_length', 'status')
    #     attrs = {"class": "min-w-full leading-normal shadow rounded-md"}


class EntryFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=['Imported', 'Ordered', 'Error'],field_name="order_status", lookup_expr='icontains')
    ingest_source = django_filters.CharFilter(field_name="integration_source", lookup_expr='icontains')
    date_published = django_filters.DateRangeFilter(field_name='created')

    class Meta:
        model = Entry
        exclude = []


def index(request):
    template = loader.get_template('index.html')
    if request.user.is_authenticated:
        HttpResponseRedirect('/library')
    context = {}
    return HttpResponseRedirect('https://mydomain.com/cirrus-integrations/')


# @login_required
def library(request):
    template = loader.get_template('library.html')
    
    try:
        u = request.user
        show_signup_conversion_script = False
        if u.last_login == None:
            show_signup_conversion_script = True
        elif u.last_login.date() == u.date_joined.date():
            show_signup_conversion_script = True
    except Exception as e:
        print(e)
    
    
    from library.models import EntryTable
    from django.contrib.auth.models import User
    u = User.objects.get(id=25)
    entry_list = Entry.objects.filter(user=u)
    # entry_list = Entry.objects.all()
    has_entries = entry_list.exists()

    data = request.GET.copy()

    entry_filter = EntryFilter(data, queryset=entry_list)
    table = EntryTable(data=entry_filter.queryset, order_by="-created")
    tables.RequestConfig(request, paginate={"per_page": 10}).configure(table)

    if request.method == "POST":
        selected_ids = request.POST.getlist("id")

        cart, created = Cart.objects.get_or_create(user=request.user, abandoned=None)
        standard_product = Preset.objects.filter(global_default=True).first()

        for sid in selected_ids:
            entry = Entry.objects.get(id=sid)
            order_item, created = OrderItem.objects.get_or_create(entry_id=entry.id, media_length_ms=entry.media_length_ms, product_template=standard_product)
            cart.orderitem_set.add(order_item)
            try:
                analytics.track(request.user.id, 'Video Added to Cart', {
                    'title': order_item.entry.title,
                    'integration_source': order_item.entry.integration_source,
                    'media_length': order_item.entry.media_length_ms
                })
            except Exception as e:
                print(e)
        try:
            cart_count = cart.orderitem_set.count() if cart.orderitem_set() else 0
            integration_sources = cart.orderitem_set.values_list("entry__integration_source", flat=True)
            analytics.track(request.user.id, 'Videos Added to Cart', {
                'count': cart_count,
                'integration_sources': str(integration_sources),
            })  
        except Exception as e:
            print(e)
        # message = "Successfully added {0} items to your cart ".format(len(selected_ids))
        # messages.success(request, message = message)
        return HttpResponseRedirect('/cart-preview')
    context = {
        'filter': entry_filter,
        'entry_list': entry_list,
        'table': table,
        'has_entries': has_entries,
        'show_signup_conversion_script': show_signup_conversion_script,
    }
    return HttpResponse(template.render(context, request))


class RefactoredSelectMultipleWidget(s2forms.ModelSelect2MultipleWidget):
    def filter_queryset(self, request, term, queryset=None, **kwargs):
        presets = Preset.objects.filter(user=request.user)
        return presets


@login_required
def cart_preview(request):
    try:
        # Init Stripe
        from django.conf import settings
        stripe_public_key = settings.STRIPE_PUBLISHABLE_KEY
        template = loader.get_template('cart_preview.html')
        # Get BillingInfo and PaymentMethod
        billing_profile = get_billing_for_user(request.user)
        payment_method = billing_profile.get_default_payment_method()

        existing_carts = Cart.objects.filter(user=request.user, abandoned=None).order_by('-created')
        cart_exists = existing_carts.exists()
        if cart_exists:
            cart = existing_carts.first()
        else:
            cart = Cart.objects.create(user=request.user, abandoned=None)
        order_items = cart.orderitem_set.all()
                # Create new Checkout Session for the order
                # Other optional params include:
                # [billing_address_collection] - to display billing address details on the page
                # [customer] - if you have an existing Stripe Customer ID
                # [payment_intent_data] - lets capture the payment later
                # [customer_email] - lets you prefill the email input in the form
                # For full details see https:#stripe.com/docs/api/checkout/sessions/create

        subtotal = 0.00
        total = 0.00
        discount = 0.00

        line_items = []
        for item in order_items:
            stripe_formatted_price = item.product_template.price * 100

            if item.minutes < 1.00:
                minutes = 1
            else:
                minutes = int(item.minutes)

            description = "{0} - Minutes: {1}".format(item.product_template.name, minutes)
            line_item = {
                'name': item.entry.title,
                'description': description,
                'images': [item.entry.thumbnail_url],
                'amount': int(stripe_formatted_price),
                'currency': 'usd',
                'quantity': int(minutes),
            }
            line_items.append(line_item)
            subtotal += int(minutes) * item.product_template.price
            if item.product_template.discount_per_minute:
                discount += int(minutes) * item.product_template.discount_per_minute

        total = subtotal

        cart_uuid = str(cart)
        if cart.is_empty():
            stripe_session_id = None
        else:
            stripe_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                success_url='https://sub.mydomain.com/payment/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://sub.mydomain.com/cart-preview',
                customer=billing_profile.stripe_customer_id,
                billing_address_collection='auto',
                client_reference_id=cart_uuid,
                line_items=line_items
                )
            try:
                stripe_session_id = stripe_session["id"]
            except Exception as e:
                stripe_session_id = stripe_session

        OrderItemFormset = modelformset_factory(OrderItem, form=OrderItemForm, extra=0)
        analytics.track(request.user.id, 'Previewed Cart', {
            'order_total': total,
        })
        if request.method == "POST":
            analytics.track(request.user.id, 'Updated Cart Products', {
                'order_total': total,
                'item_count': order_items.count(),
            })
            formset = OrderItemFormset(request.POST, form_kwargs={'user': request.user}, queryset=order_items)
            if formset.is_valid():
                formset.save()
                print("form saved")
                return HttpResponseRedirect('/cart-preview')
            else:
                print("wtf")
        else:
            formset = OrderItemFormset(form_kwargs={'user': request.user}, queryset=order_items)
        context = {
            'cart': cart,
            'formset': formset,
            'order_items': order_items,
            'subtotal': subtotal,
            'discount': discount,
            'total': total,
            'stripe_public_key': stripe_public_key,
            'hide_checkout': False,
            'CHECKOUT_SESSION_ID': stripe_session_id,
            # 'pm_id': pm_id,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/library')


@login_required
def bulk_import(request):
    template = loader.get_template('bulk_import.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def plans(request):
    from billing.models import BillingInfo
    template = loader.get_template('plans.html')
    billing_profile = BillingInfo.objects.get(user=request.user)
    payment_methods = billing_profile.get_default_payment_method()
    customer = billing_profile.get_stripe_customer()
    context = {
        'payment_methods': payment_methods,
        'balance': billing_profile.balance,
        'customer': customer,
    }
    return HttpResponse(template.render(context, request))

@login_required
def add_card(request):
    from billing.models import BillingInfo
    template = loader.get_template('add-card.html')
    billing_profile = BillingInfo.objects.get(user=request.user)
    customer = billing_profile.get_stripe_customer()
    payment_methods = billing_profile.get_default_payment_method()
    context = {
        'payment_methods': payment_methods,
        'balance': billing_profile.balance
    }
    return HttpResponse(template.render(context, request))

def api_keys(request):
    api_key_qs = AccessToken.objects.filter(created_by=request.user)
    template = loader.get_template('api_keys.html')
    context = {
        'api_key_qs': api_key_qs,
    }
    return HttpResponse(template.render(context, request))

def zoom_verify(request):
    template = loader.get_template('zoomverify.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def integrations(request):
    analytics.track(request.user.id, 'Viewed Page', {"title": "Integrations", "email": request.user.email})  
    from integrations.zoom.models import ZoomAuth
    from integrations.youtube.models import GoogleAPIOauthInfo
    has_zoom_integration = ZoomAuth.objects.filter(user=request.user).exists()
    has_youtube_integration = GoogleAPIOauthInfo.objects.filter(user=request.user).exists()
    has_wistia_integration = False
    has_limelight_integration = False
    has_vimeo_integration = False
    template = loader.get_template('integrations.html')
    analytics.track(request.user.id, 'Viewed Integrations', {
        'has_wistia_integration': has_wistia_integration,
        'has_zoom_integration': has_zoom_integration,
        'has_limelight_integration': has_limelight_integration,
        'has_wistia_integration': has_wistia_integration,
        'has_vimeo_integration': has_vimeo_integration,
    })
    context = {
        'has_zoom_integration': has_zoom_integration,
        'has_youtube_integration': has_youtube_integration,
    }
    return HttpResponse(template.render(context, request))

@login_required
def order(request):
    template = loader.get_template('order.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def order_realtime(request):
    template = loader.get_template('order_realtime.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def team(request):
    template = loader.get_template('team.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def user_settings(request):
    from access.forms import AccountSettingsForm
    from billing.forms import BillingInfoForm
    from billing.models import BillingInfo
    
    billing_profile = BillingInfo.objects.get(user=request.user)
    account_settings_form = AccountSettingsForm()
    billing_info_form = BillingInfoForm(instance=billing_profile)
    template = loader.get_template('settings.html')
    context = {
        'account_settings_form': account_settings_form,
        'billing_info_form': billing_info_form,
    }
    analytics.track(request.user.id, 'Viewed User Settings', {
        'placeholder': True,
    })
    return HttpResponse(template.render(context, request))


class OrderFilter(django_filters.FilterSet):
    job_name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=OrderStatus.choices,field_name="order_status", lookup_expr='icontains')
    ingest_source = django_filters.CharFilter(field_name="source", lookup_expr='icontains')
    added = django_filters.DateRangeFilter(field_name='created')
    order_type = django_filters.CharFilter(field_name="order_type", lookup_expr='icontains')

    class Meta:
        model = Entry
        exclude = []
        # form = OrderFilterForm


@login_required
def presets(request):
    template = loader.get_template('presets.html')
    context = {}
    return HttpResponse(template.render(context, request))


@login_required
def checkout(request):
    from billing.forms import BillingInfoForm
    
    billing_profile = BillingInfo.objects.get(user=request.user)
    billing_info_form = BillingInfoForm(instance=billing_profile)
    payment_methods = billing_profile.get_default_payment_method()
    template = loader.get_template('checkout.html')

    # Execute off-session payment and process the orders
    if request.method == "POST":
        pass
    context = {
        'billing_info_form': billing_info_form,
    }
    return HttpResponse(template.render(context, request))


@login_required
def orders(request):
    from library.models import OrderTable
    order_list = OrderItem.objects.filter(entry__user=request.user)
    # order_list = OrderItem.objects.all()
    data = request.GET.copy()
    order_filter = OrderFilter(data, queryset=order_list)
    table = OrderTable(data=order_filter.qs, order_by="-created")
    tables.RequestConfig(request, paginate={"per_page": 10}).configure(table)
    template = loader.get_template('orders.html')
    analytics.track(request.user.id, 'Viewed Orders', {
        'order_count': order_list.count(),
    })
    if request.method == "POST":
        cart_job_ids = request.POST.getlist("id")
        message = json.dumps({"cart_job_ids": cart_job_ids})
        messages.success(request, message = message)
        return HttpResponseRedirect('/cart')
    context = {
        # 'filter': order_filter,
        'order_list': order_list,
        'table': table,
    }
    return HttpResponse(template.render(context, request))



class PresetListView(generic.ListView):
    model = Preset
    template_name = "presets.html"
    form_class = PresetForm


class PresetCreateView(generic.CreateView):
    model = Preset
    template_name = "presets/create_preset.html"
    form_class = PresetForm


class PresetDetailView(generic.DetailView):
    model = Preset
    template_name = "presets/preset_detail.html"
    form_class = PresetForm


class PresetUpdateView(generic.UpdateView):
    model = Preset
    template_name = "presets/update_preset.html"
    form_class = PresetForm
    pk_url_kwarg = "pk"


def get_billing_for_user(user):
    from billing.models import BillingInfo
    billing_profile = BillingInfo.objects.get(user=user)
    return billing_profile


@login_required
def payment_confirmation(request, payment_id):
    from billing.forms import BillingInfoForm
    from billing.models import BillingInfo
    
    billing_profile = BillingInfo.objects.get(user=request.user)
    billing_info_form = BillingInfoForm(instance=billing_profile)
    
    payment_metadata = payment_id
    final_amount = 10.00
    transaction_id = payment_id.split("secret")[0]

    template = loader.get_template('payment_confirmation.html')
    context = {
        'transaction_id': transaction_id,
        'payment_metadata': payment_id,
        'final_amount': final_amount,
    }
    return HttpResponse(template.render(context, request))


class SuccessView(generic.TemplateView):
    template_name = "payment_success.html"
    def get(self, request, *args, **kwargs):
        analytics.track(request.user.id, 'Payment - Checkout Success', {
            'placeholder': True,
        })
        return render(request, self.template_name )


class CancelView(generic.TemplateView):
    template_name = "payment_cancelled.html"
    def get(self, request, *args, **kwargs):
        analytics.track(request.user.id, 'Payment - Checkout Cancelled', {
            'placeholder': True,
        })
        return render(request, self.template_name )

# {
# "id": external_id,
# "object": object,
# "api_version": api_version,
# "created": created_timestamp
# "data": data_json,
# }


class StripeEventForm(forms.Form):
    id = forms.CharField()
    object = forms.CharField()
    api_version = forms.CharField()
    created = forms.CharField()
    data = forms.CharField()


@csrf_exempt
def payment_webhook_received(request):
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    from datetime import datetime, timedelta
    from django.conf import settings
    import stripe
    from billing.models import Transaction
    stripe.api_key = settings.STRIPE_API_KEY
    webhook_secret = "whsec_gyHDr6fxQEUzzkaYqlWn50GvS0tFyMHV"

    if request.method == 'POST':
    # create a form instance and populate it with data from the request:
    # form = StripeEventForm(request.POST)
    # check whether it's valid:
        # process the data in form.cleaned_data as required
        # ...
        # redirect to a new URL:

        if webhook_secret:
            # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
            sig_header = request.META['HTTP_STRIPE_SIGNATURE']
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body, sig_header=sig_header, secret=webhook_secret)
                data = event['data']
            except Exception as e:
                return e
            # Get the type of webhook event sent - used to check the status of PaymentIntents.
            event_type = event['type']
        else:
            data = request.body['data']
            event_type = request.body['type']
        data_object = data['object']

        if event_type == 'checkout.session.completed':
            try:
                print('🔔 Payment succeeded!')
                client_ref_id_raw = data_object.get("client_reference_id", "")
                client_ref_id = client_ref_id_raw.replace("Cart object (", "").replace(")", "").strip()
                cart_id = client_ref_id
                payment_id = data_object.get("id", None)
                if payment_id and cart_id:
                    # Create Transaction model entry
                    cart = Cart.objects.get(uuid=cart_id)
                    data_json_str = json.dumps(data_object)
                    transaction, created = Transaction.objects.get_or_create(ordered_by=cart.user, data_json=data_json_str, service='STRIPE', cart_id=cart_id, external_id=payment_id)

                    cart.checked_out = True
                    cart.payment_id = payment_id
                    cart.completed_date = datetime.now()
                    cart.payment_status = "SUCCESS"
                    cart.save()
                    for item in cart.orderitem_set.all():
                        item.status = 'Pending'
                        item.payment_status = 'Paid'
                        item.save()
                    analytics.track(cart.user.id, 'Payment - Success', {
                        'payment_source': 'Stripe',
                        'cart_id': cart.payment_id,
                        'payment_id': cart.payment_id,
                    })
                    try:
                        publish_orders(cart.orderitem_set.all())
                        from service.email import send_order_started_email
                        send_order_started_email(cart.user, cart.orderitem_set.all())
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
        else:
            analytics.track('MACHINE', 'Payment - Failed', {
                'payment_source': 'Stripe',
            })
    return JsonResponse({'status': 'success'})


def cookies(request):
    try:
        analytics.track(request.user.id, 'Terms Pages', {
            'page_type': 'cookies',
        })
    except Exception as e:
        print(e)
    template = loader.get_template('cookies.html')
    context = {}
    return HttpResponse(template.render(context, request))


def privacy(request):
    try:
        analytics.track(request.user.id, 'Terms Pages', {
            'page_type': 'privacy',
        })
    except Exception as e:
        print(e)
    template = loader.get_template('privacy.html')
    context = {}
    return HttpResponse(template.render(context, request))


def terms(request):
    try:
        analytics.track(request.user.id, 'Terms Pages', {
            'page_type': 'terms-of-service',
        })
    except Exception as e:
        print(e)
    template = loader.get_template('terms.html')
    context = {}
    return HttpResponse(template.render(context, request))

def get_output_download_url(order_item_uuid):
    from orders.models import OutputProduct
    order_item = OrderItem.objects.filter(uuid=order_item_uuid).first()
    output = OutputProduct.objects.filter(entry_id=order_item.entry.id).first()
    output_json = output.json
    vtt_data = output_json.get("vtt", None)
    bucket_name = vtt_data.get("bucket")
    file_key = vtt_data.get("path")
    signed_url = generate_signed_url('google-cloud.json', bucket_name, file_key)
    return signed_url

def download_to_memory(order_item_uuid):
    from orders.models import OutputProduct
    order_item = OrderItem.objects.filter(uuid=order_item_uuid).first()
    output = OutputProduct.objects.filter(entry_id=order_item.entry.id).first()
    output_json = output.json
    vtt_data = output_json.get("srt", None)
    bucket_name = vtt_data.get("bucket")
    file_key = vtt_data.get("path")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.get_blob(file_key)
    content = blob.download_as_string()
    content = content.decode("utf-8")
    return content

@login_required
def download_vtt(request, order_uuid):
    try:
        order_item = OrderItem.objects.filter(uuid=order_uuid).first()
        cart = order_item.cart
        if request.user == cart.user:
            signed_url = get_output_download_url(order_uuid)
            return HttpResponseRedirect(signed_url)
        return HttpResponseRedirect('/unauthorized')
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/orders')

@login_required
def job_detail(request, entry_id):
    try:
        from library.interactive import convert_srt_to_hyperaudio
        template = loader.get_template('job_detail.html')
        context = {}
        order_items = OrderItem.objects.filter(entry__id=entry_id, payment_status="Paid")
        order_item = order_items.first()
        cart = order_item.cart
        if request.user == cart.user:
            content = download_to_memory(str(order_item.uuid))
            interactive_transcript = convert_srt_to_hyperaudio(content)
            context["interactive_transcript"] = interactive_transcript
            context["entry"] = Entry.objects.filter(user=request.user, id=entry_id).first()
            return HttpResponse(template.render(context, request))
        return HttpResponseRedirect('/library')
    except Exception as e:
        print(e.format_exc())
        return HttpResponse(template.render(context, request))

@login_required
def remove_item_from_cart(request, order_uuid):
    try:
        order_item = OrderItem.objects.get(uuid=order_uuid)
        cart = order_item.cart
        analytics.track(request.user.id, 'Cart - Item Removed', {
            'entry_id': order_item.entry.id,
            'integration_source': order_item.entry.integration_source,
            'own_cart': False,
        })
        if request.user == cart.user:
            cart.orderitem_set.remove(order_item)
            analytics.track(request.user.id, 'Cart - Item Removed', {
                'entry_id': order_item.entry.id,
                'integration_source': order_item.entry.integration_source,
                'own_cart': True,
            })
    except Exception as e:
        print(e)
    return HttpResponseRedirect('/cart-preview')


def construct_order_details(order_item):
    order_details = {
        "order_uuid": str(order_item.uuid), 
        "preset_uuid": str(order_item.product_template.uuid),
        "entry_title": order_item.entry.title,
        "media_url": order_item.entry.media_url,
        "turnaround_time": order_item.product_template.turnaround_time,
        "source_language": order_item.product_template.source_language,
        "target_languages": order_item.product_template.target_languages,
    }
    return order_details


def publish_orders(order_items):
    project_id = "coresystem-171219"
    topic_name = "Order-From-Main"

    # Add IAM Role
    service_account_info = json.load(open('google-cloud.json'))
    publisher_audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
    credentials = jwt.Credentials.from_service_account_info(service_account_info, audience=publisher_audience)
    credentials_pub = credentials.with_claims(audience=publisher_audience)

    # Configure the batch to publish as soon as there is ten messages,
    # one kilobyte of data, or one second has passed.
    batch_settings = pubsub_v1.types.BatchSettings(
        max_messages=8,  # default 100
        max_bytes=1024,  # default 1 MB
        max_latency=15,  # default 10 ms
    )

    publisher = pubsub_v1.PublisherClient(credentials=credentials_pub, batch_settings=batch_settings)
    topic_path = publisher.topic_path(project_id, topic_name)

    for order_item in order_items:
        order_details = construct_order_details(order_item)
        data = bytes(json.dumps(order_details).encode("utf-8"))
        publisher.publish(topic_path, data, order_uuid=str(order_item.uuid),
            preset_uuid=str(order_item.product_template.uuid),
            entry_title=order_item.entry.title,
            media_url=order_item.entry.media_url,
            turnaround_time=order_item.product_template.turnaround_time,
            source_language=order_item.product_template.source_language,
            target_language=order_item.product_template.target_languages)
