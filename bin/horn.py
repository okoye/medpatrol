'''
Responsible for conducting searches on ES to find certain entities
'''

import os
import zmq
import logging
import elasticsearch
from a.coder import to_base64, from_base64

class Searcher(object):

    def __init__(self):
        zmq_port = os.environ['SEARCHER_RESPONSE_PORT']
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        self.socket = socket
        self._business_name_fields = ['business_name', 'other_names']

        # setup elasticsearch
        es_nodes = os.environ.get('ES_HOST', 'localhost')
        self._es = elasticsearch.Elasticsearch(es_nodes,
                sniff_on_start=True)

    def _fuzzy_query(self, business_name):
        '''
        business_name - best effort business name from decider
        '''
        return {
            "fuzzy_like_this": {
                "fields": self._business_name_fields,
                "like_text": business_name
            }
        }

    def _distance_filter(self, location, miles=2):
        '''
        location - long, lat (like GeoJSON)
        '''
        return {
            "geo_distance": {
                "distance": "%smi" % miles,
                "pin.location", location
            }
        }

    def _query(self, location, business_name):
        query = {
            "filtered": {
                "query": self._fuzzy_query(business_name),
                "filter": self._distance_filter(location)
            }
        }
        return query

    def search(self, message):
        '''
        A json dict containing location and business_name parameters
        '''
        if 'location' not in message or 'business_name' not in message:
            return ''
        logging.info('querying for %s' % (message['business_name']))
        query = self._query(message['location'], message['business_name'])
        raw_results = self._es(index='pharmacies', body=query)
        results = {}
        for i, hit in doc_hits(raw_results):
            results[i] = hit

        logging.info('search term generated %d hits' % i)
        return results

    def process(self):
        '''
        Actual processor that does a request-reply cycle
        '''
        while True:
            message = self.socket.recv()
            logging.debug('received new search request')

            try:
                decoded = json.loads(from_base64(message))
            except Exception as ex:
                logging.error('failed to decode a message, continuing')
            else:
                response = self.search(decoded)
                #TODO: we should actually return *most likely* result not multiple
                encoded = to_base64(response)
                self.socket.send(encoded)
