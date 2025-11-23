from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("watchlist/add/", views.add_watchlist, name="add_watchlist"),
    path("watchlist/remove/", views.remove_watchlist, name="remove_watchlist"),
    path('send_graph_email/', views.send_graph_email, name='send_graph_email'),
]
