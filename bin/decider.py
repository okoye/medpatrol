'''
Decider, a core application is responsible for the following:
    Entity recognition and parsing
    Identification of class of message
    Routing messages to relevant post-processing services
'''

import os
import json
import zerorpc
import logging
from twitter import status
from a.coder import to_base64, from_base64
from nltk.tag import StanfordNERTagger

class Decider(object):

    def __init__(self):
        # Entity recognition
        ner_classifier = os.environ['NER_CLASSIFIER']
        ner_jar = os.environ['NER_JAR']
        st = StanfordNERTagger(ner_classifier, ner_jar)
        self.entity_engine = st
        logging.info('successfully initialized Stanford NER tagger')
        # TODO: Part of speech tagger (POS)


        #zrpc clients
        shredder_port = os.environ['SHREDDER_PORT']
        shredder = zerorpc.Client()
        shredder.connect('tcp://localhost:%s' % shredder_port)
        self.shredder = shredder

        horn_port = os.environ['HORN_PORT']
        horn = zerorpc.Client()
        horn.connect('tcp://localhost:%s' % horn_port)
        self.horn = horn

        # TODO: outlook

    def get_entities(self, text):
        '''
        Should return only business (organization names) and locations

        text - string content of the tweet

        Note, we need to do some 'adjustments' and generate possibly other
        substitute strings.
        '''
        def generator(text, aggressive=1):
            '''
            Get new representations of the text. Aggressive levels can be tuned.
            '''
            pass

        # first some cleaning
        text = text.replace('@medpatrol', 'hey')
        entities = self.entity_engine.tag(text.split())
        org = []
        location = []
        for entity, classification in entities:
            if classification == 'LOCATION':
                location.append(entity)
            elif classification == 'PERSON' or classification == 'ORGANIZATION':
                org.append(entity) # needs more training to distinguish better

        if not len(org) or not len(location):
            logging.info('no entities extracted, increasing aggro')
        else:
            return org, location

        #TODO increase aggression levels.
        return ([], [])

    def process(self, message):
        '''
        Do request-reply dance
        '''

        logging.info('received new message from firehose')
        try:
            decoded = json.loads(from_base64(message))
            tweet = status.Status(**decoded)
        except Exception as ex:
            logging.error('could not decode message, probably corrupted')
            return 'sour'
        else:
            org, location = self.get_entities(tweet.text)
            if not len(org) or not len(location):
                return 'sour'
            else:
                logging.info('we have identified potential location and org')
        search_request = {
            'business_name': ' '.join(org),
            'location' : ' '.join(location)
        }
        result = self.horn.process(to_base64(json.dumps(search_request)))
        logging.debug('search finished')

        #TODO: determine what kind of request this is
        return 'sweet'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    s = zerorpc.Server(Decider())
    port = os.environ['DECIDER_PORT']
    s.bind('tcp://0.0.0.0:%s'%port)
    s.run()
