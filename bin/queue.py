'''
A ZeroMQ queue device

Assumptions:
    ZMQ_REQUEST_PORT and ZMQ_RESPONSE_PORT set in env vars
'''
import os
import zmq
import logging

def run_forever():
    try:
        rep_port = os.environ['ZMQ_RESPONSE_PORT']
        req_port = os.environ['ZMQ_REQUEST_PORT']
        logging.info('device listening on %s and %s' % (rep_port, req_port))
        context = zmq.Context(1)
        frontend = context.socket(zmq.XREP)
        frontend.bind('tcp://*:%s'%rep_port)
        backend = context.socket(zmq.XREQ)
        backend.bind('tcp://*:%s'%req_port)

        logging.info('starting device')
        zmq.device(zmq.QUEUE, frontend, backend)
    except Exception as ex:
        logging.error(ex)
        logging.warn('shutting down ZMQ port')
    finally:
        frontend.close()
        backend.close()
        context.term()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_forever()
