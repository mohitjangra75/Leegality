from rest_framework import serializers
from .models import Node, Edge, RouteQuery


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['id', 'name']


class EdgeSerializer(serializers.Serializer):
    source = serializers.CharField()
    destination = serializers.CharField()
    latency = serializers.FloatField()

    def validate_latency(self, value):
        if value <= 0:
            raise serializers.ValidationError("Latency must be greater than 0.")
        return value

    def validate(self, data):
        if data['source'] == data['destination']:
            raise serializers.ValidationError("Source and destination cannot be the same.")
        return data


class EdgeResponseSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='source.name')
    destination = serializers.CharField(source='destination.name')

    class Meta:
        model = Edge
        fields = ['id', 'source', 'destination', 'latency']


class ShortestRouteRequestSerializer(serializers.Serializer):
    source = serializers.CharField()
    destination = serializers.CharField()


class RouteQuerySerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='source.name')
    destination = serializers.CharField(source='destination.name')

    class Meta:
        model = RouteQuery
        fields = ['id', 'source', 'destination', 'total_latency', 'path', 'created_at']
