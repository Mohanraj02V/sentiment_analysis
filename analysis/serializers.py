from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SentimentAnalysis

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user

class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentAnalysis
        fields = ('id', 'text', 'sentiment', 'confidence', 'raw_score', 'created_at')
        read_only_fields = ('user', 'sentiment', 'confidence', 'raw_score', 'created_at')