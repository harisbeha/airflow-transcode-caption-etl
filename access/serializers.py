from rest_framework.serializers import ModelSerializer
from access.models import AccountConfiguration, AccessToken
from django.contrib.auth.models import User

class AccountConfigurationSerializer(ModelSerializer):
    class Meta:
        model = AccountConfiguration
        fields = '__all__'


class AccessTokenSerializer(ModelSerializer):
    class Meta:
        model = AccessToken
        fields = '__all__'

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'