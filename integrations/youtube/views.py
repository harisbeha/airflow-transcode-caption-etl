import tempfile
from django import forms
from django.conf import settings
from django.shortcuts import reverse
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.edit import FormView

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from integrations.youtube.models import GoogleAPIOauthInfo
import json
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.template import loader

import django_tables2 as tables
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from integrations.youtube.forms import YouTubeSettingsForm

from django.utils.safestring import mark_safe
from datetime import datetime

def MergeResults(dict1, dict2): 
    return(dict2.update(dict1))

class ThumbnailColumn(tables.Column):
    def render(self, value):
        return mark_safe(value)

class TruncatedTextColumn(tables.Column):
    def render(self, value):
        formatted_value = (value[:64] + '..') if len(value) > 64 else value
        return mark_safe(formatted_value)

class OrdersTable(tables.Table):
    id = tables.CheckBoxColumn(accessor='id', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    video_id = TruncatedTextColumn(accessor='video_id', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    channel_title = TruncatedTextColumn(accessor='channel_title', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    # playlist_id = TruncatedTextColumn(accessor='playlist_title', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    thumbnail_url = ThumbnailColumn(accessor='thumbnail_url', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    published_at = TruncatedTextColumn(accessor='published_at', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    title = TruncatedTextColumn(accessor='title', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    # description = TruncatedTextColumn(accessor='description', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"},"th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})
    imported = tables.BooleanColumn(accessor='media_length', attrs={"td": {"class": "px-5 py-5 border-b border-gray-200 bg-white text-sm"}, "th": {"class": "px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"}})


    class Meta:
        template_name = "django_tables2/tailwind.html"
        fields = ('id', 'video_id', 'published_at', 'title', 'channel_title', 'thumbnail_url', 'imported')
        attrs = {"class": "min-w-full leading-normal shadow rounded-md"}
        sequence = ('id', 'thumbnail_url', 'channel_title', 'published_at', 'video_id', 'title', 'imported')


class YouTubeForm(forms.Form):
    video = forms.FileField()


API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def feed_type(request):
    template = loader.get_template('integrations/youtube/youtube_select_feed_type.html')
    context = {
        'feed_type': feed_type,
    }
    return HttpResponse(template.render(context, request))

# elif feed_type == 'channel':
#     results = requests.get("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true", headers=headers)
#     import_template = "channel"
# elif feed_type == 'playlist':
#     results = requests.get("https://www.googleapis.com/youtube/v3/playlists?part=snippet&mine=true", headers=headers)
#     import_template = "playlist"

def youtube_import(request):
    template = loader.get_template('integrations/youtube/youtube_import.html')
    import requests
    auth = GoogleAPIOauthInfo.objects.get(user=request.user)
    access_token = auth.auth_token
    bearer = "Bearer {0}".format(access_token)
    headers = {"Authorization": bearer}
    results = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&forMine=true", headers=headers)
    formatted_data = format_results(results.json())
    if request.method == 'GET':
        table = OrdersTable(data=formatted_data, order_by="-published_at")
        tables.RequestConfig(request, paginate={"per_page": 25}).configure(table)
    if request.method == "POST":
        selected_ids = request.POST.getlist("id")
        for result in formatted_data:
            if result["video_id"] in selected_ids:
                create_entry_from_youtube_result(request.user, result)
        message = "Successfully imported {0} videos".format(len(selected_ids))
        messages.success(request, message = message)
        return HttpResponseRedirect('/')
    context = {
        'feed_type': feed_type,
        'table': table,
    }
    return HttpResponse(template.render(context, request))


def get_videos_in_playlist(client, playlist_id):
    """
    Get list of videos in a play list.
    :param playlist_id: ID of the playlist.
    """
    playlist_list_params = {
        'part': 'snippet,contentDetails',
        'maxResults': 'YOUTUBE_VIDEOS_PER_PAGE',
        'playlistId': playlist_id,
    }
    while True:
        playlist_info = client.call_api(
            service_type='playlistItems',
            mine=True,
            method_type='list',
            id=playlist_id,
            params=playlist_list_params
        )
        for video_details in playlist_info['items']:
            video = {
                'id': video_details['contentDetails']['videoId'],
                'publishedAt': video_details['snippet']['publishedAt'],
                'title': video_details['snippet']['title'],
            }
            yield video

        # See if we need to keep looping to get more videos
        if 'nextPageToken' not in playlist_info:
            break

        playlist_list_params['pageToken'] = playlist_info['nextPageToken']


def format_results(data=dict(), feed_type=None):
    entries = []
    try:
        for entry in data["items"]:
            entry_data = entry["snippet"]
            videoId = entry["id"]["videoId"]
            publishedAt = entry_data.get("publishedAt")
            title = entry_data.get("title")
            description = entry_data.get("description")
            channel_title = entry_data["channelTitle"]
            media_length = entry_data.get("length", 0)
            playlist_title = entry_data.get("playlistId")
            for thumbnail_type, thumbnail_value in entry_data["thumbnails"].items():
                if thumbnail_type == "high":
                    thumbnail_src = thumbnail_value.get("url", "")
                    thumbnail_html = '<img class="rounded rounded-lg shadow" src={0} style="width:120; height:93;" />'.format(thumbnail_src)
            entry = {
                "id": videoId,
                "video_id": videoId,
                "published_at": publishedAt,
                "title": title,
                "description": description,
                "media_length_ms": 0,
                "media_url": "youtube://{0}".format(videoId),
                "thumbnail_url": thumbnail_src,
                "thumbnail_html": thumbnail_html,
                "channel_title": channel_title,
                "playlist_title": playlist_title,
                "imported": False,
            }
            entries.append(entry)
    except Exception as e:
        print(e)
    if entries:
        print(entries)
    return entries


def youtube_settings(request):
    template = loader.get_template('integrations/youtube/youtube_settings.html')

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = YouTubeSettingsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:


            # Add Django messages saying settings successfully updated
            return HttpResponseRedirect('/integrations/youtube/settings')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = YouTubeSettingsForm() 

    context = {
        "form": form,
    }
    return HttpResponse(template.render(context, request))

def create_entry_from_youtube_result(user, entry_data):
    from library.models import Entry
    entry = {
        "external_id": entry_data.get("video_id"),
        "integration_source": "YouTube",
        "channel_title": entry_data.get("channel_title"),
        "media_url": "YouTube",
        "thumbnail_url": entry_data.get("thumbnail_url"),
        "thumbnail_html": entry_data.get("thumbnail_html"),
        "media_length_ms": 0,
        "published_at": entry_data.get("published_at"),
        "media_length_ms": entry_data.get("media_length_ms", 2200),
        "title": entry_data.get("title"),
        "import_status": "IMPORTED",
        "description": entry_data.get("description"),
    }
    created_entry, created = Entry.objects.get_or_create(user=user, **entry)
    return entry["external_id"]


import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build


# scopes="https://www.googleapis.com/auth/youtube.force-ssl"
# user_service = GoogleAPIOauthInfo.objects.get(user=request.user)

# API - authenticate user with Youtube
def auth_youtube(request):

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scopes=['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtube.force-ssl'])
    flow.redirect_uri = "https://sub.mydomain.com/integrations/youtube/oauth2callback"
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        prompt='consent',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    # return JsonResponse({'redirect_url': authorization_url})
    return HttpResponseRedirect(authorization_url)


from rest_framework import serializers
import requests

class YouTubeAuthSerializer(serializers.ModelSerializer):
	class Meta:
		model = GoogleAPIOauthInfo
		fields = ("user_id", "auth_token", "expiry", "refresh_token")

from django.utils import timezone

def obtain_youtube_token(request):
  try:
    user_service = GoogleAPIOauthInfo.objects.get(user_id=request.user)
  except GoogleAPIOauthInfo.DoesNotExist:
    return HttpResponse("User does not have this service")

  # If token has expired - renew using refresh token : else return token
  expiry_object = datetime.strptime(user_service.expiry, '%Y-%d-%m %H:%M:%S.%f')
  koala = 2
  if koala == 1:
    return JsonResponse( {'access_token': user_service.auth_token} )
  else:
    # Send credentials to retrieve new token using refresh token
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': user_service.refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post('https://www.googleapis.com/oauth2/v4/token',
      data=data,
      headers=headers)

    data = response.json()
    # update new token and its new expiry date
    service = {
      'user_id': request.user.pk,
      'auth_token': data.get("access_token"),
      'expiry': timezone.now() + timezone.timedelta(seconds=data.get("expires_in")),
      'refresh_token': user_service.refresh_token,
      'access_token': data.get("access_token"),
    }
    userservice = YouTubeAuthSerializer(data=service)
    if userservice.is_valid():
      userservice.save()
    else:
      print(userservice.errors)

    return HttpResponseRedirect("/integrations/youtube/import")

def oauth2cb(request):
    # Send information from Youtube to retrieve the access token to the API
    state = request.GET.get('state')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scopes=['https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/youtube.force-ssl'],
        state=state)

    flow.redirect_uri = "https://sub.mydomain.com/integrations/youtube/oauth2callback"
    code = request.GET.get('code')
    flow.fetch_token(code=code)

    # Add the service and access_token to the user in the database
    data = flow.credentials
    service = {
        'user_id': request.user.pk,
        'auth_token': data.token,
        'expiry': data.expiry,
        'refresh_token': data.refresh_token
    }
    
    user_service, created = GoogleAPIOauthInfo.objects.get_or_create(user=request.user)
    user_service.auth_token = data.token
    user_service.expiry = data.expiry
    user_service.refresh_token = data.refresh_token
    user_service.save()

    # Test api - irrelevant
    youtube = build('youtube', 'v3', credentials=data)

    try:
        # response = youtube.search().list(
        #     part='snippet',
        #     forMine='true',
        #     maxResults=50
        # ).execute()
        # print(response)

        import requests
        auth = GoogleAPIOauthInfo.objects.get(user=request.user)
        access_token = auth.auth_token
        bearer = "Bearer {0}".format(access_token)
        headers = {"Authorization": bearer}
        results = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&forMine=true", headers=headers)
        formatted_data = format_results(results.json())

        entry_ids = []
        for result in formatted_data:
            new_entry_id = create_entry_from_youtube_result(request.user, result)
            entry_ids.append(new_entry_id)
        add_timestamps_to_entries(request.user, entry_ids)

        message = "Successfully imported {0} videos".format(len(formatted_data))
        messages.success(request, message = message)
    except Exception as e:
        print(e)

    return HttpResponseRedirect("/library")
    
