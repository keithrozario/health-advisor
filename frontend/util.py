import boto3
Session_Local = boto3.session.Session(profile_name='nnatri+testenv-unicorngymrole', region_name="us-east-1")
bedrockClient = Session_Local.client('bedrock-agent-runtime')

sonnet_arn = "arn:aws:bedrock:us-east-1:205079877575:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
haiku_arn = 'arn:aws:bedrock:us-east-1:205079877575:inference-profile/us.anthropic.claude-3-5-haiku-20241022-v1:0'

def get_answers(questions):
    response  = bedrockClient.retrieve_and_generate(
        input={'text': questions},
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': 'ANO84FOE13',
                'modelArn': sonnet_arn
            },
            'type': 'KNOWLEDGE_BASE'
        })

    text = response['output']['text']
    source_doc = response['citations'][0]['retrievedReferences'][0]['location']['s3Location']
    return text, source_doc