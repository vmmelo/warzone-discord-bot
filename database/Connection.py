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
        self.create_guild_settings_table()

    def get_client(self):
        if os.environ.get('APP_ENV') != 'development':
            return boto3.client('dynamodb',
                                region_name='us-east-2',
                                aws_access_key_id=os.environ.get('AWS_ACCESS_ID'),
                                aws_secret_access_key=os.environ.get('AWS_ACCESS_KEY')
                                )
        else:
            return boto3.client('dynamodb', endpoint_url='http://localhost:8000')

    def get_resource(self):
        if os.environ.get('APP_ENV') != 'development':
            return boto3.resource('dynamodb',
                                region_name='us-east-2',
                                aws_access_key_id=os.environ.get('AWS_ACCESS_ID'),
                                aws_secret_access_key= os.environ.get('AWS_ACCESS_KEY')
                                )
        else:
            return boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    def create_tweets_table(self):
        table_name = 'warzone_updates'
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

    def save_update(self, update_id, content={}):
        table = self.res.Table('warzone_updates')
        current = datetime.datetime.now()
        response = table.put_item(
            Item={
                'id': update_id,
                'created_at': current.strftime('%Y-%m-%d %H:%M:%S'),
                'content': content
            }
        )
        return response

    def get_update(self, update_id):
        try:
            response = self.client.get_item(TableName='warzone_updates', Key={'id': {'S': update_id}})
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
            response = self.client.get_item(TableName='Loadouts', Key={'alias': {'S': alias}})
        except ClientError as e:
            saveLog('db.log', e.response['Error']['Message'], 'error')
        else:
            return None if 'Item' not in response else response['Item']

    def get_guilds_settings(self):
        try:
            table = self.res.Table('guild_settings')
            response = table.scan()
        except ClientError as e:
            saveLog('db.log', e.response['Error']['Message'], 'error')
        else:
            if 'Items' not in response:
                return []
            result = {}
            for item in response['Items']:
                result[item['guild_id']] = item['settings']
            return result

    def save_guild_settings(self, guild_id, settings=None):
        if settings is None:
            settings = {}
        table = self.res.Table('guild_settings')
        response = table.put_item(
            Item={
                'guild_id': guild_id,
                'settings': settings
            }
        )
        return response

    def create_guild_settings_table(self):
        table_name = 'guild_settings'
        existing_tables = self.client.list_tables()['TableNames']

        if table_name not in existing_tables:
            response = self.client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'guild_id',
                        'AttributeType': 'N',
                    },
                ],
                KeySchema=[
                    {
                        'AttributeName': 'guild_id',
                        'KeyType': 'HASH',
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1,
                },
                TableName=table_name,
            )
            saveLog('db.log', 'created guild_settings table')
