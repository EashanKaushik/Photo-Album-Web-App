import json
import boto3
import os
import requests
import datetime
import time

ELASTIC_SEARCH_ENDPOINT = "URL/index/_type/_search"
ES_USER = ""
ES_PASSWORD = ""


def lambda_handler(event, context):
    print(event)
    query = event["queryStringParameters"]["q"]

    if(query == "searchAudio"):
        query = convert_speechtotext()

    lex = boto3.client("lex-runtime", region_name="us-east-1")

    lex_resp = lex.post_text(
        botName='photoalbum',
        botAlias='photoalbumprod',
        userId='string',
        inputText=query)

    print(lex_resp)

    keywords = list(lex_resp["slots"].values())

    result = list()

    print(keywords)

    for keyword in keywords:

        if keyword is None:
            break

        label = keyword
        print(label)

        es_query = {
            "query": {
                "match": {
                    "labels": label
                }
            }
        }

        print(es_query)

        es_response = json.loads(requests.get(ELASTIC_SEARCH_ENDPOINT,
                                              auth=(ES_USER, ES_PASSWORD),
                                              headers={
                                                  "Content-Type": "application/json"},
                                              data=json.dumps(es_query)).content.decode('utf-8'))

        print(es_response)

        for idx in es_response['hits']['hits']:
            key = idx['_source']['objectKey']
            url_res = "https://photoalbumcloudassignment3.s3.amazonaws.com/"+key

            if (url_res not in result):
                result.append(url_res)

        print(result)

    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,PUT',
            'Access-Control-Allow-Credentials': 'true'
        }
    }


def convert_speechtotext():

    transcribe = boto3.client('transcribe')

    job_name = datetime.datetime.now().strftime("%m-%d-%y-%H-%M%S")
    job_uri = "https://s3-voice-recording-photo-album.s3.amazonaws.com/Recording.wav"
    storage_uri = "s3-voice-output-photo-album"

    s3 = boto3.client('s3')
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='en-US',
        OutputBucketName=storage_uri
    )

    while True:
        status = transcribe.get_transcription_job(
            TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)

    print("Transcript URL: ", status)

    job_name = str(job_name) + '.json'
    print(job_name)
    obj = s3.get_object(Bucket="s3-voice-output-photo-album", Key=job_name)
    print("Object : ", obj)
    body = json.loads(obj['Body'].read().decode('utf-8'))
    print("Body :", body)

    return body["results"]["transcripts"][0]["transcript"]
