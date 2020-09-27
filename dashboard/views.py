from django.http import JsonResponse
from django.views import View
from pytrends.request import TrendReq

pytrends = TrendReq()


class TrendView(View):

    def get(self, request):
        query = request.GET.get('q', 'anime')
        t = request.GET.get('t', 'now 7-d')
        pytrends.build_payload(kw_list=[query, ], timeframe=t)
        trends = pytrends.related_topics()
        response = JsonResponse(trends[query]['rising'])
        response['Content-Type'] = 'application/json'
        return response
