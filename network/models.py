from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Edge(models.Model):
    source = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name='outgoing_edges'
    )
    destination = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name='incoming_edges'
    )
    latency = models.FloatField()

    class Meta:
        unique_together = ('source', 'destination')

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name} ({self.latency})"


class RouteQuery(models.Model):
    source = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name='route_queries_as_source'
    )
    destination = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name='route_queries_as_destination'
    )
    total_latency = models.FloatField()
    path = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name} ({self.total_latency})"
