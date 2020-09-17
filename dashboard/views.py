from urllib.parse import quote_plus

from django.http import HttpResponse
from django.views import View
from pytrends.request import TrendReq


class TrendView(View):

    def get(self, request):
        query = request.GET.get('q', 'anime')
        # if not query:
        #     return HttpResponseBadRequest()
        keywords = [query, ]

        pytrends = TrendReq()
        pytrends.build_payload(kw_list=keywords, timeframe='now 1-d')

        output = ""

        for kw in keywords:
            data = pytrends.related_topics()[kw]  # .tail(25)
            rising, top = data['rising'], data['top']
            output += rising.to_html()
            output += f"""https://yandex.ru/images/search?text={quote_plus(rising.iloc[0].topic_title)}%20logo"""
        response = HttpResponse(output)
        # response['Content-Type'] = 'application/json'
        return response
        # return render(request, 'trend.html', {'object_list': output})
