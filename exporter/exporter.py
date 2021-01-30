import time
import json
import requests
from datetime import datetime
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY, UnknownMetricFamily

url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/BR/BRL/pt-BR/GRU-sky/EZE-sky/2021-09/2021-09"
headers = {
    'x-rapidapi-key': "key"
}

def export_quotes(quotes):
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    
    places = {}

    for place in response.get('Places'):
        places[place.get('PlaceId')] = place.get('CityName')

    for quote in response.get('Quotes'):
        origin = places.get(quote.get('OutboundLeg').get('OriginId'))
        destination = places.get(quote.get('OutboundLeg').get('DestinationId'))
        return_date = datetime.fromisoformat(quote.get('InboundLeg').get('DepartureDate')).strftime('%d/%m/%Y')
        outbound_date = datetime.fromisoformat(quote.get('OutboundLeg').get('DepartureDate')).strftime('%d/%m/%Y')
        quote_time = datetime.fromisoformat(quote.get('QuoteDateTime'))
        price = str(quote.get('MinPrice'))

        if quote_time.date() == datetime.now().date():
            quotes.add_metric([origin, destination, outbound_date, return_date], price)


class CustomCollector(object):
    def collect(self):
        labels = ['origin', 'destination', 'outbound_date', 'return_date'] #outbound = ida, inbound = volta
        quotes = GaugeMetricFamily('quotes', 'Airfare Prices', labels=labels)

        export_quotes(quotes)

        yield quotes

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    port = 8000
    start_http_server(port)

    REGISTRY.register(CustomCollector())

    while True: time.sleep(1)
