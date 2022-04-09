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
        self.create_loadouts_table()

    def get_client(self):
        if os.environ.get('APP_ENV') == 'production':
            return boto3.client('dynamodb',
                                region_name='us-east-2',
                                aws_access_key_id=os.environ.get('AWS_ACCESS_ID'),
                                aws_secret_access_key=os.environ.get('AWS_ACCESS_KEY')
                                )
        else:
            return boto3.client('dynamodb', endpoint_url='http://localhost:8000')

    def get_resource(self):
        if os.environ.get('APP_ENV') == 'production':
            return boto3.resource('dynamodb',
                                region_name='us-east-2',
                                aws_access_key_id=os.environ.get('AWS_ACCESS_ID'),
                                aws_secret_access_key= os.environ.get('AWS_ACCESS_KEY')
                                )
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
            saveLog('db.log', 'created tweets table')

    def create_loadouts_table(self):
        table_name = 'Loadouts'
        existing_tables = self.client.list_tables()['TableNames']

        if table_name not in existing_tables:
            response = self.client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'weapon',
                        'AttributeType': 'S',
                    },
                ],
                KeySchema=[
                    {
                        'AttributeName': 'weapon',
                        'KeyType': 'HASH',
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1,
                },
                TableName=table_name,
            )
            saveLog('db.log', 'created loadouts table')

    def save_tweet(self, tweet_id, content={}):
        table = self.res.Table('Tweets')
        current = datetime.datetime.now()
        response = table.put_item(
            Item={
                'id': tweet_id,
                'created_at': current.strftime('%Y-%m-%d %H:%M:%S'),
                'content': content
            }
        )
        return response

    def get_tweet(self, tweet_id):
        try:
            response = self.client.get_item(TableName='Tweets', Key={'id': tweet_id})
        except ClientError as e:
            saveLog('db.log', e.response['Error']['Message'], 'error')
        else:
            return None if 'Item' not in response else response['Item']


    def save_loadout(self, item):
        table = self.res.Table('Loadouts')
        response = table.put_item(Item=item)
        return response

    def get_loadout(self, alias):
        try:
            response = self.client.get_item(TableName='Loadouts', Key={'alias': alias})
        except ClientError as e:
            saveLog('db.log', e.response['Error']['Message'], 'error')
        else:
            return None if 'Item' not in response else response['Item']
