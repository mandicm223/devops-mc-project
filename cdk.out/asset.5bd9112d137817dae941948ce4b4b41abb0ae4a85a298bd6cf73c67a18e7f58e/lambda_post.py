from __future__ import print_function
from curses import raw
from email import message
from urllib import response

import boto3
import json

print('Loading function')

dynamodb = boto3.client('dynamodb')
dynamo = boto3.resource('dynamodb').Table("lambda_api_table")

def handler(event, context):
    '''Provide an event that contains the following keys:

      - operation: one of the operations in the operations dict below
      - tableName: required for operations that interact with DynamoDB
      - payload: a parameter to pass to the operation being performed
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    # print(event)

    if event['path'] == '/apiv1createPerson':
        body = json.loads(event["body"])
        responseBody = "POST method"
        
        operation = body["operation"]
        if 'tableName' in body:
            dynamodb.put_item(TableName=body["tableName"], Item={'id':{'S': body["payload"]["Item"]["id"]}})

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps(responseBody),
                "isBase64Encoded": False
            };

    elif event['path'] == '/apiv1getPerson':
        # if 'tableName' in body:
            
        responseBody = dynamodb.get_item(TableName="lambda_api_table", Key={'id':{'S': event["queryStringParameters"]["id"]}})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(responseBody),
            "isBase64Encoded": False
        };
        

    

    
        