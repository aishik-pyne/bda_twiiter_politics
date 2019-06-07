from django.contrib import admin
from livetweets.models import TweetDumps, TweetCountSummary
# Register your models here.
admin.site.register(TweetDumps)
admin.site.register(TweetCountSummary)
