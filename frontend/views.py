from django import views
from django.shortcuts import render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.conf import settings
from frontend import forms
from billing.models import BillingInfo
from orders.serializers import OrderItemSerializer
import stripe
import json

STRIPE_PUBLISHABLE_KEY = settings.STRIPE_PUBLISHABLE_KEY

class BaseOrderFormView(views.View):
    form_label = ''
    form_class = forms.BaseOrderForm

    def get(self, request, *args, **kwargs):
        return render(request, 'fragments/forms/order_form.html', {'form_label': self.form_label, 'form': self.form_class(request.user)})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)

        if form.is_valid():
            serializer = OrderSerializer(data=form.cleaned_data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.create(serializer.validated_data)

        else:
            print(form.errors)

        return render(request, 'fragments/forms/order_form.html', {'form_label': self.form_label, 'form': self.form_class(request.user)})


class OrderTranscriptionView(BaseOrderFormView):
    form_label = "Transcription Order Form"
    form_class = forms.TranscriptionOrderForm


class OrderTranslationView(BaseOrderFormView):
    form_label = "Translation Order Form"
    form_class = forms.TranslationOrderForm


class OrderAudioDescriptionView(BaseOrderFormView):
    form_label = "Audio Description Order Form"
    form_class = forms.AudioDescriptionOrderForm

def get_billing_for_user(user):
    billing_profile = BillingInfo.objects.get(user=user)
    return billing_profile

def get_publishable_key(request):
    return JsonResponse({'publicKey': settings.STRIPE_PUBLISHABLE_KEY})

@csrf_exempt
def create_setup_intent(request):
    # Create or use an existing Customer to associate with the SetupIntent.
    # The PaymentMethod will be stored to this Customer for later use.
    stripe.api_key = settings.STRIPE_API_KEY
    billing_profile = get_billing_for_user(request.user)
    customer = stripe.Customer.retrieve(billing_profile.stripe_customer_id)

    setup_intent = stripe.SetupIntent.create(
        customer=customer['id']
    )
    return JsonResponse({'setup_intent': setup_intent})

@csrf_exempt
def set_default_payment_method(request, payment_method_id):
    try:
        billing_profile = get_billing_for_user(request.user)
        billing_profile.set_default_payment_method(payment_method_id)
        return HttpResponseRedirect("/plans")
    except Exception as e:
        return HttpResponseRedirect("/plans")

@csrf_exempt
def webhook_received(request):
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = settings.STRIPE_API_KEY
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'setup_intent.created':
        print('🔔 A new SetupIntent was created.')

    if event_type == 'setup_intent.succeeded':
        print(
            '🔔 A SetupIntent has successfully set up a PaymentMethod for future use.')
    
    if event_type == 'payment_method.attached':
        print('🔔 A PaymentMethod has successfully been saved to a Customer.')

        # At this point, associate the ID of the Customer object with your
        # own internal representation of a customer, if you have one.

        # Optional: update the Customer billing information with billing details from the PaymentMethod
        stripe.Customer.modify(
            data_object['customer'],
            email=data_object['billing_details']['email']
        )
        print('🔔 Customer successfully updated.')

    if event_type == 'setup_intent.setup_failed':
        print(
            '🔔 A SetupIntent has failed the attempt to set up a PaymentMethod.')

    if event_type == 'payment_intent.succeeded':
        print('Payment received!')
        # Fulfill any orders, e-mail receipts, etc
        # TODO Update Order Status
        # Send job to Airflow for processing

    if event_type == 'payment_intent.payment_failed':
        # Notify the customer that their order was not fulfilled
        # TODO Add e-mail / slack / CS notif.
        print(' Payment failed.')

    return JsonResponse({'status': 'success'})

@csrf_exempt
def create_payment():
    data = json.loads(request.data)
    # Create a PaymentIntent with the order amount and currency
    intent = stripe.PaymentIntent.create(
        amount=calculate_order_amount(data['items']),
        currency=data['currency'],
    )

    try:
        # Send publishable key and PaymentIntent details to client
        return jsonify({'publicKey': STRIPE_PUBLISHABLE_KEY, 'clientSecret': intent.client_secret, 'id': intent.id})
    except Exception as e:
        return jsonify(str(e)), 403

@csrf_exempt
def pay(request):
  intent = None
  billing_profile = get_billing_for_user(request.user)
  payment_method = billing_profile.get_default_payment_method()
  pm_id = payment_method['data'][0]['id']

  json_data = json.loads(request.body)
  clientSideAmount = json_data["clientPrice"]
  order_data = json_data["order_data"]
  try:
    if payment_method:
      # Create the PaymentIntent
      order_amount = calculate_order_amount(clientSideAmount)
      intent = stripe.PaymentIntent.create(
        payment_method = pm_id,
        customer = billing_profile.stripe_customer_id,
        description = json.dumps(order_data),
        amount = order_amount,
        currency = 'usd',
        confirmation_method = 'automatic',
        confirm = True,
        metadata={
            'data': json.dumps(order_data),
        },
      )
    elif 'payment_intent_id' in request.POST:
      intent = stripe.PaymentIntent.confirm(json_data['payment_intent_id'])
  except stripe.error.CardError as e:
    # Display error on client
    return json.dumps({'error': e.user_message}), 200

  resp = generate_response(intent)
  print(intent)
  return resp

@csrf_exempt
def generate_response(intent):
  # Note that if your API version is before 2019-02-11, 'requires_action'
  # appears as 'requires_source_action'.
  if intent.status == 'requires_action' and intent.next_action.type == 'use_stripe_sdk':
    # Tell the client to handle the action
    return JsonResponse({
      'requires_action': True,
      'payment_intent_client_secret': intent.client_secret,
    })
  elif intent.status == 'succeeded':
    # The payment didn’t need any additional actions and completed!
    # Handle post-payment fulfillment
    return JsonResponse({'publicKey': STRIPE_PUBLISHABLE_KEY, 'clientSecret': intent.client_secret, 'id': intent.id})
  else:
    # Invalid status
    return JsonResponse({'error': 'Invalid PaymentIntent status'})

def calculate_order_amount(clientPrice=None):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    raw_amount = float(clientPrice) * float(100.00)
    integer_amount = int(raw_amount)
    return integer_amount