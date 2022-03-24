import boto3
import datetime
import os
from dotenv import load_dotenv
from config.Logging import saveLog
from botocore.exceptions import ClientError

load_dotenv()

class Connection:
    def __init__(self):
        saveLog('db.log', 'entrou init con')
        self.client = self.get_client()
        self.res = self.get_resource()
        self.create_tweets_table()

    def get_client(self):
        if os.environ.get('APP_ENV') == 'production':
            return boto3.client('dynamodb')
        else:
            return boto3.client('dynamodb', endpoint_url='http://localhost:8000')

    def get_resource(self):
        if os.environ.get('APP_ENV') == 'production':
            return boto3.resource('dynamodb')
        else:
            return boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    def create_tweets_table(self):
        table_name = 'Tweets'
        existing_tables = self.client.list_tables()['TableNames']

        if table_name not in existing_tables:
            response = self.client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S',
                    }
                ],
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH',
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1,
                },
                TableName=table_name,
            )

    def put_tweet(self, tweet_id, res=None):
        if not res:
            res = self.get_resource()

        table = res.Table('Tweets')
        current = datetime.datetime.now()
        response = table.put_item(
            Item={
                'id': tweet_id,
                'created_at': current.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )
        return response

    def get_tweet(self, tweet_id, res=None):
        if not res:
            res = self.get_resource()

        table = res.Table('Tweets')

        try:
            response = table.get_item(Key={'id': tweet_id})
        except ClientError as e:
            saveLog('db.log', e.response['Error']['Message'], 'error')
        else:
            return None if 'Item' not in response else response['Item']
