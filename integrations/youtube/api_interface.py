
class YoutubeApiIntegration(object):
    """
    API integration for YouTube v3.
    """

    def __init__(self, service=None):
        # If no service is passed in, build an unauthenticated service connector
        if service is None:
            service = build(
                YOUTUBE_API_SERVICE_NAME,
                YOUTUBE_API_VERSION,
                developerKey=settings.YOUTUBE_API_KEY
            )

        self.service = service

    @classmethod
    def access_as_user(cls, internal_user_user, youtube_account):
        """
        Create a YoutubeApiIntegration object that is authenticated to access
        the youtube account as the internal_user user.
        :param internal_user_user: The MyDomain account username.
        :param youtube_account: The YouTube account UUID.
        :return: An authenticated YoutubeApiIntegration object.
        """
        transport = YoutubeOAuth(internal_user_user)
        service = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            http=transport
        )

        return cls(service=service)

    @classmethod
    def access_with_credentials(cls, credentials):
        """
        Create a YoutubeApiIntegration object that is authenticated to access
        the youtube account as the internal_user user.
        :param credentials: An OAuth2Credentials object holding the credentials
            for the new youtube account.
        :return: An authenticated YoutubeApiIntegration object.
        """
        transport = credentials.authorize(Http())
        service = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            http=transport
        )

        return cls(service=service)

    def call_api(self, service_type, method_type, id, params):
        """
        It's a helper method for calling google API's and catching the exceptions.
        :param service_type: Type of the service for example: videos, captions.
        :type service_type: string
        :param method_type: Method type on the service for example: list, update.
        :type method_type: string
        :param id: The ID of the Youtube resource, for example: video_id, channel_id, playlist_id
        :type id: string
        :param params: Parameters passed to the endpoint.
        :type params: object
        :return: Response from given query.
        :rtype: json
        """
        assert service_type in ('videos', 'captions', 'channels', 'playlists', 'playlistItems')
        assert method_type in ('list', 'update', 'insert')
        assert params and isinstance(params, dict)

        try:
            service_type = getattr(self.service, service_type)()
            response = getattr(service_type, method_type)(**params).execute()
        except Exception as e:
            error_details = json.loads(e.content)
            try:
                error_reason = error_details['error']['errors'][0]['reason']
            except KeyError:
                error_reason = ''

            if e.resp.status == 400:
                raise YouTubeInvalidRequest(id)
            elif e.resp.status == 403:
                raise YouTubePermissionDenied(id)
            elif e.resp.status == 404 and error_reason == 'captionNotFound':
                raise YouTubeCaptionNotFound(id)
            elif e.resp.status == 404:
                raise Exception(id)
            elif e.resp.status == 409:
                raise YouTubeCaptionAlreadyExists(id)
            else:
                raise YouTubeException(id)
        return response

    def get_video_title(self, video_id):
        """
        Get title of the video from given id of the video.
        :param video_id: The ID of the Youtube video.
        :type video_id: string
        :return: The title of the video.
        :rtype unicode
        Raises:
          Exception: If the returned list is empty.
        """
        video_data = self.call_api(
            service_type='videos',
            method_type='list',
            id=video_id,
            params={'part': 'id,snippet', 'id': video_id},
        )
        if not video_data.get('items', []):
            raise Exception(video_id)

        assert len(video_data.get('items')) == 1
        return video_data['items'][0]['snippet']['title']

    def has_access(self, video_id):
        """
        Check if a user have a access to a specific video.
        :param video_id: The ID of the Youtube video.
        :type video_id: str
        :return: True if we have access to the target video.
        :rtype bool
        """
        video_data = self.call_api(
            service_type='videos',
            method_type='list',
            id=video_id,
            params={'part': 'id,snippet', 'id': video_id},
        )
        return len(video_data.get('items', [])) == 1

    def has_access_to_source(self, source_id, source_type):
        """
        Check if a user has access to a specific source.
        :param source_id: The ID of the source
        :param source_type: The type of the source
        :return: True if we have access to the source
        """
        assert source_type in YouTubeSourceTypeEnum.get_values(),\
            'has_access_to_source called with an invalid type of {}'.format(source_type)

        if source_type == YouTubeSourceTypeEnum.CHANNEL:
            service_type = 'channels'
        elif source_type == YouTubeSourceTypeEnum.PLAYLIST:
            service_type = 'playlists'

        source_data = self.call_api(
            service_type=service_type,
            method_type='list',
            id=source_id,
            params={'part': 'id', 'id': source_id}
        )
        return len(source_data.get('items', [])) == 1

    def add_tags(self, video_id, tags=None):
        """
        Add the tags for video with id video_id. We adding tags if they
        don't already exist. If they exist we are merging them to fit google
        tags limit.
        :param video_id: ID of the video that we want to modify..
        :param tags: List of tags to add to the video.
        """
        if not tags and not isinstance(tags, list):
            raise YouTubeMissingTags(
                'You have to specify list of tags to add.'
            )

        video_data = self.call_api(
            service_type='videos',
            method_type='list',
            id=video_id,
            params={'part': 'id,snippet', 'id': video_id},
        )

        if not video_data.get('items', []):
            raise Exception(video_id)

        assert len(video_data.get('items')) == 1
        snippet = video_data['items'][0]['snippet']

        if 'tags' not in snippet:
            snippet['tags'] = []

        tags_added, could_not_add_tags, duplicate_tags, updated_list_of_tags = \
            add_video_tags(snippet['tags'], tags)

        if tags_added:
            snippet['tags'] = updated_list_of_tags
            self.call_api(
                service_type='videos',
                method_type='update',
                id=video_id,
                params={
                    'part': 'snippet',
                    'body': {
                        'snippet': snippet,
                        'id': video_id
                    }
                })

        return tags_added, could_not_add_tags, duplicate_tags, updated_list_of_tags

    def list_captions(self, video_id):
        """
        List all the captions for a video
        """
        caption_list = self.call_api(
            service_type='captions',
            method_type='list',
            id=video_id,
            parms={'part': 'id,snippet'}
        )

        return [caption['id'] for caption in caption_list['items']]

    def set_caption(self, video_id, caption, language, caption_title=None):
        """
        Add or update the caption track for the given video, setting language as appropriate.
        :param video_id: The ID that YouTube uses to uniquely identify the video associated with the caption track.
        :param caption: The caption track as a bytestring.
        :param language: The language of the caption track, in the form of a BCP-47 language tag.
        :param caption_title: The title of the caption track.
        :return: The caption track ID.
        """
        # Youtube API has a file size max for captions
        assert(sys.getsizeof(caption) <= YOUTUBE_CAPTION_MAX_LENGTH_BYTES)

        existing_caption_id = None

        # Check whether there already exists a caption track for this video
        # with the same language and title.
        caption_data = self.call_api(
            service_type='captions',
            method_type='list',
            id=video_id,
            params={'part': 'id,snippet', 'videoId': video_id}
        )

        for caption_track in caption_data.get('items'):
            if caption_track['snippet']['language'] == language and \
               caption_track['snippet']['name'] == caption_title:
                existing_caption_id = caption_track['id']
                break

        # Ensure that caption is a byte string instead of unicode.
        if isinstance(caption, unicode):
            caption = caption.encode('utf-8')

        # Ensure that caption title is a byte string instead of unicode.
        if isinstance(caption_title, unicode):
            caption_title = caption_title.encode('utf-8')

        # media_body needs to be a filename or a subclass of apiclient.http.MediaUpload.
        # Since we do not want to pass in a filename, we need to use the
        # MediaIoBaseUpload class here.
        file_handler = io.BytesIO(caption)
        caption_media = MediaIoBaseUpload(file_handler, mimetype='application/octet-stream')

        if existing_caption_id:
            # Update this caption track.
            response = self.call_api(
                service_type='captions',
                method_type='update',
                id=video_id,
                params={
                    'part': 'id',
                    'body': {'id': existing_caption_id},
                    'media_body': caption_media,
                })
        else:
            # Insert a new caption track.
            response = self.call_api(
                service_type='captions',
                method_type='insert',
                id=video_id,
                params={
                    'part': 'snippet',
                    'body': {
                        'snippet': {
                            'videoId': video_id,
                            'language': language,
                            'name': caption_title,
                        }
                    },
                    'media_body': caption_media,
                })

        return response['id']

    def get_my_channel_info(self):
        """
        Get information about user channel.
        :returns: ID and title of the first channel.
        :rtype: dict
        """
        channels_data = self.call_api(
            service_type='channels',
            method_type='list',
            id='channel info',
            params={'part': 'id,snippet', 'mine': True}
        )

        if not channels_data.get('items', []):
            raise Exception()

        channel = channels_data['items'][0]
        return {
            'name': channel['snippet']['title']
        }

    def get_playlist_id_from_channel(self, channel_id):
        """
        Get the id of the uploads playlist from the channel with the given channel id.
        :param channel_id: Id of the YouTube channel.
        :return: The playlist id that can be used to list uploaded videos.
        """
        channel_data = self.call_api(
            service_type='channels',
            method_type='list',
            id=channel_id,
            params={'part': 'contentDetails', 'id': channel_id}
        )
        if len(channel_data.get('items', [])) != 1:
            return None

        return channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    def get_videos_in_playlist(self, playlist_id):
        """
        Get list of videos in a play list.
        :param playlist_id: ID of the playlist.
        """
        playlist_list_params = {
            'part': 'snippet,contentDetails',
            'maxResults': YOUTUBE_VIDEOS_PER_PAGE,
            'playlistId': playlist_id,
        }
        while True:
            playlist_info = self.call_api(
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

    def get_video_status_details(self, video_id):
        """
        Gets details about the video status.
        :param video_id: youtube video id
        :return: details about video
        :rtype: dict in the format:
        {
            "uploadStatus": string,
            "failureReason": string,
            "rejectionReason": string,
            "privacyStatus": string,
            "publishAt": datetime,
            "license": string,
            "embeddable": boolean,
            "publicStatsViewable": boolean
        }
        (ref: https://developers.google.com/youtube/v3/docs/videos)
        """
        video_list_params = {
            'part': 'status',
            'id': video_id
        }

        video_details = self.call_api(
            service_type='videos',
            method_type='list',
            id=video_id,
            params=video_list_params
        )

        if len(video_details.get('items', [])) != 1:
            raise Exception(video_id)

        return video_details['items'][0]['status']