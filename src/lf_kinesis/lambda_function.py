#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import boto3
import json
import time
import base64
import logging
import datetime
import cv2
import random
from utils import *

ACCESSKEY = ""
SECRET_ACCESS_KEY = ""
def unknown_face():
    s3_client = boto3.client('s3')
    print('succeed1')

    kvs_client = boto3.client('kinesisvideo',
                              region_name='us-east-1',
                              aws_access_key_id=ACCESSKEY,
                              aws_secret_access_key=SECRET_ACCESS_KEY)
    kvs_data_pt = kvs_client.get_data_endpoint(
        StreamARN="arn:aws:kinesisvideo:us-east-1:415865090458:stream/hw2/1584652513088", # kinesis stream arn
        APIName='GET_MEDIA'
    )
    print('succeed2')
    
#print(kvs_data_pt)
    
    end_pt = kvs_data_pt['DataEndpoint']
    kvs_video_client = boto3.client('kinesis-video-media', endpoint_url=end_pt, region_name='us-east-1') # provide your region
    kvs_stream = kvs_video_client.get_media(
        StreamARN="arn:aws:kinesisvideo:us-east-1:415865090458:stream/hw2/1584652513088", # kinesis stream arn
        StartSelector={'StartSelectorType': 'NOW'} # to keep getting latest available chunk on the stream
    )
#print(kvs_stream)
    print('succeed3')
    with open('/tmp/stream.mkv', 'wb') as f: 
        print('succeed4')
        streamBody = kvs_stream['Payload'].read(512*512)
        print('succeed5')# reads min(16MB of payload, payload size) - can tweak this
        f.write(streamBody)
        # use openCV to get a frame
        cap = cv2.VideoCapture('/tmp/stream.mkv')
        print('succeed6')

        # use some logic to ensure the frame being read has the person, something like bounding box or median'th frame of the video etc
        ret, frame = cap.read() 
        print('succeed7')
        cv2.imwrite('/tmp/frame.jpg', frame)
        print('succeed8')
        # s3_client = boto3.client('s3')
        # print('succeed8')
        x = random.randint(1, 100)
        img ="unknown_frame%s.jpg"%x
        # img = 'unknown_frame.jpg'
        s3_client.upload_file(
            '/tmp/frame.jpg',
            'detectface', # replace with your bucket name
            img
            )
        print('succeed9')
        cap.release()
        print("unknown_frame%s.jpg uploaded"%x)
        
    # img_url = "https://" + 'detectface' + ".s3.amazonaws.com/" + img
    # return img_url
    bucket = 'detectface'
    collection_id = 'face'
    unknown_id =add_faces_to_collection(bucket,img,collection_id)
    return unknown_id
    #return img_url
def add_faces_to_collection(bucket,photo,collection_id):


    
    client=boto3.client('rekognition',region_name='us-east-1',
                              aws_access_key_id=ACCESS_KEY,
                              aws_secret_access_key=SECRET_ACCESS_KEY)

    response=client.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                ExternalImageId=photo,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])

    print ('Results for ' + photo) 	
    print('Faces indexed:')						
    for faceRecord in response['FaceRecords']:
         return faceRecord['Face']['FaceId']
    #      print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

    # print('Faces not indexed:')
    # for unindexedFace in response['UnindexedFaces']:
    #     print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
    #     print(' Reasons:')
    #     for reason in unindexedFace['Reasons']:
    #         print('   ' + reason)
    # return len(response['FaceRecords'])

def sendSMS(phone_num, message):
    print("Sending Message: ", message)
    return 
    client = boto3.client('sns')
    response = client.publish(
        PhoneNumber = phone_num,
        # PhoneNumber = '+16462037548',
        Message = message
    )
    print(response)

def get_face(event):
    """Return None, None if it is an unknown user
    Return:
    face:{
        "faceid": "id",
        "bucket":
            {
                “objectKey”: “my-photo.jpg”,
                “bucket”: “my-photo-bucket”,
                “createdTimestamp”: “2018-11-05T12:40:02”
            }
    }
    """
    data = base64.b64decode(event['Records'][0]['kinesis']['data'].encode("UTF-8"))
    data = json.loads(data)
    print(data)
    if len(data["FaceSearchResponse"]) == 0:
        return "No face!"
    elif len(data["FaceSearchResponse"][0]["MatchedFaces"]) == 0:
        return None
    else:
        face = data["FaceSearchResponse"][0]["MatchedFaces"][0]
        faceid = face["Face"]["FaceId"]
        return {
               'faceid': faceid,
               'bucket': {
                    "objectKey": face["Face"]["ExternalImageId"],
                    "bucket": "detectface",
                    "createdTimestamp": str(datetime.datetime.now())
                }
           }


def lambda_handler(event, context):
    res = get_visitor_by_faceid("Hello?")
    if res is not None and time.time() < float(res.get('expiredTime', 0)):
        return
    store_visitor({'faceId': "Hello?", 'expiredTime': str(time.time()+60)})

    face = get_face(event)
    if face == "No face!":
        print("No face detected")
        return
    elif face is None:
        print("face is None")
        faceid = unknown_face()
    else:
        faceid = face["faceid"]
    visitor = get_visitor_by_faceid(faceid)

    #visitor = get_visitor_by_faceid(face["faceid"])
    print('faceid:', faceid)
    if visitor is None:
        link = "http://smartdoorwp1.com.s3-website-us-east-1.amazonaws.com?face={}".format(json.dumps(face))
        msg = "Hello Master, there is a visitor asking for access. Please check via the following link: " + link

        phone_num = "+16464201338"
        print(msg)
        sendSMS(phone_num, msg)
        print("visitor not found")
    elif visitor is not None and 'name' in visitor:
        passcode = generate_otp()
        store_passcode(passcode)
        msg = "Hello {}, your verification code is {}".format(visitor["name"], passcode)
        print(msg)
        sendSMS(visitor["phoneNumber"], msg)
        print("Send SMS to visitor")

