import json
import boto3
import os
import requests

ELASTIC_SEARCH_ENDPOINT = "URL/index/_type"
ES_USER = ""
ES_PASSWORD = ""


def lambda_handler(event, context):
    # TODO implement

    print("Photo inserted in s3", event)

    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]

    rekognition = boto3.client("rekognition", "us-east-1")
    rekognition_labels = rekognition.detect_labels(Image={"S3Object": {
        "Bucket": bucket_name, "Name": object_key}}, MaxLabels=3, MinConfidence=70)

    print(rekognition_labels)

    labels = list()

    for detected_labels in rekognition_labels["Labels"]:
        labels.append(detected_labels["Name"])

    s3 = boto3.client("s3", "us-east-1")
    object_metadata = s3.head_object(
        Bucket=bucket_name, Key=object_key)

    print(object_metadata)

    if "x-amz-meta-customlabels" in object_metadata["ResponseMetadata"]["HTTPHeaders"]:
        customlabels = object_metadata["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-customlabels"].split(
            ",")
        for c_labels in customlabels:
            c_labels = c_labels.strip()
            c_labels = c_labels.lower()
            if c_labels not in labels:
                labels.append(c_labels)

    print(labels)

    es_query = {
        "objectKey": object_key,
        "bucket": bucket_name,
        "createdTimestamp": event["Records"][0]["eventTime"],
        "labels": labels
    }

    print(es_query)

    response = json.loads(requests.post(ELASTIC_SEARCH_ENDPOINT,
                                        auth=(ES_USER, ES_PASSWORD),
                                        headers={
                                            "Content-Type": "application/json"},
                                        data=json.dumps(es_query)).content.decode('utf-8'))

    print(response)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET',
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps("Image labels have been detected successfully!")
    }
