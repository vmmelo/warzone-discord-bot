import boto3

## For a Boto3 client ('client' is for low-level access to Dynamo service API)
ddb1 = boto3.client('dynamodb', endpoint_url='http://localhost:8042')

dynamodb_client = boto3.client('dynamodb')


table_name = 'test'
existing_tables = dynamodb_client.list_tables()['TableNames']

if table_name not in existing_tables:
    response = dynamodb_client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'Artist',
                'AttributeType': 'S',
            },
            {
                'AttributeName': 'SongTitle',
                'AttributeType': 'S',
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'Artist',
                'KeyType': 'HASH',
            },
            {
                'AttributeName': 'SongTitle',
                'KeyType': 'RANGE',
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5,
        },
        TableName=table_name,
    )


response = ddb1.list_tables()
print(response)
