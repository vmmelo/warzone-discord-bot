import boto3
import datetime
from config.Logging import saveLog
from botocore.exceptions import ClientError


class Connection:
    def __init__(self):
        saveLog('connection', 'entrou init con')
        self.client = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
        self.res = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        self.create_tweets_table()

    def create_tweets_table(self):
        table_name = 'Tweets'
        existing_tables = self.client.list_tables()['TableNames']

        if table_name not in existing_tables:
            response = self.client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S',
                    },
                    {
                        'AttributeName': 'created_at',
                        'AttributeType': 'S',
                    },
                ],
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH',
                    },
                    {
                        'AttributeName': 'created_at',
                        'KeyType': 'RANGE',
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
            res = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

        table = res.Table('Tweets')
        response = table.put_item(
            Item={
                'id': tweet_id,
                'created_at': datetime.datetime.now(),
            }
        )
        return response

    def get_tweet(self, tweet_id, res=None):
        if not res:
            res = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

        table = res.Table('Tweets')

        try:
            response = table.get_item(Key={'id': tweet_id})
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']
