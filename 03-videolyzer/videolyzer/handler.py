import os
import json
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
        },
        NotificationChannel={
            'SNSTopicArn': os.environ['REKOGNITION_SNS_TOPIC_ARN'],
            'RoleArn': os.environ['REKOGNITION_ROLE_ARN']
        }
        )

    return

def get_video_labels(job_id):
    rekognition_client = boto3.client('rekognition')

    response = rekognition_client.get_label_detection(JobId=job_id)

    next_token = response.get('NextToken', None)

    while next_token:
        next_page = rekognition_client.get_label_detection(
            JobId=job_id,
            NextToken=next_token
        )

        next_token = next_page.get('NextToken', None)

        response['Labels'].extend(next_page['Labels'])

    return response

def make_item(data):
    if isinstance(data, dict):
        return { k: make_item(v) for k, v in data.items() }

    if isinstance(data, list):
        return [ make_item(v) for v in data ]

    if isinstance(data, float):
        return str(data)

    return data


def put_labels_in_db(data, video_name, video_bucket):
    del data['ResponseMetadata']
    del data['JobStatus']

    data['videoName'] = video_name
    data['videoBucket'] = video_bucket

    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['DYNAMODB_TABLE_NAME']
    videos_table = dynamodb.Table(table_name)

    data = make_item(data)

    videos_table.put_item(Item=data)

    return

# Lambda events
## Triggered when a new video is uploaded to the created S3 bucket (in serverless.yml) 
def start_processing_video(event, context):
    for record in event['Records']:
        bucketName = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        start_label_detection(
            bucketName,
            key
        )
    return



## Automatically triggered when the notification in start_label_detection is published to the created SNS topic (in serverless.yml)
def handle_label_detection(event, context):
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        job_id = message['JobId']
        s3_object = message['Video']['S3ObjectName']
        s3_bucket = message['Video']['S3Bucket']

        response = get_video_labels(job_id)
        put_labels_in_db(response, s3_object, s3_bucket)

    return