'''
Messages stored by our platform
'''
from couchdbkit import *

class Flag(Document):
    business_id = StringProperty() # uuid4
    drug_name = StringProperty() # drug name
    date = DateTimeProperty()
