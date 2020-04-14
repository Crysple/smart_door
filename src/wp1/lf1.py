import json
from utils import *
import boto3

# db2 schema
# {
#     “faceId”: “{UUID}”,
#     “name”: “Jane Doe”,
#     “phoneNumber”: “+12345678901”, 
#     “photos”: [
#         {
#             “objectKey”: “my-photo.jpg”, 
#             “bucket”: “my-photo-bucket”, 
#             “createdTimestamp”: “2018-11-05T12:40:02” 
#         }
#         ]
# }

# event = {
#     "access": boolean,
#     "name": string,
#     "phone": string
# }

def sendSMS(phone_num, message):
    client = boto3.client('sns')
    response = client.publish(
        PhoneNumber = phone_num,
        Message = message
    )
    print("message success")

def lambda_handler(event, context):
    
    access = event["access"]
    if access:
        faceId = event["faceid"] 
        name = event["name"]
        phone_num = event["phone"]
        bucket = event["bucket"]
        
        if phone_num[:2]!="+1":
            phone_num = "+1" + phone_num
        
        otp = generate_otp()
        store_passcode(otp, faceId)
        
        visitor =  {
                        "faceId": faceId,
                        "name": name,
                        "phoneNumber": phone_num, 
                        "photos": [bucket]
                            
                    }
                    
        print(visitor)
        store_visitor(visitor)
        
        # sns access
        send_message = "Hi {}, your otp is {}.".format(name, otp)
        # print(send_message)
        print()
        sendSMS(phone_num, send_message)
        
        
# db2 schema
# {
#     “faceId”: “{UUID}”,
#     “name”: “Jane Doe”,
#     “phoneNumber”: “+12345678901”, 
#     “photos”: [
#         {
#             “objectKey”: “my-photo.jpg”, 
#             “bucket”: “my-photo-bucket”, 
#             “createdTimestamp”: “2018-11-05T12:40:02” 
#         }
#         ]
# }


# test case:
#     {
#   "access": 1,
#   "faceid": "9a6ca8ab-a6bb-45e9-8c42-ac826adfb8b9",
#   "name": "yan",
#   "phone": "43254657768",
#   "bucket": {
#     "objectKey": "Jin.png",
#     "bucket": "detectface",
#     "createdTimestamp": "abc"
#   }
# }