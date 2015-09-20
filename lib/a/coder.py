'''
Simple serialization library for Zero-MQ messages
'''

import base64

def to_base64(message):
    '''
    Zero-MQ expects a string
    '''
    return base64.b64encode(message)

def from_base64(encoded_message):
    '''
    Application expects a JSON string
    '''
    return base64.b64decode(encoded_message)
