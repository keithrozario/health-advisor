import boto3
import botocore

Session_Local = boto3.session.Session(profile_name='nnatri+testenv-unicorngymrole', region_name="us-east-1")
bedrock_agent_runtime_client = Session_Local.client('bedrock-agent-runtime')

agent_id = "WCORHJLNTQ"
agentAliasId = "ODRJYJEDVX"

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

def get_agent_response(question: str, session_id: str) -> str:
    
    agent_response = bedrock_agent_runtime_client.invoke_agent(
        inputText=question,
        agentId=agent_id,
        agentAliasId=agentAliasId,
        sessionId=session_id,
    )
    responses = []
    
    try:
        for event in agent_response['completion']:
            chunk = event.get('chunk')
            if chunk:
                responses.append(chunk.get("bytes").decode())
    except botocore.exceptions.EventStreamError as e:
        return "Throttling Error: Please stop asking me so many questions"

    return "\n".join(responses)