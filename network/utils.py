import heapq
from collections import defaultdict
from .models import Edge


def dijkstra(source_name, destination_name):
    edges = Edge.objects.select_related('source', 'destination').all()

    graph = defaultdict(list)
    for edge in edges:
        graph[edge.source.name].append((edge.destination.name, edge.latency))
        graph[edge.destination.name].append((edge.source.name, edge.latency))

    distances = {source_name: 0}
    previous = {}
    heap = [(0, source_name)]
    visited = set()

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == destination_name:
            break

        for neighbor, latency in graph[current_node]:
            if neighbor in visited:
                continue
            new_dist = current_dist + latency
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                previous[neighbor] = current_node
                heapq.heappush(heap, (new_dist, neighbor))

    if destination_name not in distances:
        return None, None

    path = []
    node = destination_name
    while node is not None:
        path.append(node)
        node = previous.get(node)
    path.reverse()

    return round(distances[destination_name], 4), path
