from django.db import models
from django.contrib.auth.models import User

class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_ticker = models.CharField(max_length=16, blank=True, default="AAPL")

class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    ticker = models.CharField(max_length=16)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "ticker")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username}:{self.ticker}"


# Create your models here.
