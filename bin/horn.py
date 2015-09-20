'''
Responsible for conducting searches on ES to find certain entities
'''

import os
import json
import zerorpc
import logging
import elasticsearch
from a.coder import to_base64, from_base64

class Searcher(object):

    def __init__(self):
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
                "pin.location": location
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
        raw_results = self._es.search(index='pharmacies', body=query)
        results = {}
        for i, hit in doc_hits(raw_results):
            results[i] = hit

        logging.info('search term generated %d hits' % i)
        return results

    def process(self, message):
        '''
        Actual processor that does a request-reply
        '''
        logging.debug('received a new search request')
        try:
            decoded = json.loads(from_base64(message))
        except Exception as ex:
            logging.error('failed to decode search request')
            print ex
            return None
        else:
            response = self.search(decoded)
            return to_base64(response)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    s = zerorpc.Server(Searcher())
    port = os.environ['HORN_PORT']
    s.bind('tcp://0.0.0.0:%s'%port)
    s.run()
