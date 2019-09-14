import urllib

import boto3

def start_label_detection(bucket, key):
    rekognition_client = boto3.client('rekognition')
    response = rekognition_client.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        })

    print(response)

    return

def start_processing_video(event, context):
    print(event)

    return