def add_timestamps_to_entries(user, entry_ids):
    try:
        from library.models import Entry
        import requests
        auth = GoogleAPIOauthInfo.objects.get(user=user)
        access_token = auth.auth_token
        bearer = "Bearer {0}".format(access_token)
        headers = {"Authorization": bearer}
        entry_id_str = ",".join(entry_ids)
        formatted_url = "https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={0}".format(entry_id_str)
        resp = requests.get(formatted_url, headers=headers)
        data = resp.json()
        print("durationData", data)
        for item in data["items"]:
            entry_file_data = item["contentDetails"]
            videoId = item["id"]
            duration = entry_file_data["duration"]
            media_length_ms = ytDurationToMS(duration)
            entries = Entry.objects.filter(external_id=videoId)
            entries.update(media_length_ms=media_length_ms)
    except Exception as e:
        print(e)


def ytDurationToMS(duration): #eg P1W2DT6H21M32S
    week = 0
    day  = 0
    hour = 0
    min  = 0
    sec  = 0

    duration = duration.lower()

    value = ''
    for c in duration:
        if c.isdigit():
            value += c
            continue

        elif c == 'p':
            pass
        elif c == 't':
            pass
        elif c == 'w':
            week = int(value) * 604800
        elif c == 'd':
            day = int(value)  * 86400
        elif c == 'h':
            hour = int(value) * 3600
        elif c == 'm':
            min = int(value)  * 60
        elif c == 's':
            sec = int(value)

        value = ''

    dur = week + day + hour + min + sec
    durationMs = dur * 1000
    return durationMs


