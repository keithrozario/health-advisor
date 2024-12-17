import boto3
import os
import json

from aws_lambda_powertools import Logger

Session = boto3.session.Session()
dynamodb = Session.resource('dynamodb')
logger = Logger()
table_name = os.getenv('TABLE_NAME', 'DynamoTable')
default_patient = 'Kapil'

@logger.inject_lambda_context(log_event=True)
def main(event, context):

    query_string_parameters = event.get('queryStringParameters', {})
    patient = query_string_parameters.get('patient', default_patient)
    return_body = find_bookings_for_patient(patient)

    return {"statusCode": 200, "body": json.dumps(return_body)}

def find_bookings_for_patient(patient: str)->list:
    """
    Args:
        patient: patient name
    returns:
        list of bookings for patient
    """
    table = dynamodb.Table(table_name)
    response = table.query(
        IndexName='PatientHistory',
        KeyConditionExpression='patient = :patient',
        ExpressionAttributeValues={
            ':patient': patient
        }
    )
    items = response['Items']
    for item in items:
        item['doctor'] = item.pop('pk')
        item['appt_datetime'] = item.pop('sk')

    return items