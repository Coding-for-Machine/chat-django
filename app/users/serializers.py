from rest_framework import serializers

class SendCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()
