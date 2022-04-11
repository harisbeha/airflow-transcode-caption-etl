# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User

from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.http import HttpResponse
# from django.shortcuts import HttpResponseRedirect
from django.template import loader
from django.conf import settings

import requests
import json
import urllib

from integrations.zoom.models import ZoomAuth
from integrations.zoom.forms import ZoomSettingsForm

import django_tables2 as tables


import random
import string

import logging
logger = logging.getLogger(__name__)


def zoom_api(request):
    """
        GET REQUEST
        Generate refresh token from the Zoom API
        Update refresh token in models
        Redirect to Portfolio
    """
    # check method and params
    try:
        if request.method != "GET":
            print('32')
            return HttpResponse(status=400)
        if 'code' not in request.GET:
            print('35')
            print(request.GET.get('code'), request.GET.get('redirect'))
            return HttpResponse(status=400)

        user = request.user
        authorization_code = request.GET.get('code')
        redirect = request.GET.get('redirect')  # Portfolio Redirect URL
        redirect_uri = settings.ZOOM_REDIRECT_URI
        token = get_refresh_token(authorization_code, redirect_uri)
        if 'error' in token:
            logger.error("Error get_refresh_token {}".format(token['error']))
            print('53')
            print(token)
            return HttpResponse(status=400)

        _update_auth(user, token['refresh_token'])

        return HttpResponseRedirect("/integrations/zoom/import")
    except Exception as e:
        print(e)


def is_logged_zoom(request):
    """
        GET REQUEST
        Get if user is logged in zoom and profile data
    """
    # check method
    if request.method != "GET":
        return HttpResponse(status=400)
    user = request.user
    user_profile = _get_user_profile(user)
    data = _get_recordings(user)
    context = {
        "user_profile": user_profile,
        "extra": data,
    }
    return JsonResponse(context, safe=False)


def new_scheduled_meeting(request):
    """
        Generate new scheduled meeting
        https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingcreate
    """
    # check method and params
    if request.method != "POST":
        return HttpResponse(status=400)
    if 'display_name' not in request.POST or 'description' not in request.POST or 'date' not in request.POST or 'time' not in request.POST or 'duration' not in request.POST:
        return HttpResponse(status=400)

    user_id = 'me'
    url = "https://api.zoom.us/v2/users/{}/meetings".format(user_id)

    return set_scheduled_meeting(request, url, 'POST')


def update_scheduled_meeting(request):
    """
        Update scheduled meeting already created
    """

    # check method and params
    if request.method != "POST":
        return HttpResponse(status=400)
    if 'display_name' not in request.POST or 'description' not in request.POST or 'date' not in request.POST or 'time' not in request.POST or 'duration' not in request.POST or 'meeting_id' not in request.POST:
        return HttpResponse(status=400)

    meeting_id = request.POST['meeting_id']
    url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)

    return set_scheduled_meeting(request, url, 'PATCH')


def set_scheduled_meeting(request, url, api_method):
    """
        Set all attributes and create/update meeting
    """
    user = request.user
    refresh_token = _get_refresh_token(user)
    token = get_access_token(user, refresh_token)
    if 'error' in token:
        logger.error("Error get_access_token {}".format(token['error']))
        return HttpResponse(status=400)
    access_token = token['access_token']
    topic = request.POST['display_name']
    ttype = 2  # Scheluded Meeting
    start_time = '{}T{}:00'.format(
        request.POST['date'],
        request.POST['time'])  # yyyy-mm-ddTHH:mm:ss
    duration = request.POST['duration']
    timezone = "America/Los_Angeles"
    agenda = request.POST['description']
    body = {
        "topic": topic,
        "type": ttype,
        "start_time": start_time,
        "duration": duration,
        "timezone": timezone,
        "agenda": agenda,
    }
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json"
    }
    if api_method == 'POST':
        body['password'] = _generate_password()
        r = requests.post(
            url,
            data=json.dumps(body),
            headers=headers)  # CREATE
        if r.status_code == 201:
            data = r.json()
            response = {
                'meeting_id': data['id'],
                'start_url': data['start_url'],
                'join_url': data['join_url']
            }
        else:
            return HttpResponse(status=r.status_code)
    elif api_method == 'PATCH':
        r = requests.patch(
            url,
            data=json.dumps(body),
            headers=headers)  # UPDATE
        if r.status_code == 204:
            meeting_id = request.POST['meeting_id']
            response = {
                'meeting_id': meeting_id
            }
        else:
            return HttpResponse(status=r.status_code)
    return JsonResponse(response)


def get_access_token(user, refresh_token):
    """
        Get Access Token from the Zoom API
        IMPORTANT: REFRESH TOKEN WILL BE UPDATED.
    """
    params = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    url = 'https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token={0}'.format(refresh_token)
    headers = {
        'Authorization': 'Basic {}'.format(settings.ZOOM_AUTHORIZATION)
    }
    r = requests.post(url, headers=headers)
    token = r.json()
    if 'error' not in token:
        _update_auth(user, token['refresh_token'])  # Update refresh_token
    return token


def _get_refresh_token(user):
    """
        Get refresh token from models
    """
    try:
        zoom_auth = ZoomAuth.objects.get(
            user=user
        )
        return zoom_auth.zoom_refresh_token
    except ZoomAuth.DoesNotExist:
        return None


def get_refresh_token(authorization_code, redirect_uri):
    """
        Get refresh token from the Zoom API
    """
    params = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri
    }
    # https://zoom.us/oauth/token?code=sBOCeUSOfG_6gEcex6xQcKMeLoE4zq1aQ&redirect_uri=http://0.0.0.0:8000    
    import urllib.parse
    
    url = "https://zoom.us/oauth/token?grant_type=authorization_code&code={0}&redirect_uri=https://sub.mydomain.com/integrations/zoom/oauth".format(authorization_code)
    headers = {'Authorization': 'Basic {}'.format("bkk0bENVZVJYT0dyYmhadmVMYXc6YmZoS093Mk01SDdJbjRnU3AyUTZvRFY2N2pucUZHREw")}
    r = requests.post(url, headers=headers)
    return r.json()


def _update_auth(user, refresh_token):
    """
        Update the refresh token
    """
    try:
        zoom_auth = ZoomAuth.objects.get(
            user=user
        )
        zoom_auth.zoom_refresh_token = refresh_token
        zoom_auth.save()
    except ZoomAuth.DoesNotExist:
        zoom_auth = ZoomAuth.objects.create(
            user=user,
            zoom_refresh_token=refresh_token
        )


def _get_user_profile(user):
    """
        Get user profile
        Return user_profile
    """
    refresh_token = _get_refresh_token(user)
    # check if refresh token exists
    if refresh_token:
        token = get_access_token(user, refresh_token)
        if 'error' in token:
            logger.error("Error get_access_token {}".format(token['error']))
            return None
        access_token = token['access_token']

        user_profile = get_user_profile(access_token)
        if 'code' in user_profile:
            logger.error(
                "Error get_user_profile {}".format(
                    user_profile['code']))
            return None

        return user_profile
    else:
        logger.warning("Access Token Not Found")
        return None

def get_user_profile(access_token):
    """
        Using an Access Token to get User profile
    """
    headers = {
        'Authorization': 'Bearer  {}'.format(access_token)
    }
    url = 'https://api.zoom.us/v2/users/me'
    r = requests.get(url, headers=headers)
    data = r.json()
    return data

def _generate_password():
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(10))

def _get_recordings(user):
    """
        Get user profile
        Return user_profile
    """
    refresh_token = _get_refresh_token(user)
    # check if refresh token exists
    if refresh_token:
        token = get_access_token(user, refresh_token)
        if 'error' in token:
            logger.error("Error get_access_token {}".format(token['error']))
            return None
        access_token = token['access_token']

        resp = construct_request(access_token)
        if 'code' in resp:
            logger.error(
                "Error resp {}".format(
                    resp['code']))
            return None

        return resp
    else:
        logger.warning("Access Token Not Found")
        return None

def construct_request(access_token):
    """
        Establish a function for constructing arbitrary requests to the Zoom API
    """
    headers = {
        'Authorization': 'Bearer  {}'.format(access_token)
    }
    url = 'https://api.zoom.us/v2/users/me/recordings'
    r = requests.get(url, headers=headers)
    data = r.json()
    return data

class PreviewColumn(tables.Column):
    attrs = {
        "td": {
            "data-first-name": lambda entry: entry.play_url
        }
    }
    def render(self, play_url):
        preview_html = "<a href={0}>Preview</>".format(play_url)
        return preview_html

class ZoomEntryTable(tables.Table):
    cid = tables.CheckBoxColumn(accessor='id', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    id = tables.Column(accessor='id', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    start_time = tables.Column(accessor='start_time', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    name = tables.Column(accessor='name', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    meeting_id = tables.Column(accessor='meeting_id', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    play_url = PreviewColumn(accessor='play_url', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    # actions = tables.Column(attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    
    class Meta:
        # fields = ('id', 'name', 'start_time', 'meeting_id', 'play_url')
        template_name = "django_tables2/tailwind.html"
        attrs = {"class": "min-w-full leading-normal shadow rounded-md"}

def zoom_import(request):
    template = loader.get_template('integrations/zoom/zoom_import.html')
    entries = []
    context = {}
    _recordings = _get_recordings(request.user)
    meetings = _recordings.get("meetings", {})
    webinars = _recordings.get("webinars", {})
    for recording_type in [meetings, webinars]:
        for entry in recording_type:
            play_url = "Not provided"
            meeting_id = "Not provided"
            for recording in entry["recording_files"]:
                if recording["file_type"] == "MP4":
                    meeting_id = recording.get("meeting_id", "Not provided")
                    play_url = recording.get("play_url", "Not provided")
            entry = {
                "id": entry["id"],
                "name": entry["topic"],
                "meeting_id": meeting_id,
                "start_time": entry["start_time"],
                "play_url": play_url,
            }
            entries.append(entry)
    context["entries"] = entries
    print(entries)
    return HttpResponseRedirect("/library")

def zoom_settings(request):
    template = loader.get_template('integrations/zoom/zoom_settings.html')

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ZoomSettingsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:


            # Add Django messages saying settings successfully updated
            return HttpResponseRedirect('/integrations/zoom/settings')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ZoomSettingsForm() 

    context = {
        "form": form,
    }
    return HttpResponse(template.render(context, request))

def create_orders_from_zoom_results(entries):

    orders = {}
    return orders

def deactivate_zoom(request):
    """
        GET REQUEST
        Get if user is logged in zoom and profile data
    """
    # check method
    if request.method != "GET":
        return HttpResponse(status=400)
    context = {}
    return JsonResponse(context, safe=False)
