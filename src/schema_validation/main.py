#!/usr/bin/python3
from domain.model import EventModel
from domain.message import ResponseMessage
from domain.environment import Environments
from domain.exceptions import PutRecordError
from botocore.client import ClientError
from avro.io import validate
from avro.schema import parse
from utils import logger
import boto3
import json

logger = logger(__name__)
environments = Environments()
session = boto3.Session()

def parse_body(record: dict):
    record['body'] = json.loads(record['body'])
    event = {
        'event_id': record['body']['EventID'],
        'event_time': record['body']['EventTime'],
        'data_product': record['pathParameters']['datalake_name'],
        'schema_name': record['pathParameters']['schema_name'],
        'schema_version': record['pathParameters']['schema_version'],
        'event_data': json.loads(record['body']['EventData'])
    }
    return event

def put_record(name: str, record: str, partition_key: str, kns_client):
    try:
        name = name.replace('_', '-')
        response = kns_client.put_records(
            Records=[{
                'Data': record,
                'PartitionKey': partition_key
            }],
            StreamName=name)
        logger.info("Put record in stream %s.", name)
        return response
    except ClientError:
        logger.exception("Couldn't put record in stream %s.", name)
        raise PutRecordError(f"Couldn't put record in stream {name}.")

def get_schema_version(registry: str, schema: str, schema_version: int, region: str, glue=None) -> dict:
    if not glue:
        glue = session.client("glue", region_name=region)
    return glue.get_schema_version(SchemaId={'RegistryName': registry, 'SchemaName': schema},
                                            SchemaVersionNumber={'VersionNumber': schema_version})

def validate_avro(reponse, record) -> None:
    validate(parse(reponse), record, raise_on_error=True)

def get_schema_version_db(registry: str, schema: str, schema_version: int, region: str, dynamodb=None) -> dict:
    try:
        dynamodb = session.resource("dynamodb", region_name=region)
        logger.info('Searching for information on DynamoDB| %s', registry)
        table = dynamodb.Table(registry)
        response = table.get_item(Key={
            'Schema': schema,
            'VersionNumber': schema_version})
        if not "Item" in response:
            logger.warning('Item not found | %s', schema)
            response = get_schema_version(registry, schema, schema_version, region)
            put_item_db(registry, schema, schema_version, response["SchemaDefinition"], region,  dynamodb)
            return response
        return response['Item']
    except ClientError as err:
        logger.error(err)
        raise err

def put_item_db(registry: str, schema: str, schema_version: int, schema_definition: dict, region: str, dynamodb=None) -> None:
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(registry)
    table.put_item(
        Item={
            'Schema': schema,
            'VersionNumber': schema_version,
            'SchemaDefinition': schema_definition
        }
    )

def validate_schema_version(registry: str, schema: str, record: dict, schema_version, region: str) -> int:
    response = get_schema_version_db(registry, schema, int(schema_version), region)
    logger.info(f"Execute Validation Record v{schema_version}")
    validate_avro(response['SchemaDefinition'], record)
    return schema_version

def put_stream_transaction(stream_name: str, record: dict, region: str, kns=None) -> dict:
    if not kns:
        kns = session.client("kinesis", region_name=region)
    put_record(stream_name, json.dumps(record), "default", kns)

def main(event, context):
    try:

        message = parse_body(event)
        body = EventModel(**message)
        message['schema_version'] = validate_schema_version(
            body.data_product, body.schema_name, body.event_data, body.schema_version, environments.region)
        put_stream_transaction(
            f'{body.data_product}-{body.schema_name}-kinesis',  message, environments.region)
        
        return ResponseMessage.rep_200(
            message=f"Put record in stream {body.data_product}-{body.schema_name}-kinesis.",
            type='EventTransaction',
            category='DataSchema',
            id=body.event_id).format_report

    except Exception as err:
        print(err)
        return ResponseMessage.rep_400(
            message=str(err),
            type='EventTransactionError',
            category='DataSchema',
            id='ex00000001').format_report
