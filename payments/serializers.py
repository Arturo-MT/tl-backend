from rest_framework import serializers

class MyCheckoutSerializer(serializers.Serializer):
    def get_serializer_class(self):
        return MyCheckoutSerializer

class MyWebhookSerializer(serializers.Serializer):
    def get_serializer_class(self):
        return MyWebhookSerializer