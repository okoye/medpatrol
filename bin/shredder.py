'''
Ideally the shredder service performs the following:
    1. Spam detection
    2. Business anti-cheat detection
    3. Persist and retrieve messages from datastore
'''
import os
import zmq
import json
import couchdbkit
from couchdbkit.designer import push
from a.message import Flag
from datetime import datetime

class SpamDetection:pass

class AntiCheat(object):pass

class Persistence(object):

    def __init__(self):
        # handle zmq setup
        zmq_port = os.environ['PERSIST_RESPONSE_PORT']
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        self.socket = socket


        # now, setup couchdb
        db_port = os.environ.get('COUCH_PORT', '5984')
        db_server = os.environ.get('COUCH_HOST', '127.0.0.1')
        views_path = os.environ['COUCH_VIEWS_LOCATION']
        couch = couchdbkit.Server(uri='http://%s:%s' % (db_server, db_port))
        db = couch.get_or_create_db('flags')
        push(views_path, db)
        Flag.set_db(db)

    def store(self, message):
        '''
        Store messages flagging a business
        format of message:
            {
                'business_id': ----
                'drug': ---
            }
        Message should be a dictionary object
        '''
        flag = Flag(business_id=message['business_id'],
                    drug_name=message.get('drug_name', 'Unspecified',
                    date=datetime.utcnow()))
        flag.save()


    def retreive(self, business):
        '''
        Given a particular business ID, retrieve all flags
        if any associated with the business.
        '''
        flag_results = Flag.view('flag/business', key=business)
        flags = []
        for flag in flag_results:
            flags.append(flag)
        return flags


    def process(self):
        '''
        Actually processor that does a the request-reply cycle
        '''
        while True:
            message = self.socket.recv()
            logging.debug('received new message')

            # decode to determine type using additional metadata in message
            try:
                decoded = json.loads(from_base64(message))
            except Exception as ex:
                logging.error('failed to decode a message, dropping silently')
            else:
                if 'flag' in decoded:
                    self.store(decoded)
                elif 'check' in decoded:
                    flags = self.retrieve(decoded['business_id'])
                    encoded = to_base64(flags)
                    self.socket.send(encoded)
                else:
                    logging.warn('unidentified message sent')

if __name__ == '__main__':
    persistence = Persistence()
    persistence.process()
