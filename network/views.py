from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Node, Edge, RouteQuery
from .serializers import (
    NodeSerializer, EdgeSerializer, EdgeResponseSerializer,
    ShortestRouteRequestSerializer, RouteQuerySerializer,
)
from .utils import dijkstra


def dashboard(request):
    return render(request, 'network/dashboard.html')



@api_view(['GET', 'POST'])
def node_list(request):
    if request.method == 'GET':
        nodes = Node.objects.all()
        return Response(NodeSerializer(nodes, many=True).data)

    serializer = NodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def node_delete(request, pk):
    node = get_object_or_404(Node, pk=pk)
    node.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
def edge_list(request):
    if request.method == 'GET':
        edges = Edge.objects.select_related('source', 'destination')
        return Response(EdgeResponseSerializer(edges, many=True).data)

    serializer = EdgeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data

    src = Node.objects.filter(name=d['source']).first()
    dst = Node.objects.filter(name=d['destination']).first()

    if not src:
        return Response({"error": f"Source node '{d['source']}' not found."}, status=400)
    if not dst:
        return Response({"error": f"Destination node '{d['destination']}' not found."}, status=400)
    if Edge.objects.filter(source=src, destination=dst).exists():
        return Response({"error": "Edge already exists between these nodes."}, status=400)

    edge = Edge.objects.create(source=src, destination=dst, latency=d['latency'])
    return Response(EdgeResponseSerializer(edge).data, status=201)


@api_view(['DELETE'])
def edge_delete(request, pk):
    edge = get_object_or_404(Edge, pk=pk)
    edge.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
def shortest_route(request):
    serializer = ShortestRouteRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data

    src = Node.objects.filter(name=d['source']).first()
    dst = Node.objects.filter(name=d['destination']).first()
    if not src:
        return Response({"error": f"Source node '{d['source']}' not found."}, status=400)
    if not dst:
        return Response({"error": f"Destination node '{d['destination']}' not found."}, status=400)

    total_latency, path = dijkstra(src.name, dst.name)
    if total_latency is None:
        return Response(
            {"error": f"No path exists between {src.name} and {dst.name}"}, status=404
        )

    # save to history
    RouteQuery.objects.create(
        source=src, destination=dst,
        total_latency=total_latency, path=path,
    )
    return Response({"total_latency": total_latency, "path": path})


@api_view(['GET'])
def route_history(request):
    qs = RouteQuery.objects.select_related('source', 'destination')

    src = request.query_params.get('source')
    dst = request.query_params.get('destination')
    if src:
        qs = qs.filter(source__name=src)
    if dst:
        qs = qs.filter(destination__name=dst)

    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    if date_from:
        qs = qs.filter(created_at__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__lte=date_to)

    limit = request.query_params.get('limit')
    if limit:
        try:
            qs = qs[:int(limit)]
        except ValueError:
            pass

    return Response(RouteQuerySerializer(qs, many=True).data)
