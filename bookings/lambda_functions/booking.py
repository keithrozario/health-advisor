import boto3
import botocore
import datetime
import pytz
import json
import os

from aws_lambda_powertools import Logger

Session = boto3.session.Session()
dynamodb = Session.resource('dynamodb')
logger = Logger()
table_name = os.getenv('TABLE_NAME', 'Calendars')

default_doctor='Dr.Keith'
default_patient='Kapil'

@logger.inject_lambda_context(log_event=True)
def main(event, context):

    event_body = json.loads(event.get('body', '{}'))
    doctor = event_body.get('doctor', default_doctor)
    patient = event_body.get('patient', default_patient)
    request_datetime = event_body.get('apptDateTime', get_next_slot_for_doctor(doctor))
    
    logger.info({'doctor':doctor, 'patient':patient, 'request_datetime':request_datetime})
    
    if request_datetime:
        return_body = insert_booking(doctor, request_datetime, patient)
    else:
        return_body = {"statusCode": 400, "body": f"No slots available for {doctor}"}

    return return_body


def get_next_slot_for_doctor(doctor: str):
    
    # Get current time in Singapore (lambda operating in us-west-2)
    SGT = pytz.timezone('Asia/Singapore') 
    now = datetime.datetime.now(SGT).replace(second=0, microsecond=0).isoformat()

    taken_slots = find_taken_slots_for_doctor(doctor=doctor, from_time=now)
    logger.debug({'taken_slots':taken_slots})

    next_slot = next_time_slot(now)
    for _ in range(16*3):
        logger.debug(next_slot)
        if next_slot not in taken_slots:
            break
        else:
            next_slot = next_time_slot(next_slot)    
    else:
        return None

    return next_slot

def find_taken_slots_for_doctor(doctor: str, from_time: str):
    """
    Args:
        doctor: doctor name
        from_time: datetime in isoformat
    returns:
        taken_slots: list of taken slots after now in isoformat
    """

    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression='pk = :pk AND sk > :sk',
        ExpressionAttributeValues={
            ':pk': doctor,
            ':sk': from_time
        }
    )
    taken_slots = [item['sk'] for item in response['Items']]
    
    return taken_slots

def next_time_slot(slot: str):
    """
    Args:
        slot: Datetime in isoformat
    returns:
        next_slot: next 30 minute slot in isoformat.
    """
    next_slot = datetime.datetime.fromisoformat(slot)
    if next_slot.minute < 30:
        next_slot = next_slot.replace(minute=30)
    elif next_slot.minute >= 30 and next_slot.minute < 60:
        next_slot = next_slot.replace(minute=0, hour=next_slot.hour + 1)
    
    if next_slot.hour < 8:
        next_slot = next_slot.replace(minute=0, hour=8)
    elif next_slot.hour >= 18:
        next_slot = next_slot.replace(minute=0, hour=8, day=next_slot.day + 1)
    
    # Note: isoformat will not print microsecods if it is 0.
    next_slot = next_slot.replace(second=0, microsecond=0)
    
    return next_slot.isoformat()


def insert_booking(doctor: str, request_datetime:str, patient_name: str) -> dict:
    # Insert the record only if it doesn't exists
    table = dynamodb.Table(table_name)
    item={
        'pk':doctor,
        'sk':request_datetime,
        'patient': patient_name,
        'createdOn': datetime.datetime.now().isoformat(),
    }
    try:
        table.put_item(
            Item=item,
            ConditionExpression='attribute_not_exists(pk) AND attribute_not_exists(sk)'
        )
    except botocore.exceptions.ClientError as e:
        
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {"statusCode": 400, "body": "Booking Unsuccessful"}
        else:
            return {"statusCode": 500, "body": "Unknown Error"}
    
    item['doctor'] = item.pop('pk')
    item['appt_datetime'] = item.pop('sk')
    return {"statusCode": 200, "body": json.dumps(item)}
 
# Test
if __name__ == "__main__":
    Session_Local = boto3.session.Session(profile_name='nnatri+testenv-unicorngymrole', region_name="us-east-1")
    dynamodb = Session_Local.resource('dynamodb')
    doctor = 'Dr.Keith'
    patient = 'Kapil'

    # for _ in range(4):
    #     request_datetime = get_next_slot_for_doctor(doctor)
    #     if request_datetime:
    #         return_body = insert_booking(doctor, request_datetime, patient_name=patient)
    #         print(return_body)
    #     else:
    #         print("No more slots")