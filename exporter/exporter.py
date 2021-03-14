import os
import time
import json
import requests
from datetime import datetime
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY, UnknownMetricFamily

url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/BR/BRL/pt-BR/GRU-sky/EZE-sky/2021-09/2021-09"
headers = {
    'x-rapidapi-key': os.environ['rapidapikey']
}

def export_quotes(quotes):
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    
    places = {}
    carriers = {}

    for place in response.get('Places'):
        places[place.get('PlaceId')] = place.get('IataCode')

    for carrier in response.get('Carriers'):
        carriers[carrier.get('CarrierId')] = carrier.get('Name')

    for quote in response.get('Quotes'):
        origin = places.get(quote.get('OutboundLeg').get('OriginId'))
        destination = places.get(quote.get('OutboundLeg').get('DestinationId'))
        return_date = datetime.fromisoformat(quote.get('InboundLeg').get('DepartureDate'))#.strftime('%d/%m/%Y')
        outbound_date = datetime.fromisoformat(quote.get('OutboundLeg').get('DepartureDate'))#.strftime('%d/%m/%Y')
        duration = return_date - outbound_date
        carrier = carriers.get(quote.get('OutboundLeg').get('CarrierIds')[0])
        quote_time = datetime.fromisoformat(quote.get('QuoteDateTime'))
        price = str(quote.get('MinPrice'))

        quote_period = datetime.now() - quote_time
        
        if quote_period.days <= 1:
            quotes.add_metric([origin, destination, outbound_date.strftime('%d/%m/%Y'), return_date.strftime('%d/%m/%Y'), str(duration.days), carrier, quote_time.strftime('%d/%m/%Y')], price)


class CustomCollector(object):
    def collect(self):
        labels = ['origin', 'destination', 'outbound_date', 'return_date', 'duration', 'carrier', 'quote_time'] #outbound = ida, inbound = volta
        quotes = GaugeMetricFamily('quotes', 'Airfare Prices', labels=labels)

        export_quotes(quotes)

        yield quotes

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    port = 8000
    start_http_server(port)

    REGISTRY.register(CustomCollector())

    while True: time.sleep(1)
