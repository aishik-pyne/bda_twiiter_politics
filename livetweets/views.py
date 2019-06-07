from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from livetweets.models import TweetCountSummary
from django.core.serializers import serialize
# Create your views here.
from pprint import pprint

def index(request):
    return JsonResponse(list(TweetCountSummary.objects.order_by('-time').values()), safe=False)
    # return render(request, 'livetweets/index.html', context)
