from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('nodes', views.node_list, name='node-list'),
    path('nodes/<int:pk>', views.node_delete, name='node-delete'),

    path('edges', views.edge_list, name='edge-list'),
    path('edges/<int:pk>', views.edge_delete, name='edge-delete'),

    path('routes/shortest', views.shortest_route, name='shortest-route'),
    path('routes/history', views.route_history, name='route-history'),
]
