from django.urls import path
from . import api
app_name = "api"


urlpatterns = [
    path("stock/<str:ticker>/history/", api.stock_history, name="stock_history"),
    path("predict/<str:ticker>/", api.predict_price, name="predict_price"),
    path("chatbot/", api.chatbot, name="chatbot"),

    path("watchlist/", api.watchlist, name="watchlist"),
   
]
