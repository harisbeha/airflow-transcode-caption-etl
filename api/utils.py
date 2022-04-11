from django.forms.models import model_to_dict
import json, re

from access.models import AccountConfiguration
from service.enums import OrderType, OrderStatus, DEFAULT_VIEW_ERROR_RESPONSE
from orders.models import Cart, OrderItem, OutputProduct
from orders.serializers import OrderItemSerializer


def unpack_values(values, key):
    """
    Unpacks A list of values from a comma delimited string
    :param values:
    :param key:
    :return:
    """
    if isinstance(values, str):
        values = re.sub(r'[\s\n\t]+', '', values)
        values = values.split(',')
    elif not isinstance(values, list):
        raise TypeError("{} must be either a comma delimited string or a list of strings".format(key.Ti))
    return values


def decipher_order(order_data, organization_user):
    """
    Unpacks the request data to determine what type of order is being requested
    :param order_data:
    :param organization_user:
    :return:
    """

    if isinstance(order_data, str):
        order_data = json.loads(order_data)
    elif not isinstance(order_data, dict):
        raise TypeError("Order Data must be submitted in json format")

    account_configs = AccountConfiguration.objects.get(account=organization_user.user).json
    order_details = {}

    if order_data.get('add_ons'):
        order_details.update({'add_ons': unpack_values(order_data.get('add_ons'), 'add_ons')})
    else:
        order_details.update({'add_ons': account_configs.get('default_add_ons', None)})

    if order_data.get('target_languages'):
        order_details.update({'target_languages': unpack_values(order_data['target_languages'], 'target_languages')})

    order_details.update({'source_language': order_data.get('source_language', 'en')})
    order_details.update({'title': order_data.get('title', None)})
    order_details.update({'media_url': order_data.get('media_url', None)})

    return json.dumps(order_details)


def decipher_order_for_update(order_data):
    """
    Fetches from the request body data the altered order details
    :param order_data:
    :return:
    """
    if isinstance(order_data, str):
        order_data = json.loads(order_data)
    elif not isinstance(order_data, dict):
        raise TypeError("Order Data must be submitted in json format")

    order_details = {}
    if order_data.get('order_type'):
        order_details.update({"order_type": order_data.get['order_type']})
    if order_data.get('add_ons'):
        order_details.update({'add_ons': unpack_values(order_data.get('add_ons'), 'add_ons')})
    if order_data.get('target_languages'):
        order_details.update({'target_languages': unpack_values(order_data['target_languages'], 'target_languages')})
    if order_data.get('source_language'):
        order_details.update({'source_language': order_data.get('source_language')})
    if order_data.get('title'):
        order_details.update({'title': order_data['title']})
    if order_data.get('media_url'):
        order_details.update({'media_url': order_data['media_url']})
    return order_details


def create_order(order_data):
    order_serializer = OrderSerializer(data=order_data)
    order_serializer.is_valid(raise_exception=True)
    order_object = order_serializer.create(order_serializer.validated_data)
    return model_to_dict(order_object)


def update_order(target_order, new_order_details):
    old_order_details = target_order.json
    target_order.order_details = json.dumps(old_order_details.update(new_order_details))
    target_order.save()
    return model_to_dict(target_order)


def cancel_order(pk, organization):
    order = fetch_order_by_pk(pk)
    if not order:
        return False, "Order matching ID does not exist"
    elif order.organization_id != organization.id:
        return False, "Orders may only be cancelled by the ordering organization. " + DEFAULT_VIEW_ERROR_RESPONSE
    elif order.deleted:
        return True, "Order {} has already been previously deleted".format(pk)
    else:
        order.delete_order()
        return True, "Order {} successfully Deleted".format(pk)


def fetch_existing_order_for_update(pk, organization):
    order = fetch_order_by_pk(pk)
    if not order:
        return "Order matching ID does not exist"
    elif order.organization_id != organization.id:
        # return "Orders may only be modified by the ordering organization. " + DEFAULT_VIEW_ERROR_RESPONSE
        return "Orders may only be modified by the ordering organization. If you feel like you recieved this message in error, please contact your support admin"
    elif order.order_status not in [OrderStatus.PENDING.value, OrderStatus.LOW_BALANCE.value]:
        return "Unable to update order once in progress"
    else:
        return order


def fetch_order_by_pk(pk):
    return Order.objects.filter(uuid=pk).first()


# TODO: this is a skeleton to be completed in another issue
def job_status(pk, organization):
    return {}


def fetch_job_statuses(organization, pk=None):
    """
    filters orders by organization and optional order ID and returns json of order/status/details
    :param organization:
    :param pk:
    :return:
    """
    orders = Order.objects.prefetch_related('job', 'job__workflowtracker').filter(organization=organization)

    if pk:
        orders = orders.filter(uuid=pk)

    if not orders.exists():
        return False, "Unable to find any orders matching request. " + DEFAULT_VIEW_ERROR_RESPONSE

    orders_data = []
    for target_order in list(orders):
        orders_data.append(fetch_job_info(target_order))

    if len(orders_data) == 1:
        return True, orders_data[0]
    else:
        return True, orders_data


def fetch_job_info(target_order):
    """
    Returns data and status of a job
    :param target_order:
    :return:
    """
    job_info = {
        'order_details': target_order.json,
        'order_id': target_order.uuid,
        'order_status': target_order.order_status
    }

    if target_order.order_status in [OrderStatus.SUBMITTED.value, OrderStatus.COMPLETE.value]:
        workflow_steps = target_order.job.workflowtracker.json
        job_info.update({"job_status": workflow_steps})
    return job_info

def get_product_url(order_uuid, organization, product_name=None):
    target_order = fetch_order_by_pk(order_uuid)
    if not target_order:
        return False, "Order matching ID does not exist. " + DEFAULT_VIEW_ERROR_RESPONSE
    if not target_order.organization_id == organization.id:
        return False, "Account not authorized to view this data. " + DEFAULT_VIEW_ERROR_RESPONSE

    output_product = target_order.outputproduct

    if not output_product:
        return False, "Output Product not ready. " + DEFAULT_VIEW_ERROR_RESPONSE

    results = {product_name: output_product.json[product_name]} if product_name else output_product.json
    return True, results


def list_all_product_urls(organization):
    output_products = list(
        Order.valid_orders.filter(
            organization=organization,
            order_status=OrderStatus.COMPLETE.value,
            outputproduct__isnull=False
        ).values_list('uuid', 'output_product')
    )

    return {"data": [{product[0]: product[1].json} for product in output_products]}