'''
The crawling service.

Primarily responsible for fetching all mentions from twitter

Assumptions:
    Some external polling mechanism will call this routine every n  seconds
    TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET
    TWITTER_TOKEN_KEY and TWITER_TOKEN_SECRET are available in environment

    Also, the zero mq port ZMQ_REQUEST_PORT must be set
'''
import os
import zmq
import twitter
import logging
from a.coder import to_base64, from_base64

class Twitter(object):

    def __init__(self):
        ckey = os.environ['TWITTER_CONSUMER_KEY']
        csecret = os.environ['TWITTER_CONSUMER_SECRET']
        tkey = os.environ['TWITTER_TOKEN_KEY']
        tsecret = os.environ['TWITTER_TOKEN_SECRET']
        self.api = twitter.Api(consumer_key=ckey,
                                consumer_secret=csecret,
                                access_token_key=tkey,
                                access_token_secret=tsecret)
        zmq_port = os.environ['FIREHOSE_REQUEST_PORT']
        context = zmq.Context()
        logging.info('Setting up ZeroMQ port at %s' % zmq_port)
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://localhost:%s' % zmq_port)
        self.socket = socket
        self.topic = os.environ.get('TWITTER_PLUCKER','firehose.twitter')

    def crawl(self, state):
        '''
        Contact twitter, retrieve all most recent mentions and throw into message q

        state - dictionary containing state info.
        '''
        mentions = self.api.GetMentions(since_id=state.get('since_id', None))
        for status in mentions:
            encoded_msg = to_base64(status.AsJsonString())
            logging.debug('sending to zeromq frontend')
            self.socket.send(encoded_msg)
            reply = self.socket.recv() # reply is sweet or sour
            logging.debug('received message from zmq backend')
            reply = from_base64(reply)
            if reply == 'sweet':
                self.api.CreateFavorite(status)
            elif reply == 'sour':
                logging.warn('cannot understand message [%s]' % status.text)
            else:
                logging.error('emmm...protocol fail')


def runner():
    twitter = Twitter()
    twitter.crawl(dict())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    runner()




