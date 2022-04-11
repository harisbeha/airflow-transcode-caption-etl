import requests

def wistia_settings(request):
    template = loader.get_template('integrations/wistia/wistia_settings.html')
    context = {}
    return HttpResponse(template.render(context, request))

    
def sync_wistia_entries(request):
    user = request.user
    entries = sync_entries_for_user(user)
    return HttpResponseRedirect('/library')

def sync_entries_for_user(user):
    media_list_url = "https://api.wistia.com/v1/medias.json"
    wistia_auth = WistiaAuth.objects.get(user=user)
    api_key = wistia_auth.api_key
    querystring = {"access_token": api_key,"page":"1","per_page":"10"}
    payload = ""
    response = requests.request("GET", url, data=payload, params=querystring)
    create_entries_from_results(user, response)
    return created_entries
  
def create_entries_from_results(user, results):
    created_entries = []
    for entry in results:
        try:
            entry_id = create_entry_from_wistia_result(user, entry)
            created_entries.append(entry_id)
        except Exception as e:
            print(e)
    return created_entries

def get_thumbnail_from_result(entry_data):
    thumbnail_data = entry_data.get("thumbnail", {})
    thumbnail_url = thumbnail_data.get("url", "")
    return thumbnail_url
        

def get_media_from_result(entry_data):
    media_assets = entry_data.get("assets", {})
    media_url = ""
    for asset in media_assets:
        media_type = asset.get("type")
        if media_type = "HdMp4VideoFile":
            media_url = asset.get("url", "")
    return media_url

def create_entry_from_wistia_result(user, entry_data):
    from library.models import Entry
    
    thumbnail_url = get_thumbnail_from_result(entry_data)
    media_url = get_media_from_result(entry_data)
    entry = {
        "external_id": entry_data.get("hashed_id"),
        "integration_source": "Wistia",
        "channel_title": entry_data.get("channel_title", "Wistia"),
        "media_url": media_url,
        "thumbnail_url": thumbnail_url,
        "thumbnail_html": entry_data.get("thumbnail_html"),
        "media_length_ms": entry_data.get("duration", 9999),
        "published_at": entry_data.get("published_at"),
        "media_length_ms": entry_data.get("duration", 9999),
        "title": entry_data.get("name", "Wistia - Untitled"),
        "import_status": "IMPORTED",
        "description": entry_data.get("description"),
    }
    created_entry, created = Entry.objects.get_or_create(user=user, **entry)
    return entry["external_id"]