def get_timestamp_for_video(user_id, video_id):
    refresh_token, auth_token = get_user_refresh_token(user_id)
    credentials = Credentials(auth_token, refresh_token=refresh_token, client_id=client_id, client_secret=client_secret, token_uri=token_uri)
    # grequest = GRequest()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
    part = "snippet"
    request = youtube.videos().list(part="contentDetails", id=video_id)
    response = request.execute()
    duration = response["items"][0]["contentDetails"]["duration"]
    media_length_ms = ytDurationToMS(duration)

# items = sune_entries["items"]
# existing_entries = Entry.objects.filter(user_id=383).values_list("external_id", flat=True)
# new_entries = []
# for entry_data in items:
#     entry = {}
#     entry["external_id"] = entry_data["contentDetails"]["videoId"]
#     entry["integration_source"] = "YouTube"
#     entry["title"] = entry_data["snippet"]["title"]
#     entry["description"] = entry_data["snippet"]["description"]
#     entry["import_status"] = "IMPORTED"
#     entry["channel_title"] = entry_data["snippet"]["channelId"]
#     entry["media_url"] = "https://www.youtube.com/watch?v={0}".format(entry["external_id"])
#     entry["thumbnail_url"] = entry_data["snippet"]["thumbnails"]["default"]["url"]
#     entry["published_at"] = entry_data["snippet"]["publishedAt"]
#     durationMs = get_timestamp_for_video(383, entry["external_id"])
#     entry["media_length_ms"] = durationMs
    
#     if not entry["external_id"] in existing_entries:
#         new_entries.append(entry)

# for entry in new_entries:
#     u = User.objects.get(id=383)
#     created_entry, created = Entry.objects.get_or_create(user=u, **entry)


# from django.db.models import Count

# duplicate_external_ids = []
# dups = (
#     Entry.objects.values_list('external_id').annotate(count=Count('external_id')).values_list('external_id').filter(count__gt=2)
# )
# for dup in dups:
#     duplicate_external_ids.append(dup[0])
# print(duplicate_external_id)

# mark_as_deleted = []
# for ext_id in duplicate_external_ids:
#     entries = Entry.objects.filter(external_id=ext_id).order_by()
#     first_entry = entries.first()
#     duplicate_entries = entries.exclude(id=first_entry.id)
#     detest = duplicate_entries.first()
#     detest.is_deleted = True
#     duplicate_ids = list(duplicate_entries.values_list("id", flat=True))
#     mark_as_deleted.append(duplicate_ids)

# import itertools
# print(list(itertools.chain.from_iterable(mark_as_deleted)))

# This will return a ValuesQuerySet with all of the duplicate names. However, you can then use this to construct a regular QuerySet by feeding it back into another query. The django ORM is smart enough to combine these into a single query:

# Entry.objects.filter(external_id__in=dups)

# for dup in dupes:

