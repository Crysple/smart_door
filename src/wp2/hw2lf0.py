import json
import time
from utils import *


def lambda_handler(event, context):
    passcode = event['message']['passcode']
    print(passcode)
    name = 'None'
    item = get_passcode(passcode)
    if item != None and time.time() <= float(item['expirationTime']):
        res = "valid"
        print(get_passcode(passcode))
        name = get_visitor_by_faceid(get_passcode(passcode)['faceId'])['name']
    else:
        res = "not valid"
        
    # TODO implement
    return {
        'statusCode': 200,
        'body': {
            "valid": res, 
            "name": name
        }         # json.dumps('Hello from Lambda!')
    }
