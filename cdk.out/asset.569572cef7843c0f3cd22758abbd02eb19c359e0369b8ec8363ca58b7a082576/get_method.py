import boto3
import json
from aws_final_project.vardata import developers, project, position, s

dynamodbTableName=s.join(["interns",project])
dynamodb= boto3.resource('dynamodb')
dynamoTable=dynamodb.Table('project_table')

def lambda_handler(event, context):
    for n in developers:
        data=dynamoTable.get_item(
           Key={      
            'Name': developers[n]
        }
    )
               
    response = {
      'statusCode': 200,
      'body': json.dumps(data),
      'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
  }
  
    return response