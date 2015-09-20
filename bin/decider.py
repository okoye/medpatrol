'''
Decider, a core application is responsible for the following:
    Entity recognition and parsing
    Identification of class of message
    Routing messages to relevant post-processing services
'''

import os
import zmq
import logging
from a.coder import to_base64, from_base64
from nltk.tag import StanfordNERTagger

class Decider(object):

    def __init__(self):
        firehose_port = os.environ['FIREHOSE_RESPONSE_PORT']
        searcher_port = os.environ['SEARCHER_REQUEST_PORT']
        persist_port = os.environ['PERSIST_REQUEST_PORT']
        outreach_port = os.environ['OUTREACH_REQUEST_PORT']

        # zmq setup
        context = zmq.Context()
        firehose_socket = context.socket(zmq.REP)
        self.firehose_socket = firehose_socket

        # TODO: start enabling services for testing purposes

        # Entity recognition
        ner_classifier = os.environ['NER_CLASSIFIER']
        ner_jar = os.environ['NER_JAR']
        st = StanfordNERTagger(ner_classifier, ner_jar)
        self.entity_engine = st
        logging.info('successfully initialized Stanford NER tagger')
        # TODO: Part of speech tagger (POS)


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

    def process(self):
        '''
        Do request-reply dance
        '''
        while True:
            logging.info('listening for connections')
            message = self.firehose_socket.recv()
            logging.debug('received new message from firehose')

            try:
                decoded = json.loads(from_base64(message))
                tweet = status.Status(**decoded)
            except Exception as ex:
                logging.error('could not decode message, probably corrupted')
                self.socket.send('sour')
            else:
                org, location = self.get_entities(tweet.text)
                if not len(org) or not len(location):
                    self.socket.send('sour')
                else:
                    logging.info('we have identified potential location and org')
                    pass # TODO: contact search API.


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    decider = Decider()
    decider.process()
