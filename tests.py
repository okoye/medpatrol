import unittest
import json
from uuid import uuid4
from datetime import datetime
from lib.a.coder import to_base64, from_base64
from lib.a.message import Flag

class TestSerialization(unittest.TestCase):

    def test_conversion_to_base_64(self):
        doc = {'name': 'chuka',
                'website': 'chookah.org',
                'message': 'hello world'}
        encoded = to_base64(json.dumps(doc))
        # just verify there is no syntactic error really.

        decoded = from_base64(encoded)
        new_doc = json.loads(decoded)

        self.assertTrue('name' in new_doc)
        self.assertTrue('website' in new_doc)
        self.assertTrue('message' in new_doc)

        #TODO: some equals assertion?


class TestMessage(unittest.TestCase):

    def test_a_flag(self):
        message = Flag(business_id=str(uuid4()),
                        drug_name='Chloroquine',
                        date=datetime.utcnow())

        self.assertTrue(hasattr(message, 'business_id'))
        self.assertTrue(hasattr(message, 'drug_name'))
        self.assertTrue(hasattr(message, 'date'))

        #TODO: some equals assertion to ensure no data corruption
