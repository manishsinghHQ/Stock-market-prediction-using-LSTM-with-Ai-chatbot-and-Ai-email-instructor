from django.contrib import admin

# Register your models here.
from .models import WatchlistItem, Preference

@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'added_at')
    list_filter = ('ticker',)

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_ticker')
