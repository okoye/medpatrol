import unittest
import json
from lib.a.coder import to_base64, from_base64

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
