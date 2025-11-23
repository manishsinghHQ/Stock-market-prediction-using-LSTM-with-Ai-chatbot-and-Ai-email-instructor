from django.urls import path
from . import views
from . import api


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login_custom'),
    path('logout/', views.logout_view, name='logout_custom'),
    path('watchlist/add/', views.add_watchlist, name='add_watchlist'),
    path('watchlist/remove/', views.remove_watchlist, name='remove_watchlist'),
    path("api/history/<str:ticker>/", api.stock_history, name="stock_history"),
    path("api/predict/<str:ticker>/", api.predict_price, name="predict_price"),
    path("api/chatbot/", api.chatbot, name="chatbot"),
    path("api/watchlist/add/", api.add_watchlist, name="add_watchlist"),
    path("api/watchlist/remove/", api.remove_watchlist, name="remove_watchlist"),
]
