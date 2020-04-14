# -*- coding: utf-8 -*-
import decimal
import time
import boto3
import random
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
PASSCODES_TABLE_NAME = "passcodes"
VISITORS_TABLE_NAME = "visitors"
EXPIRED_TIME = 60 * 5  # 5 minutes


__all__ = ["store_passcode", "store_visitor", "get_visitor_by_faceid", "get_passcode", "generate_otp"]


def decode_decimal(item):
    for key, value in item.items():
        if isinstance(value, decimal.Decimal):
            if value % 1 > 0:
                item[key] = float(value)
            else:
                item[key] = int(value)
        elif isinstance(value, dict):
            decode_decimal(value)
        elif isinstance(value, list):
            for i in value:
                decode_decimal(i)
        elif not isinstance(value, str):
            raise Exception("Unrecognized type: {}".format(type(value)))


def put_item(table_name, item):
    table = dynamodb.Table(table_name)
    try:
        response = table.put_item(Item=item)
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise


def get_item(table_name, key):
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise

    if 'Item' in response:
        decode_decimal(response['Item'])
        return response['Item']
    return None


def store_passcode(passcode: str):
    """Store a new passcode for visitor with faceid"""
    assert isinstance(passcode, str), "Passcode must be of type str"

    item = {
        "passcode": passcode,
        "expirationTime": str(time.time()+EXPIRED_TIME)
    }
    put_item(PASSCODES_TABLE_NAME, item)


def get_passcode(passcode: str):
    """Check if for visitor with faceId, exists a passcode
    Return:
    {
        "faceid": faceid,
        "passcode": passcode
    }
    or None if passcode not exists
    """
    assert isinstance(passcode, str), "Passcode must be of type str"

    item = get_item(PASSCODES_TABLE_NAME, {"passcode": passcode})

    return item


def store_visitor(visitor: dict):
    assert isinstance(visitor, dict), "visitor must be of type dict"
    put_item(VISITORS_TABLE_NAME, visitor)


def get_visitor_by_faceid(faceid: str):
    """Return None if not exist"""
    assert isinstance(faceid, str), "faceid must be of type str"
    return get_item(VISITORS_TABLE_NAME, {"faceId": faceid})


def generate_otp():
    return str(random.randint(10**6, 10**7-1))
